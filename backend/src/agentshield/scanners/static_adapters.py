import json
from pathlib import Path
from typing import Any

from agentshield.core.schemas.vulnerability import Severity, VulnerabilityFinding


class BaseStaticAdapter:
    """Base class for static scanner output adapters."""

    def parse_json_report(self, report_json: str | dict[str, Any]) -> list[VulnerabilityFinding]:
        raise NotImplementedError


class CheckovAdapter(BaseStaticAdapter):
    """
    Adapter for Checkov static analysis scanner output.
    Converts Checkov JSON results into standardized VulnerabilityFinding instances.
    """

    SEVERITY_MAP = {
        "CRITICAL": Severity.CRITICAL,
        "HIGH": Severity.HIGH,
        "MEDIUM": Severity.MEDIUM,
        "LOW": Severity.LOW,
        "INFORMATIONAL": Severity.INFORMATIONAL,
    }

    def parse_json_report(self, report_data: str | dict[str, Any]) -> list[VulnerabilityFinding]:
        if isinstance(report_data, str):
            try:
                report_data = json.loads(report_data)
            except Exception as e:
                raise ValueError(f"Failed to parse Checkov JSON report string: {e}") from e

        findings = []
        failed_checks = report_data.get("results", {}).get("failed_checks", [])

        if isinstance(report_data, list):
            failed_checks = []
            for item in report_data:
                failed_checks.extend(item.get("results", {}).get("failed_checks", []))

        for check in failed_checks:
            check_id = check.get("check_id", "CKV_UNKNOWN")
            check_name = check.get("check_name", "Checkov Baseline Violation")
            resource = check.get("resource", "unknown_resource")

            severity_str = check.get("severity") or "MEDIUM"
            severity = self.SEVERITY_MAP.get(str(severity_str).upper(), Severity.MEDIUM)

            findings.append(
                VulnerabilityFinding(
                    finding_id=f"CHECKOV-{check_id}",
                    rule_id=check_id,
                    title=f"Checkov: {check_name}",
                    severity=severity,
                    description=f"Rule violation {check_id} detected by Checkov engine.",
                    affected_resource=resource,
                    resource_type=resource.split(".")[0] if "." in resource else "IaCResource",
                    remediation_hint=f"Remediate according to Checkov guidelines: {check.get('guideline', 'N/A')}",
                    confidence_score=0.95,
                )
            )

        return findings


class TfsecAdapter(BaseStaticAdapter):
    """
    Adapter for tfsec static analysis scanner output.
    """

    def parse_json_report(self, report_data: str | dict[str, Any]) -> list[VulnerabilityFinding]:
        if isinstance(report_data, str):
            try:
                report_data = json.loads(report_data)
            except Exception as e:
                raise ValueError(f"Failed to parse tfsec JSON report: {e}") from e

        findings = []
        results = report_data.get("results", [])

        for item in results:
            rule_id = item.get("rule_id", "TFSEC_UNKNOWN")
            rule_description = item.get("rule_description", "tfsec violation")
            resource = item.get("resource", "unknown_resource")

            findings.append(
                VulnerabilityFinding(
                    finding_id=f"TFSEC-{rule_id}",
                    rule_id=rule_id,
                    title=f"tfsec: {rule_description}",
                    severity=Severity.HIGH if "high" in str(item.get("severity")).lower() else Severity.MEDIUM,
                    description=item.get("description", rule_description),
                    affected_resource=resource,
                    resource_type="TerraformResource",
                    remediation_hint=item.get("resolution", "Update Terraform block properties."),
                    confidence_score=0.95,
                )
            )

        return findings


class KicsAdapter(BaseStaticAdapter):
    """
    Adapter for KICS static analysis scanner output.
    """

    def parse_json_report(self, report_data: str | dict[str, Any]) -> list[VulnerabilityFinding]:
        if isinstance(report_data, str):
            try:
                report_data = json.loads(report_data)
            except Exception as e:
                raise ValueError(f"Failed to parse KICS JSON report: {e}") from e

        findings = []
        queries = report_data.get("queries", [])

        for query in queries:
            query_id = query.get("query_id", "KICS_UNKNOWN")
            query_name = query.get("query_name", "KICS Security Query")
            severity_str = query.get("severity", "MEDIUM").upper()

            severity = Severity.MEDIUM
            if severity_str == "HIGH" or severity_str == "CRITICAL":
                severity = Severity.HIGH
            elif severity_str == "LOW":
                severity = Severity.LOW

            for file_item in query.get("files", []):
                resource_name = file_item.get("resource_name", "kics_resource")

                findings.append(
                    VulnerabilityFinding(
                        finding_id=f"KICS-{query_id}",
                        rule_id=query_id,
                        title=f"KICS: {query_name}",
                        severity=severity,
                        description=query.get("description", query_name),
                        affected_resource=resource_name,
                        resource_type="PolyglotResource",
                        remediation_hint=query.get("remediation", "Fix misconfiguration according to KICS docs."),
                        confidence_score=0.92,
                    )
                )

        return findings


class StaticScannerRegistry:
    """
    Unified Static Scanner Registry managing Checkov, tfsec, and KICS adapters.
    """

    def __init__(self):
        self.checkov_adapter = CheckovAdapter()
        self.tfsec_adapter = TfsecAdapter()
        self.kics_adapter = KicsAdapter()

    def parse_reports(self, checkov_data=None, tfsec_data=None, kics_data=None) -> list[VulnerabilityFinding]:
        findings = []
        if checkov_data:
            findings.extend(self.checkov_adapter.parse_json_report(checkov_data))
        if tfsec_data:
            findings.extend(self.tfsec_adapter.parse_json_report(tfsec_data))
        if kics_data:
            findings.extend(self.kics_adapter.parse_json_report(kics_data))
        return findings
