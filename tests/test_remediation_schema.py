"""Tests for PatchDiff and RemediationStatus Pydantic v2 schemas."""

from agentshield.core.schemas.remediation import PatchDiff, ValidationCheckResult


def test_patch_diff_unified_diff_auto_generation(sample_patch_diff: PatchDiff):
    assert sample_patch_diff.unified_diff != ""
    assert "--- a/main.tf" in sample_patch_diff.unified_diff
    assert "+++ b/main.tf" in sample_patch_diff.unified_diff
    assert '-  acl    = "public-read"' in sample_patch_diff.unified_diff
    assert '+  acl    = "private"' in sample_patch_diff.unified_diff


def test_validation_check_result():
    res = ValidationCheckResult(check_name="cfn_lint", passed=True, output="No issues found")
    assert res.check_name == "cfn_lint"
    assert res.passed is True
    assert res.error is None
