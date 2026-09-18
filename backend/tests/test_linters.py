"""Unit tests for Static Verification Tools (Linters) in AgentShield AI.

Tests coverage across:
1. terraform validate (syntax and HCL structure)
2. tflint (best practice rules, naming, deprecated syntax)
3. cfn-lint (AWS CloudFormation syntax and specification)
4. kube-linter (Kubernetes manifest security and best practices)
5. helm lint (Helm chart and template validation)
"""

import pytest

from agentshield.core.schemas import IaCType, ValidationCheckResult
from agentshield.validation import (
    BaseLinter,
    CfnLintLinter,
    HelmLintLinter,
    KubeLinter,
    TerraformValidateLinter,
    TflintLinter,
    get_linters_for_iac_type,
)


def test_terraform_validate_linter_success():
    linter = TerraformValidateLinter()
    valid_tf = """
resource "aws_s3_bucket" "data_bucket" {
  bucket = "my-secure-bucket"
  acl    = "private"
}
"""
    result = linter.validate(valid_tf)
    assert result.passed is True
    assert result.check_name == "terraform_validate"
    assert result.error is None
    assert "valid" in result.output.lower()


def test_terraform_validate_linter_unbalanced_braces():
    linter = TerraformValidateLinter()
    invalid_tf = """
resource "aws_s3_bucket" "data_bucket" {
  bucket = "my-secure-bucket"
  acl    = "private"
"""
    result = linter.validate(invalid_tf)
    assert result.passed is False
    assert result.check_name == "terraform_validate"
    assert "unbalanced braces" in result.error.lower() or "unclosed configuration block" in result.error.lower()


def test_terraform_validate_linter_syntax_error():
    linter = TerraformValidateLinter()
    malformed_tf = """
resource "aws_s3_bucket" "data_bucket" {
  bucket = = "my-secure-bucket"
}
"""
    result = linter.validate(malformed_tf)
    assert result.passed is False
    assert result.error is not None


def test_tflint_linter_success():
    linter = TflintLinter()
    valid_tf = """
resource "aws_s3_bucket" "secure_bucket" {
  bucket = "my-bucket"
}
"""
    result = linter.validate(valid_tf)
    assert result.passed is True
    assert result.check_name == "tflint"
    assert result.error is None


def test_tflint_linter_naming_violation():
    linter = TflintLinter()
    invalid_name_tf = """
resource "aws_s3_bucket" "My-Invalid-Name" {
  bucket = "my-bucket"
}
"""
    result = linter.validate(invalid_name_tf)
    assert result.passed is False
    assert result.check_name == "tflint"
    assert "naming violation" in result.error.lower()


def test_tflint_linter_duplicate_resource():
    linter = TflintLinter()
    dup_tf = """
resource "aws_s3_bucket" "shared_bucket" {
  bucket = "bucket-1"
}

resource "aws_s3_bucket" "shared_bucket" {
  bucket = "bucket-2"
}
"""
    result = linter.validate(dup_tf)
    assert result.passed is False
    assert result.check_name == "tflint"
    assert "duplicate violation" in result.error.lower()


def test_tflint_linter_deprecated_interpolation():
    linter = TflintLinter()
    dep_tf = """
resource "aws_s3_bucket" "my_bucket" {
  bucket = "${var.my_bucket_name}"
}
"""
    result = linter.validate(dep_tf)
    assert result.passed is False
    assert result.check_name == "tflint"
    assert "deprecated interpolation" in result.error.lower()


def test_cfn_lint_linter_success():
    linter = CfnLintLinter()
    valid_cfn = """
AWSTemplateFormatVersion: "2010-09-09"
Description: Sample S3 Bucket Template
Resources:
  EncryptedBucket:
    Type: "AWS::S3::Bucket"
    Properties:
      BucketName: "my-cfn-bucket"
"""
    result = linter.validate(valid_cfn)
    assert result.passed is True
    assert result.check_name == "cfn_lint"
    assert result.error is None


def test_cfn_lint_linter_invalid_yaml():
    linter = CfnLintLinter()
    bad_yaml = """
AWSTemplateFormatVersion: "2010-09-09"
Resources: [Unterminated list
"""
    result = linter.validate(bad_yaml)
    assert result.passed is False
    assert result.check_name == "cfn_lint"
    assert "syntax error" in result.error.lower()


def test_cfn_lint_linter_missing_type():
    linter = CfnLintLinter()
    missing_type_cfn = """
AWSTemplateFormatVersion: "2010-09-09"
Resources:
  MyBucket:
    Properties:
      BucketName: "missing-type-bucket"
"""
    result = linter.validate(missing_type_cfn)
    assert result.passed is False
    assert "missing required 'Type' field" in result.error


def test_cfn_lint_linter_unrecognized_key():
    linter = CfnLintLinter()
    bad_key_cfn = """
AWSTemplateFormatVersion: "2010-09-09"
InvalidSectionName:
  Foo: "bar"
Resources:
  MyBucket:
    Type: "AWS::S3::Bucket"
"""
    result = linter.validate(bad_key_cfn)
    assert result.passed is False
    assert "unrecognized top-level" in result.error.lower()


def test_kube_linter_success():
    linter = KubeLinter()
    valid_k8s = """
apiVersion: v1
kind: Pod
metadata:
  name: secure-app
spec:
  containers:
    - name: web
      image: "nginx:1.25.3"
      securityContext:
        privileged: false
"""
    result = linter.validate(valid_k8s)
    assert result.passed is True
    assert result.check_name == "kube_linter"
    assert result.error is None


def test_kube_linter_missing_metadata_name():
    linter = KubeLinter()
    missing_name_k8s = """
apiVersion: v1
kind: Pod
metadata:
  labels:
    app: test
spec:
  containers:
    - name: web
      image: "nginx:1.25.3"
"""
    result = linter.validate(missing_name_k8s)
    assert result.passed is False
    assert "missing 'metadata.name'" in result.error


def test_kube_linter_privileged_container():
    linter = KubeLinter()
    privileged_k8s = """
apiVersion: v1
kind: Pod
metadata:
  name: privileged-pod
spec:
  containers:
    - name: root-container
      image: "alpine:3.19"
      securityContext:
        privileged: true
"""
    result = linter.validate(privileged_k8s)
    assert result.passed is False
    assert "privileged-container" in result.error


def test_kube_linter_latest_image_tag():
    linter = KubeLinter()
    latest_k8s = """
apiVersion: v1
kind: Pod
metadata:
  name: latest-tag-pod
spec:
  containers:
    - name: web
      image: "nginx:latest"
"""
    result = linter.validate(latest_k8s)
    assert result.passed is False
    assert "no-latest-image-tag" in result.error


def test_helm_lint_linter_success():
    linter = HelmLintLinter()
    valid_chart_yaml = """
apiVersion: v2
name: my-app-chart
version: 1.0.0
description: Sample Helm Chart
"""
    result = linter.validate(valid_chart_yaml, file_path="Chart.yaml")
    assert result.passed is True
    assert result.check_name == "helm_lint"


def test_helm_lint_linter_missing_version():
    linter = HelmLintLinter()
    missing_version = """
apiVersion: v2
name: my-app-chart
"""
    result = linter.validate(missing_version, file_path="Chart.yaml")
    assert result.passed is False
    assert "missing required field 'version'" in result.error


def test_get_linters_for_iac_type():
    tf_linters = get_linters_for_iac_type(IaCType.TERRAFORM)
    assert len(tf_linters) == 2
    assert any(isinstance(l, TerraformValidateLinter) for l in tf_linters)
    assert any(isinstance(l, TflintLinter) for l in tf_linters)

    cfn_linters = get_linters_for_iac_type(IaCType.CLOUDFORMATION)
    assert len(cfn_linters) == 1
    assert isinstance(cfn_linters[0], CfnLintLinter)

    k8s_linters = get_linters_for_iac_type(IaCType.KUBERNETES)
    assert len(k8s_linters) == 1
    assert isinstance(k8s_linters[0], KubeLinter)

    helm_linters = get_linters_for_iac_type(IaCType.HELM)
    assert len(helm_linters) == 1
    assert isinstance(helm_linters[0], HelmLintLinter)


def test_linter_mock_override():
    linter = TerraformValidateLinter()
    mock_res = ValidationCheckResult(
        check_name="terraform_validate",
        passed=False,
        output="Mocked output",
        error="Mocked failure",
    )
    linter.set_mock_result(mock_res)
    res = linter.validate("resource \"valid\" \"valid\" {}")
    assert res.passed is False
    assert res.error == "Mocked failure"
