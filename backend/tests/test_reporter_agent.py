"""Unit tests for Report Generator Agent (Task 4.4)."""

import json
from pathlib import Path

from agentshield.agents.reporter import ReportAgent, ReportGeneratorAgent
from agentshield.core.schemas import (
    AgentShieldWorkspace,
    CloudProvider,
    ComplianceFramework,
    ComplianceMapping,
    IaCTemplate,
    IaCType,
    PatchDiff,
    RemediationStatus,
    Severity,
    VulnerabilityFinding,
    VulnerabilityReport,
)


def _build_test_workspace() -> AgentShieldWorkspace:
    template = IaCTemplate(
        file_path="infra/main.tf",
        raw_content='resource "aws_s3_bucket" "b" { acl = "public-read" }',
        iac_type=IaCType.TERRAFORM,
        cloud_provider=CloudProvider.AWS,
    )

    finding1 = VulnerabilityFinding(
        finding_id="find-001",
        rule_id="CKV_AWS_20",
        title="S3 Bucket Public Read Allowed",
        description="S3 bucket allows public read ACL access.",
        severity=Severity.HIGH,
        affected_resource="aws_s3_bucket.b",
        confidence_score=0.92,
        attack_path=["Internet Gateway", "aws_security_group.web", "aws_s3_bucket.b"],
        compliance_mappings=[
            ComplianceMapping(
                framework=ComplianceFramework.PCI_DSS,
                control_id="PCI-DSS-1.3",
                title="Restrict public access",
                description="Restrict public access",
            ),
            ComplianceMapping(
                framework=ComplianceFramework.SOC2,
                control_id="CC6.1",
                title="Logical access controls",
                description="Logical access controls",
            ),
        ],
        raw_details={
            "blast_radius": 3,
            "priority_score": 85.5,
            "choke_points": [{"name": "aws_security_group.web", "cut_score": 0.8}],
        },
    )

    report = VulnerabilityReport(
        template_id=template.template_id,
        target_file="infra/main.tf",
        findings=[finding1],
    )

    patch1 = PatchDiff(
        finding_id="find-001",
        target_file="infra/main.tf",
        target_resource="aws_s3_bucket.b",
        original_code='acl = "public-read"',
        patched_code='acl = "private"',
        remediation_status=RemediationStatus.SANDBOX_PASSED,
    )

    return AgentShieldWorkspace(
        template=template,
        report=report,
        patches=[patch1],
    )


def test_report_agent_executive_summary():
    ws = _build_test_workspace()
    agent = ReportAgent()
    summary = agent.generate_executive_summary(ws)

    assert summary["total_findings"] == 1
    assert summary["high"] == 1
    assert summary["patches_generated"] == 1
    assert summary["patches_validated"] == 1
    assert summary["risk_score_post_remediation"] < summary["risk_score_initial"] or summary["risk_score_initial"] == 0.0


def test_report_agent_compliance_matrix():
    ws = _build_test_workspace()
    agent = ReportAgent()
    matrix = agent.generate_compliance_matrix(ws)

    assert "PCI_DSS" in matrix
    assert "SOC2" in matrix
    assert matrix["PCI_DSS"]["status"] == "NON_COMPLIANT"
    assert "PCI-DSS-1.3" in matrix["PCI_DSS"]["controls_affected"]


def test_report_agent_attack_path_summary():
    ws = _build_test_workspace()
    agent = ReportAgent()
    paths = agent.generate_attack_path_summary(ws)

    assert len(paths) == 1
    assert paths[0]["blast_radius"] == 3
    assert paths[0]["priority_score"] == 85.5
    assert "aws_security_group.web" in paths[0]["choke_points"]


def test_report_agent_compile_report():
    ws = _build_test_workspace()
    agent = ReportGeneratorAgent()
    compiled = agent.compile_report(ws)

    assert compiled["meta"]["iac_type"] == "terraform"
    assert "executive_summary" in compiled
    assert "compliance_matrix" in compiled
    assert "attack_paths" in compiled
    assert len(compiled["patches"]) == 1


def test_report_agent_exports(tmp_path: Path):
    ws = _build_test_workspace()
    agent = ReportAgent()

    # Markdown export
    md_content = agent.export(ws, "markdown")
    assert isinstance(md_content, str)
    assert "AgentShield AI" in md_content
    assert "CKV_AWS_20" in md_content

    # JSON export
    json_content = agent.export(ws, "json")
    parsed = json.loads(json_content)
    assert parsed["template"]["file_path"] == "infra/main.tf"

    # HTML export
    html_content = agent.export(ws, "html")
    assert "<html" in html_content

    # SARIF export
    sarif_content = agent.export(ws, "sarif")
    sarif_data = json.loads(sarif_content)
    assert sarif_data["version"] == "2.1.0"

    # PDF export
    pdf_bytes = agent.export(ws, "pdf")
    assert isinstance(pdf_bytes, bytes)
    assert pdf_bytes.startswith(b"%PDF")

    # File save
    saved = agent.save_report_to_file(ws, tmp_path / "test_report.md", "markdown")
    assert saved.exists()
    assert len(saved.read_text(encoding="utf-8")) > 50
