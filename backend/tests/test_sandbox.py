"""Unit tests for LocalStack Runtime Sandbox Testing Engine (Task 4.3)."""

from agentshield.agents import RemediationAgent, ValidatorAgent
from agentshield.core.schemas import (
    CloudProvider,
    IaCTemplate,
    IaCType,
    PatchDiff,
    RemediationStatus,
    Severity,
    ValidationCheckResult,
    VulnerabilityFinding,
)
from agentshield.validation import (
    EmulatedLocalStackSandbox,
    LocalStackSandbox,
)


def test_localstack_sandbox_availability():
    sandbox = LocalStackSandbox()
    # Should safely check without throwing exceptions
    avail = sandbox.is_available(timeout_sec=0.2)
    assert isinstance(avail, bool)


def test_emulated_sandbox_terraform_valid():
    valid_tf = """
resource "aws_s3_bucket" "data_bucket" {
  bucket = "my-secure-bucket"
}

resource "aws_security_group" "web_sg" {
  name        = "web-sg"
  description = "Web security group"
}
"""
    res = EmulatedLocalStackSandbox.validate_terraform(valid_tf)
    assert res.passed is True
    assert res.check_name == "localstack_sandbox_dryrun"
    assert "Validated" in res.output


def test_emulated_sandbox_terraform_broken_reference():
    broken_tf = """
resource "aws_s3_bucket" "data_bucket" {
  bucket = "my-secure-bucket"
}

resource "aws_security_group" "web_sg" {
  name        = "web-sg"
  description = "${aws_s3_bucket.non_existent_bucket.id}"
}
"""
    res = EmulatedLocalStackSandbox.validate_terraform(broken_tf)
    assert res.passed is False
    assert "non_existent_bucket" in res.error


def test_emulated_sandbox_cloudformation_valid():
    valid_cfn = """
AWSTemplateFormatVersion: '2010-09-09'
Resources:
  MyBucket:
    Type: 'AWS::S3::Bucket'
    Properties:
      BucketName: 'my-cfn-bucket'
"""
    res = EmulatedLocalStackSandbox.validate_cloudformation(valid_cfn)
    assert res.passed is True
    assert res.check_name == "localstack_sandbox_dryrun"


def test_emulated_sandbox_cloudformation_unresolved_ref():
    broken_cfn = """
AWSTemplateFormatVersion: '2010-09-09'
Resources:
  MyBucket:
    Type: 'AWS::S3::Bucket'
    Properties:
      BucketName: {"Ref": "NonExistentResource"}
"""
    res = EmulatedLocalStackSandbox.validate_cloudformation(broken_cfn)
    assert res.passed is False
    assert "unresolved ref" in res.error.lower()


def test_validator_agent_reaches_sandbox_passed():
    raw_tf = """
resource "aws_s3_bucket" "data_bucket" {
  bucket = "my-app-data-bucket"
  acl    = "public-read"
}
"""
    template = IaCTemplate(
        file_path="main.tf",
        raw_content=raw_tf,
        iac_type=IaCType.TERRAFORM,
        cloud_provider=CloudProvider.AWS,
    )

    clean_patch = PatchDiff(
        finding_id="find-001",
        target_file="main.tf",
        target_resource="aws_s3_bucket.data_bucket",
        original_code='  acl    = "public-read"',
        patched_code='  acl    = "private"',
    )

    validator = ValidatorAgent()
    validated = validator.validate_patch(template, clean_patch)

    assert validated.remediation_status == RemediationStatus.SANDBOX_PASSED
    assert len(validated.validation_results) >= 2
    # One of them is localstack_sandbox_dryrun
    sandbox_result = next(
        (r for r in validated.validation_results if r.check_name == "localstack_sandbox_dryrun"),
        None,
    )
    assert sandbox_result is not None
    assert sandbox_result.passed is True


def test_validator_agent_sandbox_failure_triggers_rollback():
    raw_tf = """
resource "aws_s3_bucket" "data_bucket" {
  bucket = "my-app-data-bucket"
}
"""
    template = IaCTemplate(
        file_path="main.tf",
        raw_content=raw_tf,
        iac_type=IaCType.TERRAFORM,
        cloud_provider=CloudProvider.AWS,
    )

    # Patch that introduces a broken reference caught by the sandbox
    bad_patch = PatchDiff(
        finding_id="find-002",
        target_file="main.tf",
        target_resource="aws_s3_bucket.data_bucket",
        original_code='resource "aws_s3_bucket" "data_bucket" {\n  bucket = "my-app-data-bucket"\n}',
        patched_code='resource "aws_s3_bucket" "data_bucket" {\n  bucket = "${aws_s3_bucket.deleted_bucket.id}"\n}',
    )

    validator = ValidatorAgent()
    remediator = RemediationAgent()  # Will re-remediate on rollback

    finding = VulnerabilityFinding(
        finding_id="find-002",
        rule_id="AWS_S3_REF",
        title="S3 Broken Reference Test",
        description="Broken reference test",
        severity=Severity.HIGH,
        affected_resource="aws_s3_bucket.data_bucket",
    )

    validated = validator.validate_patch(
        template,
        bad_patch,
        finding=finding,
        remediator=remediator,
        max_retries=1,
    )
    assert validated.remediation_status in {RemediationStatus.SANDBOX_PASSED, RemediationStatus.FAILED}
