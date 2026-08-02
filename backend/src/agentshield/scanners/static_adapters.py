import json
from pathlib import Path
from typing import Any

from agentshield.core.schemas.vulnerability import SeverityLevel, VulnerabilityFinding


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
        "CRITICAL": SeverityLevel.CRITICAL,
        "HIGH": SeverityLevel.HIGH,
        "MEDIUM": SeverityLevel.MEDIUM,
        "LOW": SeverityLevel.LOW,
        "INFORMATIONAL": SeverityLevel.LOW,
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
            file_line_range = check.get("file_line_range", [1, 1])

            severity_str = check.get("severity") or "MEDIUM"
            severity = self.SEVERITY_MAP.get(str(severity_str).upper(), SeverityLevel.MEDIUM)

            findings.append(
                VulnerabilityFinding(
                    finding_id=f"CHECKOV-{check_id}",
                    title=f"Checkov: {check_name}",
                    severity=severity,
                    category="Static Scanner Rule",
                    description=f"Rule violation {check_id} detected by Checkov engine.",
                    resource_id=resource,
                    resource_type=resource.split(".")[0] if "." in resource else "IaCResource",
                    affected_line_start=file_line_range[0] if len(file_line_range) > 0 else 1,
                    affected_line_end=file_line_range[1] if len(file_line_range) > 1 else 1,
                    cwe_id=check.get("guideline"),
                    remediation_recommendation=f"Remediate according to Checkov guidelines: {check.get('guideline', 'N/A')}",
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
            location = item.get("location", {})
            start_line = location.get("start_line", 1)
            end_line = location.get("end_line", 1)

            findings.append(
                VulnerabilityFinding(
                    finding_id=f"TFSEC-{rule_id}",
                    title=f"tfsec: {rule_description}",
                    severity=SeverityLevel.HIGH if "high" in str(item.get("severity")).lower() else SeverityLevel.MEDIUM,
                    category="Static Scanner Rule",
                    description=item.get("description", rule_description),
                    resource_id=resource,
                    resource_type="TerraformResource",
                    affected_line_start=start_line,
                    affected_line_end=end_line,
                    remediation_recommendation=item.get("resolution", "Update Terraform block properties."),
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

            severity = SeverityLevel.MEDIUM
            if severity_str == "HIGH" or severity_str == "CRITICAL":
                severity = SeverityLevel.HIGH
            elif severity_str == "LOW":
                severity = SeverityLevel.LOW

            for file_item in query.get("files", []):
                resource_name = file_item.get("resource_name", "kics_resource")
                line = file_item.get("line", 1)

                findings.append(
                    VulnerabilityFinding(
                        finding_id=f"KICS-{query_id}",
                        title=f"KICS: {query_name}",
                        severity=severity,
                        category="Static Scanner Rule",
                        description=query.get("description", query_name),
                        resource_id=resource_name,
                        resource_type="PolyglotResource",
                        affected_line_start=line,
                        affected_line_end=line,
                        remediation_recommendation=query.get("remediation", "Fix misconfiguration according to KICS docs."),
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
