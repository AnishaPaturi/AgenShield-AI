"""Static Linter Adapters for AgentShield AI Code & Sandbox Validator Agent.

Provides static verification adapters for:
1. terraform validate (Terraform syntax and configuration integrity)
2. tflint (Terraform best practices and lint rules)
3. cfn-lint (AWS CloudFormation specification and schema validation)
4. kube-linter (Kubernetes manifest security and best-practice checks)
5. helm lint (Helm chart and template validation)

Each linter executes via system CLI if installed, or falls back to an
accurate native AST/schema validator when offline or CLI is unavailable.
"""

from __future__ import annotations

import json
import logging
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

import hcl2
import yaml

from agentshield.core.schemas import IaCType, ValidationCheckResult

logger = logging.getLogger("agentshield.validation.linters")


class BaseLinter:
    """Base class for static IaC verification tools."""

    name: str = "base_linter"
    cli_binary: str = ""

    def __init__(self) -> None:
        self._mock_result: ValidationCheckResult | None = None

    def set_mock_result(self, result: ValidationCheckResult | None) -> None:
        """Set a mock check result for testing purposes."""
        self._mock_result = result

    def is_available(self) -> bool:
        """Check if the external CLI binary is installed on the host."""
        if not self.cli_binary:
            return False
        return shutil.which(self.cli_binary) is not None

    def validate(self, content: str, file_path: str = "template.iac") -> ValidationCheckResult:
        """Execute validation check on given content string."""
        if self._mock_result is not None:
            return self._mock_result

        if self.is_available():
            try:
                return self._run_cli(content, file_path)
            except Exception as exc:
                logger.warning(
                    "%s CLI execution failed (%s); falling back to native validator",
                    self.name,
                    exc,
                )
                return self._run_native(content, file_path)
        else:
            return self._run_native(content, file_path)

    def _run_cli(self, content: str, file_path: str) -> ValidationCheckResult:
        """Run external CLI tool."""
        raise NotImplementedError

    def _run_native(self, content: str, file_path: str) -> ValidationCheckResult:
        """Run native Python fallback validator."""
        raise NotImplementedError


class TerraformValidateLinter(BaseLinter):
    """Linter adapter for 'terraform validate'."""

    name: str = "terraform_validate"
    cli_binary: str = "terraform"

    def _run_cli(self, content: str, file_path: str) -> ValidationCheckResult:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tf_file = Path(tmp_dir) / "main.tf"
            tf_file.write_text(content, encoding="utf-8")

            # terraform validate requires initialized backend/providers; try init -backend=false
            subprocess.run(
                [self.cli_binary, "init", "-backend=false"],
                cwd=tmp_dir,
                capture_output=True,
                text=True,
                timeout=15,
                check=False,
            )

            res = subprocess.run(
                [self.cli_binary, "validate", "-json"],
                cwd=tmp_dir,
                capture_output=True,
                text=True,
                timeout=15,
                check=False,
            )

            try:
                payload = json.loads(res.stdout) if res.stdout else {}
                valid = payload.get("valid", res.returncode == 0)
                error_count = payload.get("error_count", 0)
                diagnostics = payload.get("diagnostics", [])
                error_msgs = [d.get("summary", "") for d in diagnostics if d.get("severity") == "error"]

                if valid and error_count == 0:
                    return ValidationCheckResult(
                        check_name=self.name,
                        passed=True,
                        output="Success! The configuration is valid.",
                    )
                return ValidationCheckResult(
                    check_name=self.name,
                    passed=False,
                    output=res.stdout,
                    error="; ".join(error_msgs) or res.stderr or "Terraform validation failed.",
                )
            except Exception:
                passed = res.returncode == 0
                return ValidationCheckResult(
                    check_name=self.name,
                    passed=passed,
                    output=res.stdout,
                    error=None if passed else (res.stderr or "Terraform validation failed"),
                )

    def _run_native(self, content: str, file_path: str) -> ValidationCheckResult:
        """Validate Terraform HCL syntax natively via python-hcl2 and brace checks."""
        # 1. Bracket / brace balance check
        open_braces = content.count("{")
        close_braces = content.count("}")
        if open_braces != close_braces:
            return ValidationCheckResult(
                check_name=self.name,
                passed=False,
                error=f"Unbalanced braces in Terraform HCL: {open_braces} open '{{' vs {close_braces} close '}}'",
            )

        # 2. python-hcl2 parsing check
        try:
            parsed = hcl2.loads(content)
            if not isinstance(parsed, dict):
                return ValidationCheckResult(
                    check_name=self.name,
                    passed=False,
                    error="Terraform HCL parsed into invalid non-dictionary structure.",
                )
        except Exception as exc:
            return ValidationCheckResult(
                check_name=self.name,
                passed=False,
                error=f"HCL2 syntax error: {exc}",
            )

        # 3. Structural checks for standard blocks
        valid_block_types = {
            "resource",
            "data",
            "variable",
            "output",
            "provider",
            "terraform",
            "locals",
            "module",
        }
        for key in parsed.keys():
            if key not in valid_block_types:
                # Top-level statements in TF must be recognized blocks
                return ValidationCheckResult(
                    check_name=self.name,
                    passed=False,
                    error=f"Invalid top-level Terraform block or unrecognized token: '{key}'",
                )

        return ValidationCheckResult(
            check_name=self.name,
            passed=True,
            output="Success! Terraform HCL syntax and block structures are valid.",
        )


class TflintLinter(BaseLinter):
    """Linter adapter for 'tflint'."""

    name: str = "tflint"
    cli_binary: str = "tflint"

    def _run_cli(self, content: str, file_path: str) -> ValidationCheckResult:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tf_file = Path(tmp_dir) / "main.tf"
            tf_file.write_text(content, encoding="utf-8")

            res = subprocess.run(
                [self.cli_binary, "--format", "json"],
                cwd=tmp_dir,
                capture_output=True,
                text=True,
                timeout=15,
                check=False,
            )

            try:
                data = json.loads(res.stdout) if res.stdout else {}
                issues = data.get("issues", [])
                errors = [i for i in issues if i.get("rule", {}).get("severity") == "ERROR"]
                if not errors and res.returncode == 0:
                    return ValidationCheckResult(
                        check_name=self.name,
                        passed=True,
                        output="TFLint check passed with no errors.",
                    )
                err_msg = "; ".join(f"{i.get('message')} ({i.get('rule', {}).get('name')})" for i in errors)
                return ValidationCheckResult(
                    check_name=self.name,
                    passed=False,
                    output=res.stdout,
                    error=err_msg or res.stderr or "TFLint violations detected.",
                )
            except Exception:
                passed = res.returncode == 0
                return ValidationCheckResult(
                    check_name=self.name,
                    passed=passed,
                    output=res.stdout,
                    error=None if passed else (res.stderr or "TFLint execution failed"),
                )

    def _run_native(self, content: str, file_path: str) -> ValidationCheckResult:
        """Validate Terraform best practices natively (naming, deprecated syntax, duplicate resources)."""
        # 1. Check for deprecated interpolation syntax e.g. foo = "${bar}"
        deprecated_interpolation_pattern = re.compile(r'=\s*"\$\{([a-zA-Z0-9_.]+)\}"')
        dep_matches = deprecated_interpolation_pattern.findall(content)
        if dep_matches:
            return ValidationCheckResult(
                check_name=self.name,
                passed=False,
                error=f"TFLint policy violation: Deprecated interpolation syntax detected for '${{{dep_matches[0]}}}'. Use direct reference without quotes.",
            )

        # 2. Check for resource naming conventions & duplicate resources
        resource_pattern = re.compile(r'resource\s+"([^"]+)"\s+"([^"]+)"')
        seen_resources: set[tuple[str, str]] = set()
        for match in resource_pattern.finditer(content):
            res_type, res_name = match.group(1), match.group(2)
            # Naming convention: lowercase alphanumeric + underscore
            if not re.match(r"^[a-z0-9_]+$", res_name):
                return ValidationCheckResult(
                    check_name=self.name,
                    passed=False,
                    error=f"TFLint naming violation: Resource name '{res_name}' must use only lowercase alphanumeric characters and underscores.",
                )
            res_key = (res_type, res_name)
            if res_key in seen_resources:
                return ValidationCheckResult(
                    check_name=self.name,
                    passed=False,
                    error=f"TFLint duplicate violation: Duplicate resource definition '{res_type}.{res_name}'.",
                )
            seen_resources.add(res_key)

        return ValidationCheckResult(
            check_name=self.name,
            passed=True,
            output="TFLint static rules passed with zero violations.",
        )


class CfnLintLinter(BaseLinter):
    """Linter adapter for 'cfn-lint' (AWS CloudFormation)."""

    name: str = "cfn_lint"
    cli_binary: str = "cfn-lint"

    def _run_cli(self, content: str, file_path: str) -> ValidationCheckResult:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False, encoding="utf-8"
        ) as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        try:
            res = subprocess.run(
                [self.cli_binary, "-f", "json", tmp_path],
                capture_output=True,
                text=True,
                timeout=15,
                check=False,
            )
            try:
                issues = json.loads(res.stdout) if res.stdout else []
                errors = [i for i in issues if i.get("Level") == "Error"]
                if not errors and res.returncode == 0:
                    return ValidationCheckResult(
                        check_name=self.name,
                        passed=True,
                        output="CloudFormation template validation passed.",
                    )
                err_msg = "; ".join(f"{i.get('Message')} ({i.get('Rule', {}).get('Id')})" for i in errors)
                return ValidationCheckResult(
                    check_name=self.name,
                    passed=False,
                    output=res.stdout,
                    error=err_msg or res.stderr or "cfn-lint errors detected.",
                )
            except Exception:
                passed = res.returncode == 0
                return ValidationCheckResult(
                    check_name=self.name,
                    passed=passed,
                    output=res.stdout,
                    error=None if passed else (res.stderr or "cfn-lint check failed"),
                )
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def _run_native(self, content: str, file_path: str) -> ValidationCheckResult:
        """Validate CloudFormation syntax and specification structure natively."""
        # 1. Parse YAML or JSON
        try:
            data = yaml.safe_load(content)
        except Exception as exc:
            return ValidationCheckResult(
                check_name=self.name,
                passed=False,
                error=f"CloudFormation syntax error: Failed to parse YAML/JSON: {exc}",
            )

        if not isinstance(data, dict):
            return ValidationCheckResult(
                check_name=self.name,
                passed=False,
                error="CloudFormation template must be a top-level JSON or YAML mapping object.",
            )

        # 2. Check CloudFormation allowed top-level keys
        valid_cfn_keys = {
            "AWSTemplateFormatVersion",
            "Description",
            "Metadata",
            "Parameters",
            "Mappings",
            "Conditions",
            "Transform",
            "Resources",
            "Outputs",
            "Rules",
            "Hooks",
        }
        for k in data.keys():
            if k not in valid_cfn_keys:
                return ValidationCheckResult(
                    check_name=self.name,
                    passed=False,
                    error=f"cfn-lint schema error: Unrecognized top-level CloudFormation key '{k}'.",
                )

        # 3. Check Resources block
        resources = data.get("Resources")
        if resources is None and "AWSTemplateFormatVersion" not in data:
            return ValidationCheckResult(
                check_name=self.name,
                passed=False,
                error="cfn-lint error: CloudFormation template must contain a 'Resources' section.",
            )

        if resources is not None:
            if not isinstance(resources, dict) or len(resources) == 0:
                return ValidationCheckResult(
                    check_name=self.name,
                    passed=False,
                    error="cfn-lint error: 'Resources' must be a non-empty mapping of resource logical IDs.",
                )

            for res_id, res_body in resources.items():
                if not isinstance(res_body, dict):
                    return ValidationCheckResult(
                        check_name=self.name,
                        passed=False,
                        error=f"cfn-lint error: Resource '{res_id}' definition must be a mapping.",
                    )
                res_type = res_body.get("Type")
                if not res_type or not isinstance(res_type, str):
                    return ValidationCheckResult(
                        check_name=self.name,
                        passed=False,
                        error=f"cfn-lint error: Resource '{res_id}' is missing required 'Type' field.",
                    )
                if "Properties" in res_body and not isinstance(res_body["Properties"], dict):
                    return ValidationCheckResult(
                        check_name=self.name,
                        passed=False,
                        error=f"cfn-lint error: 'Properties' for resource '{res_id}' must be a mapping.",
                    )

        return ValidationCheckResult(
            check_name=self.name,
            passed=True,
            output="Success! CloudFormation template structure and resources are valid.",
        )


class KubeLinter(BaseLinter):
    """Linter adapter for 'kube-linter'."""

    name: str = "kube_linter"
    cli_binary: str = "kube-linter"

    def _run_cli(self, content: str, file_path: str) -> ValidationCheckResult:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False, encoding="utf-8"
        ) as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        try:
            res = subprocess.run(
                [self.cli_binary, "lint", "--format", "json", tmp_path],
                capture_output=True,
                text=True,
                timeout=15,
                check=False,
            )
            try:
                data = json.loads(res.stdout) if res.stdout else {}
                checks = data.get("Reports", [])
                if not checks and res.returncode == 0:
                    return ValidationCheckResult(
                        check_name=self.name,
                        passed=True,
                        output="kube-linter passed: No security or syntax violations found.",
                    )
                errors = [c.get("Diagnostic", {}).get("Message") for c in checks]
                return ValidationCheckResult(
                    check_name=self.name,
                    passed=False,
                    output=res.stdout,
                    error="; ".join(filter(None, errors)) or res.stderr or "kube-linter checks failed.",
                )
            except Exception:
                passed = res.returncode == 0
                return ValidationCheckResult(
                    check_name=self.name,
                    passed=passed,
                    output=res.stdout,
                    error=None if passed else (res.stderr or "kube-linter execution failed"),
                )
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def _run_native(self, content: str, file_path: str) -> ValidationCheckResult:
        """Validate Kubernetes YAML manifests and standard kube-linter rules natively."""
        # 1. Parse multi-document YAML
        try:
            docs = list(yaml.safe_load_all(content))
        except Exception as exc:
            return ValidationCheckResult(
                check_name=self.name,
                passed=False,
                error=f"Kubernetes manifest YAML syntax error: {exc}",
            )

        non_empty_docs = [d for d in docs if d is not None]
        if not non_empty_docs:
            return ValidationCheckResult(
                check_name=self.name,
                passed=False,
                error="Kubernetes manifest contains no valid YAML documents.",
            )

        # 2. Check each Kubernetes manifest
        for idx, doc in enumerate(non_empty_docs):
            if not isinstance(doc, dict):
                return ValidationCheckResult(
                    check_name=self.name,
                    passed=False,
                    error=f"Document #{idx + 1} must be a Kubernetes resource object mapping.",
                )

            for req in ("apiVersion", "kind", "metadata"):
                if req not in doc:
                    return ValidationCheckResult(
                        check_name=self.name,
                        passed=False,
                        error=f"Document #{idx + 1} is missing mandatory Kubernetes field '{req}'.",
                    )

            metadata = doc.get("metadata", {})
            if not isinstance(metadata, dict) or not metadata.get("name"):
                return ValidationCheckResult(
                    check_name=self.name,
                    passed=False,
                    error=f"Resource of kind '{doc.get('kind')}' is missing 'metadata.name'.",
                )

            # Security linting rules: inspect containers for privileged mode or latest tag
            spec = doc.get("spec", {})
            pod_spec = spec
            if "template" in spec and isinstance(spec["template"], dict):
                pod_spec = spec["template"].get("spec", {})

            if isinstance(pod_spec, dict):
                containers = pod_spec.get("containers", [])
                if isinstance(containers, list):
                    for c in containers:
                        if not isinstance(c, dict):
                            continue
                        c_name = c.get("name", "unnamed")
                        img = str(c.get("image", ""))
                        if img and (img.endswith(":latest") or ":" not in img):
                            return ValidationCheckResult(
                                check_name=self.name,
                                passed=False,
                                error=f"kube-linter violation (no-latest-image-tag): Container '{c_name}' uses latest or untagged image '{img}'.",
                            )

                        sec_ctx = c.get("securityContext", {})
                        if isinstance(sec_ctx, dict) and sec_ctx.get("privileged") is True:
                            return ValidationCheckResult(
                                check_name=self.name,
                                passed=False,
                                error=f"kube-linter violation (privileged-container): Container '{c_name}' has privileged: true.",
                            )

        return ValidationCheckResult(
            check_name=self.name,
            passed=True,
            output="Success! Kubernetes manifests passed syntax and security lint checks.",
        )


class HelmLintLinter(BaseLinter):
    """Linter adapter for 'helm lint'."""

    name: str = "helm_lint"
    cli_binary: str = "helm"

    def _run_cli(self, content: str, file_path: str) -> ValidationCheckResult:
        with tempfile.TemporaryDirectory() as tmp_dir:
            chart_dir = Path(tmp_dir) / "chart"
            chart_dir.mkdir()
            (chart_dir / "Chart.yaml").write_text(
                "apiVersion: v2\nname: test-chart\nversion: 0.1.0\n", encoding="utf-8"
            )
            templates_dir = chart_dir / "templates"
            templates_dir.mkdir()
            (templates_dir / Path(file_path).name).write_text(content, encoding="utf-8")

            res = subprocess.run(
                [self.cli_binary, "lint", str(chart_dir)],
                capture_output=True,
                text=True,
                timeout=15,
                check=False,
            )

            passed = res.returncode == 0 and "ERROR" not in res.stdout
            return ValidationCheckResult(
                check_name=self.name,
                passed=passed,
                output=res.stdout,
                error=None if passed else (res.stderr or res.stdout or "Helm lint failed."),
            )

    def _run_native(self, content: str, file_path: str) -> ValidationCheckResult:
        """Validate Helm template/values syntax natively."""
        # 1. Check YAML syntax
        try:
            # Handle Helm Go-template directives by temporarily substituting them if needed
            cleaned = re.sub(r"\{\{.*?\}\}", "helm_placeholder", content)
            yaml.safe_load(cleaned)
        except Exception as exc:
            return ValidationCheckResult(
                check_name=self.name,
                passed=False,
                error=f"Helm lint error: Failed to parse YAML structure: {exc}",
            )

        # 2. Check Chart.yaml metadata if target is Chart.yaml
        if "Chart.yaml" in file_path or "chart.yaml" in file_path:
            try:
                meta = yaml.safe_load(content)
                if not isinstance(meta, dict):
                    return ValidationCheckResult(
                        check_name=self.name,
                        passed=False,
                        error="Chart.yaml must be a mapping.",
                    )
                for req in ("apiVersion", "name", "version"):
                    if req not in meta:
                        return ValidationCheckResult(
                            check_name=self.name,
                            passed=False,
                            error=f"Chart.yaml missing required field '{req}'.",
                        )
            except Exception as exc:
                return ValidationCheckResult(
                    check_name=self.name,
                    passed=False,
                    error=f"Chart.yaml syntax error: {exc}",
                )

        return ValidationCheckResult(
            check_name=self.name,
            passed=True,
            output="Success! Helm templates and values passed lint checks.",
        )


def get_linters_for_iac_type(iac_type: IaCType | str) -> list[BaseLinter]:
    """Return the static linters corresponding to a given IaC platform type."""
    iac_str = iac_type.value if isinstance(iac_type, IaCType) else str(iac_type).lower()

    if iac_str == "terraform":
        return [TerraformValidateLinter(), TflintLinter()]
    elif iac_str == "cloudformation":
        return [CfnLintLinter()]
    elif iac_str == "kubernetes":
        return [KubeLinter()]
    elif iac_str == "helm":
        return [HelmLintLinter()]
    else:
        # Default fallback to terraform validate
        return [TerraformValidateLinter()]
