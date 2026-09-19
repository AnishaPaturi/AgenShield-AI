"""Live Cloud Infrastructure Drift Detector Engine for AgentShield AI (Task 5.2).

Detects out-of-band manual state changes by comparing IaC source code against
live cloud provider resource states (AWS, Azure, GCP).
Generates actionable reconciliation patch diffs to restore security posture.
"""

from __future__ import annotations

import logging
from typing import Any

from agentshield.core.drift.models import (
    DriftItem,
    DriftReport,
    DriftSeverity,
    DriftType,
)
from agentshield.core.drift.monitors import (
    AWSCloudMonitor,
    AzureCloudMonitor,
    BaseCloudMonitor,
    GCPCloudMonitor,
)
from agentshield.core.schemas import (
    CloudProvider,
    IaCTemplate,
    PatchDiff,
    RemediationStatus,
)

logger = logging.getLogger("agentshield.core.drift.detector")


class DriftDetector:
    """Detects security discrepancies between IaC definitions and live cloud environments."""

    def __init__(
        self,
        monitors: dict[CloudProvider, BaseCloudMonitor] | None = None,
    ) -> None:
        self.monitors = monitors or {
            CloudProvider.AWS: AWSCloudMonitor(),
            CloudProvider.AZURE: AzureCloudMonitor(),
            CloudProvider.GCP: GCPCloudMonitor(),
        }

    def detect_drift(
        self,
        template: IaCTemplate,
        workspace_id: str | None = None,
    ) -> DriftReport:
        """Execute drift detection across all resources defined in the template."""
        report = DriftReport(
            workspace_id=workspace_id,
            file_path=template.file_path,
            cloud_provider=template.cloud_provider,
        )

        monitor = self.monitors.get(template.cloud_provider) or self.monitors.get(CloudProvider.AWS)
        if not monitor:
            logger.warning("No monitor available for cloud provider %s", template.cloud_provider)
            return report

        # Extract declared resources from AST or raw template
        resources = self._extract_resources(template)

        for res in resources:
            r_type = res["resource_type"]
            r_name = res["resource_name"]
            r_id = f"{r_type}.{r_name}"
            declared_props = res.get("properties", {})

            live_state = monitor.get_live_resource_state(r_type, r_name)
            if live_state is None:
                # Live resource not found in cloud
                continue

            drifts = self._compare_resource(
                template=template,
                resource_id=r_id,
                resource_type=r_type,
                declared=declared_props,
                live=live_state,
            )
            report.drifts.extend(drifts)

        report.recalculate()
        return report

    def _extract_resources(self, template: IaCTemplate) -> list[dict[str, Any]]:
        """Extract declared resources from parsed AST or polyglot dispatcher."""
        resources: list[dict[str, Any]] = []

        if template.parsed_ast:
            for node in template.parsed_ast.children:
                if node.node_type == "resource" and node.resource_type:
                    resources.append(
                        {
                            "resource_type": node.resource_type,
                            "resource_name": node.name,
                            "properties": node.attributes,
                        }
                    )
            if resources:
                return resources

        # Fallback extraction from raw content
        raw = template.raw_content
        import re

        # Terraform HCL pattern
        tf_matches = re.findall(r'resource\s+"([a-zA-Z0-9_]+)"\s+"([a-zA-Z0-9_]+)"\s*\{', raw)
        for r_type, r_name in tf_matches:
            props: dict[str, Any] = {}
            if "publicly_accessible" in raw:
                props["publicly_accessible"] = "publicly_accessible = true" in raw or "publicly_accessible   = true" in raw
            if "storage_encrypted" in raw:
                props["storage_encrypted"] = "storage_encrypted = true" in raw or "storage_encrypted   = true" in raw
            if "0.0.0.0/0" in raw:
                props["cidr_blocks"] = ["0.0.0.0/0"]
            if "acl" in raw:
                props["acl"] = "public-read" if "public-read" in raw else "private"

            resources.append(
                {
                    "resource_type": r_type,
                    "resource_name": r_name,
                    "properties": props,
                }
            )

        return resources

    def _compare_resource(
        self,
        template: IaCTemplate,
        resource_id: str,
        resource_type: str,
        declared: dict[str, Any],
        live: dict[str, Any],
    ) -> list[DriftItem]:
        """Compare declared vs live properties and identify security degradations."""
        drifts: list[DriftItem] = []

        # 1. Security Group Ingress comparison
        if "security_group" in resource_type.lower():
            live_ingress = live.get("ingress", [])
            # Check for live ingress rules granting 0.0.0.0/0 that weren't declared in IaC
            for rule in live_ingress:
                cidrs = rule.get("cidr_blocks", [])
                port = rule.get("from_port") or "all"
                if "0.0.0.0/0" in cidrs:
                    declared_cidrs = []
                    if "ingress" in declared and isinstance(declared["ingress"], list):
                        for di in declared["ingress"]:
                            declared_cidrs.extend(di.get("cidr_blocks", []))

                    if "0.0.0.0/0" not in declared_cidrs:
                        # Out-of-band open port modification in live cloud!
                        reconcile_patch = None
                        if '"0.0.0.0/0"' in template.raw_content:
                            reconcile_patch = PatchDiff(
                                finding_id=f"drift-{resource_id}",
                                target_file=template.file_path,
                                target_resource=resource_id,
                                original_code='"0.0.0.0/0"',
                                patched_code='"10.0.0.0/16"',
                                explanation="Reconcile out-of-band drift: restrict open ingress to private VPC CIDR 10.0.0.0/16",
                            )

                        drifts.append(
                            DriftItem(
                                resource_id=resource_id,
                                resource_type=resource_type,
                                drift_type=DriftType.OUT_OF_BAND_ADDITION,
                                severity=DriftSeverity.CRITICAL,
                                attribute_path=f"ingress[port={port}].cidr_blocks",
                                expected_iac_value=declared_cidrs or ["(no 0.0.0.0/0 rule)"],
                                actual_live_value=["0.0.0.0/0"],
                                security_implication=(
                                    f"Security group '{resource_id}' was manually altered in the live cloud "
                                    f"to allow open internet access (0.0.0.0/0) on port {port}."
                                ),
                                reconciliation_suggestion=(
                                    f"Revoke out-of-band rule in AWS Console/CLI or update IaC template to "
                                    f"restrict CIDR to authorized corporate subnets."
                                ),
                                reconciliation_patch=reconcile_patch,
                            )
                        )

        # 2. S3 Bucket Public Access Block & ACL comparison
        if "s3_bucket" in resource_type.lower():
            live_acl = live.get("acl")
            declared_acl = declared.get("acl", "private")
            if live_acl == "public-read" and declared_acl != "public-read":
                reconcile_patch = None
                if 'acl = "public-read"' in template.raw_content or 'acl    = "public-read"' in template.raw_content:
                    orig = 'acl    = "public-read"' if 'acl    = "public-read"' in template.raw_content else 'acl = "public-read"'
                    reconcile_patch = PatchDiff(
                        finding_id=f"drift-{resource_id}",
                        target_file=template.file_path,
                        target_resource=resource_id,
                        original_code=orig,
                        patched_code='acl    = "private"',
                        explanation="Reconcile S3 ACL drift to private access",
                    )

                drifts.append(
                    DriftItem(
                        resource_id=resource_id,
                        resource_type=resource_type,
                        drift_type=DriftType.SECURITY_DEGRADATION,
                        severity=DriftSeverity.HIGH,
                        attribute_path="acl",
                        expected_iac_value=declared_acl,
                        actual_live_value=live_acl,
                        security_implication=(
                            f"Live S3 bucket '{resource_id}' has public-read ACL enabled in AWS, "
                            f"diverging from declared private baseline."
                        ),
                        reconciliation_suggestion="Re-apply S3 Block Public Access and restore private ACL.",
                        reconciliation_patch=reconcile_patch,
                    )
                )

        # 3. Database Encryption & Public Access comparison
        if "db_instance" in resource_type.lower():
            live_enc = live.get("storage_encrypted", False)
            declared_enc = declared.get("storage_encrypted", True)
            if declared_enc is True and live_enc is False:
                drifts.append(
                    DriftItem(
                        resource_id=resource_id,
                        resource_type=resource_type,
                        drift_type=DriftType.SECURITY_DEGRADATION,
                        severity=DriftSeverity.HIGH,
                        attribute_path="storage_encrypted",
                        expected_iac_value=True,
                        actual_live_value=False,
                        security_implication=(
                            f"Database '{resource_id}' is running in live cloud without storage encryption, "
                            f"violating declared IaC security policy."
                        ),
                        reconciliation_suggestion="Enable KMS storage encryption for RDS database.",
                    )
                )

        return drifts
