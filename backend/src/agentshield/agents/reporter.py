"""Report Generator Agent for AgentShield AI (Task 4.4).

Specialized Agent 8 in the AgentShield AI architecture.
Synthesizes security findings, multi-cloud compliance matrices (SOC 2, HIPAA, PCI-DSS, NIST 800-53),
attack paths, choke point mitigations, and validated patch diffs into audit-ready reports.

Supports unified multi-format rendering across:
- JSON (high-fidelity machine-readable)
- Markdown (PR, pull request comments, and developer documentation)
- HTML (standalone, styled executive web dashboard)
- SARIF (OASIS Static Analysis Results Interchange Format for GitHub Code Scanning)
- PDF (Executive summary document via ReportLab)
"""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from agentshield.api.report_export import MEDIA_TYPES, RENDERERS
from agentshield.core.schemas import (
    AgentShieldWorkspace,
    ComplianceFramework,
    PatchDiff,
    RemediationStatus,
    Severity,
    VulnerabilityFinding,
)

logger = logging.getLogger("agentshield.agents.reporter")


class ReportAgent:
    """Specialized Report Generator Agent (Agent 8) producing multi-format compliance reports."""

    def __init__(self) -> None:
        pass

    def generate_executive_summary(self, workspace: AgentShieldWorkspace) -> dict[str, Any]:
        """Compute top-level security posture metrics and estimated post-remediation score."""
        report = workspace.report
        if report is None:
            return {
                "risk_score_initial": 0.0,
                "risk_score_post_remediation": 0.0,
                "total_findings": 0,
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0,
                "informational": 0,
                "patches_generated": len(workspace.patches),
                "patches_validated": 0,
                "patches_applied": 0,
                "audit_queue_escalated": 0,
            }

        if report.summary.total_vulnerabilities == 0 and len(report.findings) > 0:
            report.recalculate_summary()
        s = report.summary
        patches = workspace.patches
        validated_count = sum(
            1 for p in patches if p.remediation_status in {RemediationStatus.SYNTAX_VALIDATED, RemediationStatus.SANDBOX_PASSED}
        )
        applied_count = sum(1 for p in patches if p.remediation_status == RemediationStatus.APPLIED)

        # Post remediation risk estimate: remediated findings remove their severity risk
        # A finding is remediated if patch is applied or sandbox passed
        remediated_ids = {
            p.finding_id
            for p in patches
            if p.remediation_status in {RemediationStatus.APPLIED, RemediationStatus.SANDBOX_PASSED}
        }
        unresolved_findings = [f for f in report.findings if f.finding_id not in remediated_ids]

        if not report.findings:
            post_risk = 0.0
        else:
            post_risk = round(
                (len(unresolved_findings) / len(report.findings)) * s.risk_score, 1
            )

        return {
            "risk_score_initial": s.risk_score,
            "risk_score_post_remediation": post_risk,
            "total_findings": s.total_vulnerabilities,
            "critical": s.critical_count,
            "high": s.high_count,
            "medium": s.medium_count,
            "low": s.low_count,
            "informational": s.info_count,
            "patches_generated": len(patches),
            "patches_validated": validated_count,
            "patches_applied": applied_count,
            "audit_queue_escalated": sum(1 for f in report.findings if f.requires_human_review),
        }

    def generate_compliance_matrix(
        self, workspace: AgentShieldWorkspace
    ) -> dict[str, dict[str, Any]]:
        """Map findings against SOC 2, HIPAA, PCI-DSS, and NIST 800-53 frameworks."""
        framework_findings: dict[str, list[dict[str, Any]]] = {
            "SOC2": [],
            "HIPAA": [],
            "PCI_DSS": [],
            "NIST_800_53": [],
        }

        report = workspace.report
        if report:
            for f in report.findings:
                for mapping in f.compliance_mappings:
                    fw_key = mapping.framework.value.upper().replace("-", "_")
                    if fw_key not in framework_findings:
                        framework_findings[fw_key] = []
                    framework_findings[fw_key].append(
                        {
                            "control_id": mapping.control_id,
                            "title": mapping.description or mapping.control_id,
                            "finding_id": f.finding_id,
                            "severity": f.severity.value,
                            "affected_resource": f.affected_resource,
                        }
                    )

        matrix: dict[str, dict[str, Any]] = {}
        for fw, findings in framework_findings.items():
            status = "COMPLIANT" if not findings else ("NON_COMPLIANT" if any(f["severity"] in {"CRITICAL", "HIGH"} for f in findings) else "PARTIALLY_COMPLIANT")
            matrix[fw] = {
                "status": status,
                "violation_count": len(findings),
                "controls_affected": sorted(list({f["control_id"] for f in findings})),
                "violations": findings,
            }

        return matrix

    def generate_attack_path_summary(
        self, workspace: AgentShieldWorkspace
    ) -> list[dict[str, Any]]:
        """Extract attack paths, blast radii, and choke point mitigations."""
        report = workspace.report
        if not report:
            return []

        paths: list[dict[str, Any]] = []
        for f in report.findings:
            if f.attack_path:
                details = f.raw_details or {}
                paths.append(
                    {
                        "finding_id": f.finding_id,
                        "title": f.title,
                        "severity": f.severity.value,
                        "attack_path": f.attack_path,
                        "attack_path_str": " -> ".join(f.attack_path),
                        "blast_radius": details.get("blast_radius", 1),
                        "priority_score": details.get("priority_score", 0.0),
                        "choke_points": [cp.get("name") for cp in details.get("choke_points", []) if isinstance(cp, dict)],
                    }
                )
        return sorted(paths, key=lambda p: p["priority_score"], reverse=True)

    def compile_report(self, workspace: AgentShieldWorkspace) -> dict[str, Any]:
        """Compile a full audit-ready compliance report data dictionary."""
        exec_summary = self.generate_executive_summary(workspace)
        compliance_matrix = self.generate_compliance_matrix(workspace)
        attack_paths = self.generate_attack_path_summary(workspace)

        patches_summary = [
            {
                "patch_id": p.patch_id,
                "finding_id": p.finding_id,
                "target_file": p.target_file,
                "target_resource": p.target_resource,
                "status": p.remediation_status.value,
                "auto_patchable": p.auto_patchable,
                "requires_human_review": p.requires_human_review,
                "validation_checks": [
                    {"name": c.check_name, "passed": c.passed, "error": c.error}
                    for c in p.validation_results
                ],
            }
            for p in workspace.patches
        ]

        return {
            "meta": {
                "workspace_id": workspace.workspace_id,
                "target_file": workspace.template.file_path,
                "iac_type": workspace.template.iac_type.value,
                "cloud_provider": workspace.template.cloud_provider.value,
                "generated_at": datetime.now(UTC).isoformat(),
                "agent": "AgentShield Report Generator Agent",
            },
            "executive_summary": exec_summary,
            "compliance_matrix": compliance_matrix,
            "attack_paths": attack_paths,
            "patches": patches_summary,
            "execution_logs": workspace.execution_logs,
        }

    def export(
        self, workspace: AgentShieldWorkspace, export_format: str = "json"
    ) -> str | bytes:
        """Export workspace security & compliance report in the specified format."""
        fmt = export_format.lower().strip()
        renderer = RENDERERS.get(fmt)
        if not renderer:
            valid_formats = ", ".join(RENDERERS.keys())
            raise ValueError(f"Unsupported export format '{fmt}'. Choose from: {valid_formats}")

        return renderer(workspace)

    def save_report_to_file(
        self,
        workspace: AgentShieldWorkspace,
        output_path: str | Path,
        export_format: str = "json",
    ) -> Path:
        """Render report and write directly to disk."""
        content = self.export(workspace, export_format=export_format)
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)

        if isinstance(content, bytes):
            out.write_bytes(content)
        else:
            out.write_text(content, encoding="utf-8")

        logger.info("Saved %s report to %s", export_format, out)
        return out


# Aliases for architectural alignment
ReportGeneratorAgent = ReportAgent
