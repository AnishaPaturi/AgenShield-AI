"""Tests for Code & Sandbox Validator Agent and Automated Rollback Workflow.

Verifies:
1. Candidate patch application and atomic rollback
2. Multi-tool static lint validation across Terraform, CloudFormation, and Kubernetes
3. Automated rollback and re-remediation loop when lint errors occur
4. Retry exhaustion and escalation to human security review
5. Orchestrator and API endpoint integration
"""

import json
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from agentshield.agents import RemediationAgent, ValidatorAgent
from agentshield.api.main import app
from agentshield.api.store import workspace_store
from agentshield.core.llm import LLMClient
from agentshield.core.schemas import (
    AgentShieldWorkspace,
    CloudProvider,
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
from agentshield.validation import (
    TerraformValidateLinter,
    apply_patch_to_content,
    rollback_patch_from_content,
)


@pytest.fixture
def sample_tf_template() -> IaCTemplate:
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
    )


@pytest.fixture
def sample_finding() -> VulnerabilityFinding:
    return VulnerabilityFinding(
        rule_id="CKV_AWS_20",
        title="S3 Bucket Read Permissions Open To Public",
        description="S3 Bucket should not have public read access enabled.",
        severity=Severity.HIGH,
        confidence_score=0.95,
        affected_resource="aws_s3_bucket.data_bucket",
        resource_type="aws_s3_bucket",
        line_range=LineRange(start_line=1, end_line=4),
    )


def test_apply_and_rollback_patch(sample_tf_template: IaCTemplate):
    patch = PatchDiff(
        finding_id="f1",
        target_file="main.tf",
        original_code='acl    = "public-read"',
        patched_code='acl    = "private"',
        target_resource="aws_s3_bucket.data_bucket",
    )

    patched, ok = apply_patch_to_content(sample_tf_template.raw_content, patch)
    assert ok is True
    assert 'acl    = "private"' in patched
    assert 'acl    = "public-read"' not in patched

    # Rollback
    reverted = rollback_patch_from_content(patched, patch)
    assert 'acl    = "public-read"' in reverted
    assert reverted == sample_tf_template.raw_content


def test_validator_agent_clean_patch_passes(
    sample_tf_template: IaCTemplate, sample_finding: VulnerabilityFinding
):
    validator = ValidatorAgent()
    patch = PatchDiff(
        finding_id=sample_finding.finding_id,
        target_file="main.tf",
        original_code='acl    = "public-read"',
        patched_code='acl    = "private"',
        target_resource="aws_s3_bucket.data_bucket",
        remediation_status=RemediationStatus.PENDING,
    )

    validated = validator.validate_patch(
        template=sample_tf_template,
        patch=patch,
        finding=sample_finding,
    )

    assert validated.remediation_status in (
        RemediationStatus.SYNTAX_VALIDATED,
        RemediationStatus.SANDBOX_PASSED,
    )
    assert len(validated.validation_results) >= 1
    assert all(r.passed for r in validated.validation_results)
    check_names = [r.check_name for r in validated.validation_results]
    assert "terraform_validate" in check_names
    assert "tflint" in check_names


def test_validator_agent_automated_rollback_and_retry_success(
    sample_tf_template: IaCTemplate, sample_finding: VulnerabilityFinding
):
    """Simulate a patch that initially introduces a syntax error, triggers rollback, and succeeds on retry."""
    validator = ValidatorAgent()

    # Initial flawed patch with unbalanced closing brace
    flawed_patch = PatchDiff(
        finding_id=sample_finding.finding_id,
        target_file="main.tf",
        original_code='acl    = "public-read"',
        patched_code='acl    = "private" { syntax_error =',
        target_resource="aws_s3_bucket.data_bucket",
        remediation_status=RemediationStatus.PENDING,
    )

    # Mock LLM client for RemediationAgent that produces a valid fixed patch on re_remediate
    llm = LLMClient()
    repaired_payload = {
        "finding_id": sample_finding.finding_id,
        "target_file": "main.tf",
        "original_code": 'acl    = "public-read"',
        "patched_code": 'acl    = "private"',
        "target_resource": "aws_s3_bucket.data_bucket",
        "remediation_status": "PENDING",
        "explanation": "Corrected syntax error and set ACL to private",
    }
    llm.set_mock_responses([json.dumps(repaired_payload)])
    remediator = RemediationAgent(llm_client=llm)

    validated = validator.validate_patch(
        template=sample_tf_template,
        patch=flawed_patch,
        finding=sample_finding,
        remediator=remediator,
        max_retries=2,
    )

    # After rollback and re-remediation, the patch should be SYNTAX_VALIDATED or SANDBOX_PASSED
    assert validated.remediation_status in (
        RemediationStatus.SYNTAX_VALIDATED,
        RemediationStatus.SANDBOX_PASSED,
    )
    assert validated.patched_code == 'acl    = "private"'
    assert all(r.passed for r in validated.validation_results)


def test_validator_agent_retries_exhausted_escalates_to_human(
    sample_tf_template: IaCTemplate, sample_finding: VulnerabilityFinding
):
    """When a patch consistently fails linting across all retries, mark as FAILED and flag for human review."""
    validator = ValidatorAgent()

    # Consistently flawed patch
    flawed_patch = PatchDiff(
        finding_id=sample_finding.finding_id,
        target_file="main.tf",
        original_code='acl    = "public-read"',
        patched_code='acl    = "private" { invalid_syntax',
        target_resource="aws_s3_bucket.data_bucket",
        remediation_status=RemediationStatus.PENDING,
    )

    # Remediator that keeps returning an invalid patch
    llm = LLMClient()
    llm.set_mock_responses([
        json.dumps({
            "finding_id": sample_finding.finding_id,
            "target_file": "main.tf",
            "original_code": 'acl    = "public-read"',
            "patched_code": 'broken = broken {',
            "target_resource": "aws_s3_bucket.data_bucket",
        })
    ] * 5)
    remediator = RemediationAgent(llm_client=llm)

    validated = validator.validate_patch(
        template=sample_tf_template,
        patch=flawed_patch,
        finding=sample_finding,
        remediator=remediator,
        max_retries=1,
    )

    assert validated.remediation_status == RemediationStatus.FAILED
    assert validated.requires_human_review is True
    assert any(not r.passed for r in validated.validation_results)


def test_validator_agent_patch_apply_failure(sample_tf_template: IaCTemplate):
    validator = ValidatorAgent()
    missing_snippet_patch = PatchDiff(
        finding_id="nonexistent_finding",
        target_file="main.tf",
        original_code="this_code_does_not_exist_in_template = true",
        patched_code="this_code_does_not_exist_in_template = false",
        target_resource="aws_s3_bucket.data_bucket",
    )

    validated = validator.validate_patch(
        template=sample_tf_template,
        patch=missing_snippet_patch,
    )

    assert validated.remediation_status == RemediationStatus.FAILED
    assert validated.requires_human_review is True
    assert validated.validation_results[0].check_name == "patch_apply"
    assert validated.validation_results[0].passed is False


def test_validator_agent_batch_patches(
    sample_tf_template: IaCTemplate, sample_finding: VulnerabilityFinding
):
    validator = ValidatorAgent()
    p1 = PatchDiff(
        finding_id=sample_finding.finding_id,
        target_file="main.tf",
        original_code='acl    = "public-read"',
        patched_code='acl    = "private"',
        target_resource="aws_s3_bucket.data_bucket",
    )

    report = VulnerabilityReport(
        template_id=sample_tf_template.template_id,
        target_file=sample_tf_template.file_path,
        findings=[sample_finding],
    )

    validated_patches = validator.validate_patches(
        template=sample_tf_template,
        patches=[p1],
        report=report,
    )

    assert len(validated_patches) == 1
    assert validated_patches[0].remediation_status in (
        RemediationStatus.SYNTAX_VALIDATED,
        RemediationStatus.SANDBOX_PASSED,
    )


def test_api_patch_validation_endpoints(sample_tf_template: IaCTemplate):
    client = TestClient(app)

    patch = PatchDiff(
        finding_id="f_api_test",
        target_file="main.tf",
        original_code='acl    = "public-read"',
        patched_code='acl    = "private"',
        target_resource="aws_s3_bucket.data_bucket",
        remediation_status=RemediationStatus.PENDING,
    )

    ws = AgentShieldWorkspace(
        template=sample_tf_template,
        patches=[patch],
        status="REMEDIATED",
    )
    workspace_store.save(ws)

    # 1. Test single patch validate endpoint
    resp = client.post(f"/api/workspaces/{ws.workspace_id}/patches/{patch.patch_id}/validate")
    assert resp.status_code == 200
    res_body = resp.json()
    assert res_body["remediation_status"] in ("SYNTAX_VALIDATED", "SANDBOX_PASSED")
    assert len(res_body["validation_results"]) >= 1

    # 2. Test validate-patches all endpoint
    resp_all = client.post(f"/api/workspaces/{ws.workspace_id}/validate-patches")
    assert resp_all.status_code == 200
    all_body = resp_all.json()
    assert len(all_body) == 1
    assert all_body[0]["remediation_status"] in ("SYNTAX_VALIDATED", "SANDBOX_PASSED")

    # Clean up
    workspace_store.delete(ws.workspace_id)
