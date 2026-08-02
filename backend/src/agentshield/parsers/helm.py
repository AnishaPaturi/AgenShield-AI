from pathlib import Path
from typing import Any
import yaml

from agentshield.parsers.kubernetes import extract_kubernetes_resources, parse_kubernetes_file


def parse_helm_values(file_path: str) -> dict[str, Any]:
    """
    Parse a Helm values file (values.yaml) into a dictionary.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Helm values file not found: {file_path}")

    content = path.read_text(encoding="utf-8")
    try:
        data = yaml.safe_load(content)
        return data if isinstance(data, dict) else {}
    except Exception as e:
        raise ValueError(f"Failed to parse Helm values.yaml file: {e}") from e


def parse_helm_chart_dir(chart_dir: str) -> dict[str, Any]:
    """
    Parse a Helm Chart directory containing Chart.yaml, values.yaml, and templates/.
    """
    chart_path = Path(chart_dir)
    if not chart_path.is_dir():
        raise NotADirectoryError(f"Helm chart directory not found: {chart_dir}")

    chart_yaml_path = chart_path / "Chart.yaml"
    values_yaml_path = chart_path / "values.yaml"
    templates_dir = chart_path / "templates"

    chart_metadata = {}
    if chart_yaml_path.exists():
        try:
            chart_metadata = yaml.safe_load(chart_yaml_path.read_text(encoding="utf-8")) or {}
        except Exception:
            pass

    values = {}
    if values_yaml_path.exists():
        values = parse_helm_values(str(values_yaml_path))

    template_files = []
    if templates_dir.exists() and templates_dir.is_dir():
        for t_file in templates_dir.glob("**/*.yaml"):
            template_files.append(str(t_file))
        for t_file in templates_dir.glob("**/*.yml"):
            template_files.append(str(t_file))

    return {
        "chart_metadata": chart_metadata,
        "values": values,
        "template_files": template_files,
        "chart_dir": str(chart_path),
    }


def extract_helm_resources(helm_data: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Extract resources from parsed Helm chart values and template files.
    """
    resources = []
    chart_name = helm_data.get("chart_metadata", {}).get("name", "helm-chart")

    # Treat values.yaml as a configuration resource
    values = helm_data.get("values", {})
    if values:
        resources.append({
            "resource_id": f"helm.{chart_name}.values",
            "resource_type": "helm/values",
            "resource_name": f"{chart_name}-values",
            "properties": values,
            "chart_name": chart_name,
            "start_line": None,
            "end_line": None,
        })

    # Parse any static or rendered template files
    for t_file in helm_data.get("template_files", []):
        try:
            docs = parse_kubernetes_file(t_file)
            k8s_res = extract_kubernetes_resources(docs)
            for r in k8s_res:
                r["helm_chart"] = chart_name
                r["template_source"] = str(t_file)
                resources.append(r)
        except Exception:
            pass

    return resources
