"""Tests for RemediationAgent code patch generation workflow."""

import json

from agentshield.agents import RemediationAgent
from agentshield.core.llm import LLMClient
from agentshield.core.schemas import (
    IaCTemplate,
    PatchDiff,
    VulnerabilityFinding,
    VulnerabilityReport,
)


def test_remediation_agent_mock_structured(
    sample_iac_template: IaCTemplate, sample_vulnerability_finding: VulnerabilityFinding
):
    client = LLMClient()
    mock_payload = {
        "finding_id": sample_vulnerability_finding.finding_id,
        "target_file": sample_iac_template.file_path,
        "original_code": 'acl = "public-read"',
        "patched_code": 'acl = "private"',
        "target_resource": "aws_s3_bucket.data_bucket",
        "remediation_status": "PENDING",
        "explanation": "Updated ACL to private",
    }
    client.set_mock_responses([json.dumps(mock_payload)])

    agent = RemediationAgent(llm_client=client)
    patch = agent.generate_patch(sample_iac_template, sample_vulnerability_finding)

    assert isinstance(patch, PatchDiff)
    assert patch.finding_id == sample_vulnerability_finding.finding_id
    assert patch.original_code == 'acl = "public-read"'
    assert patch.patched_code == 'acl = "private"'
    assert "--- a/main.tf" in patch.unified_diff
    assert "+++ b/main.tf" in patch.unified_diff


def test_remediation_agent_fallback(
    sample_iac_template: IaCTemplate, sample_vulnerability_finding: VulnerabilityFinding
):
    client = LLMClient()
    client.set_mock_responses(["INVALID_JSON_RESPONSE"])

    agent = RemediationAgent(llm_client=client)
    patch = agent.generate_patch(sample_iac_template, sample_vulnerability_finding)

    assert isinstance(patch, PatchDiff)
    assert patch.finding_id == sample_vulnerability_finding.finding_id
    assert patch.unified_diff != ""
    assert patch.explanation != ""


def test_remediation_agent_batch_patches(
    sample_iac_template: IaCTemplate, sample_vulnerability_report: VulnerabilityReport
):
    client = LLMClient()
    agent = RemediationAgent(llm_client=client)
    patches = agent.generate_patches(sample_iac_template, sample_vulnerability_report)

    assert len(patches) == len(sample_vulnerability_report.findings)
    assert isinstance(patches[0], PatchDiff)
