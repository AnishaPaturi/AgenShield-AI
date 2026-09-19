"""Unit tests for Git Pre-Commit Hook (Task 5.1)."""

from pathlib import Path

from agentshield.cli.hook import main, scan_file


def test_hook_scan_secure_file(tmp_path: Path):
    secure_tf = tmp_path / "secure.tf"
    secure_tf.write_text(
        """
resource "aws_s3_bucket" "secure_bucket" {
  bucket = "company-secure-storage-bucket"
  acl    = "private"
}
""",
        encoding="utf-8",
    )

    passed, issues, patched = scan_file(secure_tf)
    assert passed is True
    assert len(issues) == 0
    assert patched is None


def test_hook_scan_secret_interception(tmp_path: Path):
    secret_tf = tmp_path / "secret.tf"
    secret_tf.write_text(
        """
provider "aws" {
  region     = "us-east-1"
  access_key = "AKIAIOSFODNN7EXAMPLE"
}
""",
        encoding="utf-8",
    )

    passed, issues, patched = scan_file(secret_tf)
    assert passed is False
    assert any("SECRET" in issue for issue in issues)


def test_hook_scan_and_auto_fix(tmp_path: Path):
    insecure_tf = tmp_path / "insecure.tf"
    insecure_tf.write_text(
        """
resource "aws_s3_bucket" "data_bucket" {
  bucket = "my-data-bucket"
  acl    = "public-read"
}
""",
        encoding="utf-8",
    )

    # First without fix
    passed_no_fix, issues, patched_none = scan_file(insecure_tf, auto_fix=False)
    assert passed_no_fix is False
    assert len(issues) >= 1

    # Now with auto_fix
    passed_fixed, issues_fix, patched_content = scan_file(insecure_tf, auto_fix=True)
    assert patched_content is not None
    assert 'acl    = "private"' in patched_content or 'acl = "private"' in patched_content


def test_hook_cli_main_exit_codes(tmp_path: Path):
    clean_tf = tmp_path / "clean.tf"
    clean_tf.write_text(
        'resource "aws_s3_bucket" "b" { bucket = "clean-b"; acl = "private" }',
        encoding="utf-8",
    )

    # Clean file should exit 0
    code_clean = main([str(clean_tf)])
    assert code_clean == 0

    bad_tf = tmp_path / "bad.tf"
    bad_tf.write_text(
        'provider "aws" { access_key = "AKIAIOSFODNN7EXAMPLE" }',
        encoding="utf-8",
    )

    # Insecure file should exit 1
    code_bad = main([str(bad_tf)])
    assert code_bad == 1
