from pathlib import Path
from typing import Any
import yaml

from agentshield.parsers.cloudformation import extract_cloudformation_resources, parse_cloudformation_file
from agentshield.parsers.helm import extract_helm_resources, parse_helm_chart_dir, parse_helm_values
from agentshield.parsers.kubernetes import extract_kubernetes_resources, parse_kubernetes_file
from agentshield.parsers.normalizer import normalize_terraform_resources
from agentshield.parsers.terraform import extract_terraform_resources, parse_terraform_file


def autodetect_template_format(file_or_dir_path: str) -> str:
    """
    Auto-detect whether a path is Terraform (.tf), CloudFormation, Kubernetes, or Helm.
    Returns: 'terraform', 'cloudformation', 'kubernetes', 'helm', or 'unknown'
    """
    path = Path(file_or_dir_path)

    if path.is_dir():
        if (path / "Chart.yaml").exists() or (path / "values.yaml").exists():
            return "helm"
        return "unknown"

    if not path.exists():
        raise FileNotFoundError(f"Target path not found: {file_or_dir_path}")

    suffix = path.suffix.lower()

    if suffix == ".tf":
        return "terraform"

    if suffix in {".yaml", ".yml", ".json"}:
        content = path.read_text(encoding="utf-8")

        # Check CloudFormation signatures
        if "AWSTemplateFormatVersion" in content or "Resources" in content:
            return "cloudformation"

        # Check Kubernetes signatures
        if "apiVersion" in content and "kind" in content:
            return "kubernetes"

        # Check Helm values file
        if "values" in path.name.lower():
            return "helm"

        # Try parsing YAML mapping for k8s or cfn
        try:
            doc = yaml.safe_load(content)
            if isinstance(doc, dict):
                if "apiVersion" in doc and "kind" in doc:
                    return "kubernetes"
                if "Resources" in doc:
                    return "cloudformation"
        except Exception:
            pass

    return "unknown"


def parse_iac_template(file_or_dir_path: str, template_format: str | None = None) -> list[dict[str, Any]]:
    """
    Unified entry point for parsing any multi-cloud IaC file or Helm chart.
    """
    if not template_format or template_format == "unknown":
        template_format = autodetect_template_format(file_or_dir_path)

    if template_format == "terraform":
        parsed = parse_terraform_file(file_or_dir_path)
        extracted = extract_terraform_resources(parsed)
        return normalize_terraform_resources(extracted)

    elif template_format == "cloudformation":
        parsed = parse_cloudformation_file(file_or_dir_path)
        return extract_cloudformation_resources(parsed)

    elif template_format == "kubernetes":
        docs = parse_kubernetes_file(file_or_dir_path)
        return extract_kubernetes_resources(docs)

    elif template_format == "helm":
        path = Path(file_or_dir_path)
        if path.is_dir():
            helm_data = parse_helm_chart_dir(file_or_dir_path)
            return extract_helm_resources(helm_data)
        else:
            values = parse_helm_values(file_or_dir_path)
            return extract_helm_resources({"values": values, "chart_metadata": {"name": path.stem}})

    else:
        raise ValueError(f"Unsupported or undetected IaC template format for: {file_or_dir_path}")
