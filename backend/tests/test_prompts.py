"""Tests for Prompt Engineering Engine and User Prompt Builders."""

from agentshield.agents.prompts import (
    ANALYST_SYSTEM_PROMPT,
    REMEDIATION_RETRY_SYSTEM_PROMPT,
    REMEDIATION_SYSTEM_PROMPT,
    build_analyst_user_prompt,
    build_remediation_retry_prompt,
    build_remediation_user_prompt,
)
from agentshield.core.schemas import IaCTemplate, PatchDiff, VulnerabilityFinding


def test_system_prompts_exist():
    assert "AgentShield AI" in ANALYST_SYSTEM_PROMPT
    assert "SOC2" in ANALYST_SYSTEM_PROMPT
    assert "Remediation Agent" in REMEDIATION_SYSTEM_PROMPT
    assert "Error-Correction Mode" in REMEDIATION_RETRY_SYSTEM_PROMPT



def test_build_analyst_user_prompt(sample_iac_template: IaCTemplate):
    prompt = build_analyst_user_prompt(
        sample_iac_template,
        static_findings=[{"rule_id": "CKV_AWS_18", "status": "FAILED"}],
        context_docs=["Ensure S3 bucket is private"],
    )
    assert "Target IaC File: main.tf" in prompt
    assert "CKV_AWS_18" in prompt
    assert "Ensure S3 bucket is private" in prompt
    assert "my-app-data-storage" in prompt


def test_build_remediation_user_prompt(
    sample_iac_template: IaCTemplate, sample_vulnerability_finding: VulnerabilityFinding
):
    prompt = build_remediation_user_prompt(sample_iac_template, sample_vulnerability_finding)
    assert "Target IaC File: main.tf" in prompt
    assert "CKV_AWS_20" in prompt
    assert "S3 Bucket Read Permissions Open To Public" in prompt
    assert "aws_s3_bucket.data_bucket" in prompt


def test_build_remediation_retry_prompt(
    sample_iac_template: IaCTemplate, sample_vulnerability_finding: VulnerabilityFinding
):
    failed_patch = PatchDiff(
        finding_id=sample_vulnerability_finding.finding_id,
        target_file="main.tf",
        original_code='acl    = "public-read"',
        patched_code='acl    = "private" { bad_syntax',
        target_resource="aws_s3_bucket.data_bucket",
    )
    lint_errors = ["terraform_validate: Unbalanced braces", "tflint: syntax violation"]
    prompt = build_remediation_retry_prompt(
        sample_iac_template,
        sample_vulnerability_finding,
        failed_patch,
        lint_errors,
    )

    assert "Target IaC File: main.tf" in prompt
    assert "PREVIOUS FAILED PATCH" in prompt
    assert "STATIC LINTER ERROR FEEDBACK" in prompt
    assert "terraform_validate: Unbalanced braces" in prompt
    assert "tflint: syntax violation" in prompt

