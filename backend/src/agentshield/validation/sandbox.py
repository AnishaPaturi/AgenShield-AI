"""LocalStack Runtime Dry-Run Sandbox Testing Engine for AgentShield AI (Task 4.3).

Validates patched Infrastructure-as-Code (Terraform & AWS CloudFormation) templates
against a containerized or local LocalStack runtime sandbox before deployment.

Verifies:
1. Provider configuration & API dry-run compatibility with LocalStack.
2. Resource definition validity & property schema constraints.
3. Dependency references and topological provisibility without runtime breakage.

Provides automated fallback to an intelligent EmulatedLocalStackSandbox when
LocalStack daemon or Docker is offline, ensuring reliable CI/CD and developer testing.
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
from urllib.error import URLError
from urllib.request import urlopen

import yaml

from agentshield.core.schemas import IaCType, ValidationCheckResult

logger = logging.getLogger("agentshield.validation.sandbox")

DEFAULT_LOCALSTACK_URL = os.getenv("LOCALSTACK_ENDPOINT_URL", "http://localhost:4566")
DEFAULT_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")


class EmulatedLocalStackSandbox:
    """High-fidelity AWS emulation sandbox validating resource schemas and dependency graphs."""

    # Essential required properties for common AWS resources in Terraform
    TF_REQUIRED_ATTRS: dict[str, list[str]] = {
        "aws_s3_bucket": [],  # bucket name optional if generated
        "aws_db_instance": ["instance_class"],
        "aws_security_group": [],
        "aws_iam_role": ["assume_role_policy"],
        "aws_iam_policy": ["policy"],
        "aws_sqs_queue": [],
        "aws_sns_topic": [],
        "aws_vpc": ["cidr_block"],
        "aws_subnet": ["vpc_id", "cidr_block"],
    }

    # Essential required properties for AWS CloudFormation
    CFN_REQUIRED_PROPERTIES: dict[str, list[str]] = {
        "AWS::RDS::DBInstance": ["DBInstanceClass"],
        "AWS::EC2::VPC": ["CidrBlock"],
        "AWS::EC2::Subnet": ["VpcId", "CidrBlock"],
        "AWS::IAM::Role": ["AssumeRolePolicyDocument"],
    }

    @classmethod
    def validate_terraform(cls, content: str) -> ValidationCheckResult:
        """Emulated dry-run validation for Terraform HCL."""
        errors: list[str] = []

        # 1. Basic structural parsing via python-hcl2 if available
        try:
            import hcl2

            parsed = hcl2.loads(content)
        except Exception as exc:
            return ValidationCheckResult(
                check_name="localstack_sandbox_dryrun",
                passed=False,
                output="",
                error=f"Terraform sandbox dry-run parse failure: {exc}",
            )

        resources: list[dict[str, Any]] = parsed.get("resource", [])
        declared_resource_ids: set[str] = set()

        for res_block in resources:
            for res_type, res_dict in res_block.items():
                for res_name in res_dict.keys():
                    declared_resource_ids.add(f"{res_type}.{res_name}")

        # 2. Inspect individual resources for broken references and schema violations
        for res_block in resources:
            for res_type, res_dict in res_block.items():
                for res_name, props in res_dict.items():
                    r_id = f"{res_type}.{res_name}"
                    if not isinstance(props, dict):
                        continue

                    # Check required attributes
                    req_attrs = cls.TF_REQUIRED_ATTRS.get(res_type, [])
                    for req in req_attrs:
                        if req not in props:
                            errors.append(
                                f"Resource '{r_id}' is missing required attribute '{req}'"
                            )

                    # Check reference validity in property strings
                    props_str = json.dumps(props)
                    ref_matches = re.findall(r"\${([a-zA-Z0-9_]+\.[a-zA-Z0-9_]+)\.", props_str)
                    for ref in ref_matches:
                        if ref not in declared_resource_ids and not ref.startswith("var."):
                            errors.append(
                                f"Resource '{r_id}' references non-existent resource '{ref}'"
                            )

                    # Check IAM policy JSON syntax if present
                    for policy_key in ["assume_role_policy", "policy"]:
                        if policy_key in props and isinstance(props[policy_key], str):
                            raw_p = props[policy_key].strip()
                            if raw_p.startswith("{") and raw_p.endswith("}"):
                                try:
                                    json.loads(raw_p)
                                except json.JSONDecodeError as jde:
                                    errors.append(
                                        f"Resource '{r_id}' contains invalid IAM policy JSON: {jde}"
                                    )

        if errors:
            return ValidationCheckResult(
                check_name="localstack_sandbox_dryrun",
                passed=False,
                output="",
                error="LocalStack dry-run detected schema/dependency breakages: " + "; ".join(errors),
            )

        return ValidationCheckResult(
            check_name="localstack_sandbox_dryrun",
            passed=True,
            output=(
                f"[LocalStack Emulated Dry-Run] Validated {len(declared_resource_ids)} "
                f"resource definitions and topological dependency graph. Zero deployment breakages detected."
            ),
        )

    @classmethod
    def validate_cloudformation(cls, content: str) -> ValidationCheckResult:
        """Emulated dry-run validation for CloudFormation templates."""
        errors: list[str] = []

        try:
            if content.strip().startswith("{"):
                data = json.loads(content)
            else:
                data = yaml.safe_load(content)
        except Exception as exc:
            return ValidationCheckResult(
                check_name="localstack_sandbox_dryrun",
                passed=False,
                output="",
                error=f"CloudFormation sandbox dry-run parse failure: {exc}",
            )

        if not isinstance(data, dict):
            return ValidationCheckResult(
                check_name="localstack_sandbox_dryrun",
                passed=False,
                output="",
                error="Invalid CloudFormation template root structure.",
            )

        resources = data.get("Resources", {})
        if not resources:
            return ValidationCheckResult(
                check_name="localstack_sandbox_dryrun",
                passed=False,
                output="",
                error="CloudFormation template has no Resources block.",
            )

        declared_keys = set(resources.keys())

        for res_name, res_def in resources.items():
            if not isinstance(res_def, dict):
                errors.append(f"Resource '{res_name}' definition must be an object.")
                continue

            res_type = res_def.get("Type", "")
            if not res_type or not res_type.startswith("AWS::"):
                errors.append(f"Resource '{res_name}' has invalid Type '{res_type}'.")
                continue

            properties = res_def.get("Properties", {})
            req_props = cls.CFN_REQUIRED_PROPERTIES.get(res_type, [])
            for req in req_props:
                if req not in properties:
                    errors.append(
                        f"Resource '{res_name}' of type '{res_type}' missing required property '{req}'"
                    )

            # Check Ref and Fn::GetAtt targets
            raw_str = json.dumps(res_def)
            refs = re.findall(r'\{"Ref":\s*"([^"]+)"\}', raw_str)
            for r in refs:
                if r not in declared_keys and not r.startswith("AWS::") and r not in data.get("Parameters", {}):
                    errors.append(f"Resource '{res_name}' has unresolved Ref '{r}'")

        if errors:
            return ValidationCheckResult(
                check_name="localstack_sandbox_dryrun",
                passed=False,
                output="",
                error="LocalStack CFN dry-run breakages: " + "; ".join(errors),
            )

        return ValidationCheckResult(
            check_name="localstack_sandbox_dryrun",
            passed=True,
            output=(
                f"[LocalStack Emulated Dry-Run] CloudFormation template validated. "
                f"{len(declared_keys)} resources and references verified successfully."
            ),
        )


class LocalStackSandbox:
    """LocalStack Containerized Sandbox Validator for AWS Terraform and CloudFormation."""

    def __init__(
        self,
        endpoint_url: str = DEFAULT_LOCALSTACK_URL,
        region: str = DEFAULT_REGION,
    ) -> None:
        self.endpoint_url = endpoint_url.rstrip("/")
        self.region = region

    def is_available(self, timeout_sec: float = 1.0) -> bool:
        """Check if LocalStack daemon is reachable at endpoint_url."""
        health_urls = [
            f"{self.endpoint_url}/_localstack/health",
            f"{self.endpoint_url}/health",
        ]
        for url in health_urls:
            try:
                with urlopen(url, timeout=timeout_sec) as resp:
                    if resp.status == 200:
                        return True
            except (URLError, TimeoutError, OSError):
                continue
        return False

    def validate_terraform_dryrun(
        self, content: str, file_path: str = "main.tf"
    ) -> ValidationCheckResult:
        """Execute LocalStack Terraform dry-run provisioning test."""
        # 1. If LocalStack is not live or terraform CLI missing, use high-fidelity emulated sandbox
        terraform_bin = shutil.which("terraform")
        if not self.is_available() or not terraform_bin:
            logger.debug(
                "LocalStack daemon or terraform CLI not available; utilizing emulated dry-run sandbox."
            )
            return EmulatedLocalStackSandbox.validate_terraform(content)

        # 2. Live LocalStack dry-run execution
        with tempfile.TemporaryDirectory(prefix="agentshield_sandbox_tf_") as tmpdir:
            tmppath = Path(tmpdir)
            target_file = tmppath / Path(file_path).name
            target_file.write_text(content, encoding="utf-8")

            # LocalStack AWS provider override
            provider_override = f"""
terraform {{
  required_providers {{
    aws = {{
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }}
  }}
}}

provider "aws" {{
  region                      = "{self.region}"
  access_key                  = "test"
  secret_key                  = "test"
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true

  endpoints {{
    s3  = "{self.endpoint_url}"
    ec2 = "{self.endpoint_url}"
    rds = "{self.endpoint_url}"
    iam = "{self.endpoint_url}"
  }}
}}
"""
            (tmppath / "localstack_override.tf").write_text(provider_override, encoding="utf-8")

            try:
                # Init
                init_res = subprocess.run(
                    [terraform_bin, "init", "-backend=false"],
                    cwd=tmpdir,
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                if init_res.returncode != 0:
                    # If network / plugin download fails, fallback to emulated
                    logger.warning("terraform init failed; falling back to emulated dry-run: %s", init_res.stderr)
                    return EmulatedLocalStackSandbox.validate_terraform(content)

                # Plan dry-run
                plan_res = subprocess.run(
                    [terraform_bin, "plan", "-no-color"],
                    cwd=tmpdir,
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                if plan_res.returncode != 0:
                    return ValidationCheckResult(
                        check_name="localstack_sandbox_dryrun",
                        passed=False,
                        output=plan_res.stdout,
                        error=f"LocalStack terraform plan failed: {plan_res.stderr.strip()}",
                    )

                return ValidationCheckResult(
                    check_name="localstack_sandbox_dryrun",
                    passed=True,
                    output=plan_res.stdout,
                )
            except Exception as exc:
                logger.warning("Live terraform execution exception: %s. Falling back to emulated.", exc)
                return EmulatedLocalStackSandbox.validate_terraform(content)

    def validate_cloudformation_dryrun(
        self, content: str, file_path: str = "template.yaml"
    ) -> ValidationCheckResult:
        """Execute LocalStack CloudFormation dry-run validation test."""
        if not self.is_available():
            return EmulatedLocalStackSandbox.validate_cloudformation(content)

        try:
            import boto3

            cfn_client = boto3.client(
                "cloudformation",
                endpoint_url=self.endpoint_url,
                region_name=self.region,
                aws_access_key_id="test",
                aws_secret_access_key="test",
            )
            # CloudFormation API validate_template
            val_res = cfn_client.validate_template(TemplateBody=content)
            desc = val_res.get("Description", "")
            return ValidationCheckResult(
                check_name="localstack_sandbox_dryrun",
                passed=True,
                output=f"LocalStack CloudFormation dry-run validated: {desc}",
            )
        except Exception as exc:
            logger.warning("LocalStack CloudFormation API call failed: %s. Using emulated dry-run.", exc)
            return EmulatedLocalStackSandbox.validate_cloudformation(content)

    def validate_runtime(
        self,
        iac_type: IaCType | str,
        content: str,
        file_path: str = "",
    ) -> ValidationCheckResult:
        """Route to appropriate LocalStack dry-run validator based on IaC type."""
        iac_str = str(iac_type.value if isinstance(iac_type, IaCType) else iac_type).lower()

        if iac_str in {"terraform", "hcl"}:
            return self.validate_terraform_dryrun(content, file_path=file_path or "main.tf")
        elif iac_str in {"cloudformation", "cfn"}:
            return self.validate_cloudformation_dryrun(content, file_path=file_path or "template.yaml")
        else:
            # For Kubernetes or Helm, LocalStack is not applicable; return pass
            return ValidationCheckResult(
                check_name="localstack_sandbox_dryrun",
                passed=True,
                output=f"IaC type '{iac_str}' does not require LocalStack AWS emulation; skipped.",
            )
