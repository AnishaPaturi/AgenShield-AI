"""Pytest fixtures for AgentShield AI test suite."""

import pytest

from agentshield.core.schemas import (
    AgentShieldWorkspace,
    ASTNode,
    CloudProvider,
    ComplianceFramework,
    ComplianceMapping,
    IaCTemplate,
    IaCType,
    LineRange,
    PatchDiff,
    RemediationStatus,
    Severity,
    ValidationCheckResult,
    VulnerabilityFinding,
    VulnerabilityReport,
)


@pytest.fixture
def sample_line_range() -> LineRange:
    return LineRange(start_line=10, end_line=25)


@pytest.fixture
def sample_ast_root(sample_line_range: LineRange) -> ASTNode:
    s3_node = ASTNode(
        node_id="aws_s3_bucket.data_bucket",
        node_type="resource",
        resource_type="aws_s3_bucket",
        name="data_bucket",
        attributes={"bucket": "my-app-data-storage", "acl": "public-read"},
        line_range=LineRange(start_line=12, end_line=18),
        parent_id="root",
    )
    iam_node = ASTNode(
        node_id="aws_iam_role.app_role",
        node_type="resource",
        resource_type="aws_iam_role",
        name="app_role",
        attributes={"name": "my-app-role"},
        line_range=LineRange(start_line=20, end_line=25),
        parent_id="root",
    )
    return ASTNode(
        node_id="root",
        node_type="module",
        name="main_module",
        children=[s3_node, iam_node],
        line_range=sample_line_range,
    )


@pytest.fixture
def sample_iac_template(sample_ast_root: ASTNode) -> IaCTemplate:
    content = """resource "aws_s3_bucket" "data_bucket" {
  bucket = "my-app-data-storage"
  acl    = "public-read"
}
"""
    return IaCTemplate(
        file_path="main.tf",
        iac_type=IaCType.TERRAFORM,
        cloud_provider=CloudProvider.AWS,
        raw_content=content,
        parsed_ast=sample_ast_root,
    )


@pytest.fixture
def sample_vulnerability_finding() -> VulnerabilityFinding:
    return VulnerabilityFinding(
        rule_id="CKV_AWS_20",
        title="S3 Bucket Read Permissions Open To Public",
        description="S3 Bucket should not have public read access enabled.",
        severity=Severity.HIGH,
        confidence_score=0.95,
        affected_resource="aws_s3_bucket.data_bucket",
        resource_type="aws_s3_bucket",
        line_range=LineRange(start_line=12, end_line=18),
        compliance_mappings=[
            ComplianceMapping(
                framework=ComplianceFramework.SOC2,
                control_id="CC6.1",
                title="Logical Access Security",
            ),
            ComplianceMapping(
                framework=ComplianceFramework.PCI_DSS,
                control_id="Requirement-1.3",
                title="Restrict Public Access",
            ),
        ],
        remediation_hint="Set acl to 'private' and add aws_s3_bucket_public_access_block",
    )


@pytest.fixture
def sample_vulnerability_report(
    sample_iac_template: IaCTemplate, sample_vulnerability_finding: VulnerabilityFinding
) -> VulnerabilityReport:
    report = VulnerabilityReport(
        template_id=sample_iac_template.template_id,
        target_file=sample_iac_template.file_path,
        findings=[sample_vulnerability_finding],
        scanner_sources=["Checkov", "SecurityAnalystAgent"],
    )
    report.recalculate_summary()
    return report


@pytest.fixture
def sample_patch_diff(sample_vulnerability_finding: VulnerabilityFinding) -> PatchDiff:
    orig = """resource "aws_s3_bucket" "data_bucket" {
  bucket = "my-app-data-storage"
  acl    = "public-read"
}"""
    patched = """resource "aws_s3_bucket" "data_bucket" {
  bucket = "my-app-data-storage"
  acl    = "private"
}"""
    return PatchDiff(
        finding_id=sample_vulnerability_finding.finding_id,
        target_file="main.tf",
        original_code=orig,
        patched_code=patched,
        target_resource="aws_s3_bucket.data_bucket",
        remediation_status=RemediationStatus.SYNTAX_VALIDATED,
        validation_results=[
            ValidationCheckResult(
                check_name="terraform_validate",
                passed=True,
                output="Success! The configuration is valid.",
            )
        ],
        explanation="Changed ACL from public-read to private to prevent data exposure.",
    )


@pytest.fixture
def sample_workspace(
    sample_iac_template: IaCTemplate,
    sample_vulnerability_report: VulnerabilityReport,
    sample_patch_diff: PatchDiff,
) -> AgentShieldWorkspace:
    return AgentShieldWorkspace(
        template=sample_iac_template,
        report=sample_vulnerability_report,
        patches=[sample_patch_diff],
        status="REMEDIATED",
    )
