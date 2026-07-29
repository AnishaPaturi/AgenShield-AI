"""
Unit tests for multi-cloud IaC parsers.
"""

from agentshield.parsers import parse_terraform, parse_cloudformation, parse_kubernetes


def test_terraform_parser(tmp_path):
    tf_file = tmp_path / "main.tf"
    tf_file.write_text('resource "aws_s3_bucket" "my_bucket" {\n  acl = "public-read"\n}')

    resources = parse_terraform(str(tf_file))
    assert len(resources) == 1
    assert resources[0].resource_type == "aws_s3_bucket"
    assert resources[0].resource_name == "my_bucket"


def test_cloudformation_parser(tmp_path):
    cfn_file = tmp_path / "cfn.json"
    cfn_file.write_text('{"Resources": {"MyBucket": {"Type": "AWS::S3::Bucket"}}}')

    resources = parse_cloudformation(str(cfn_file))
    assert len(resources) == 1
    assert resources[0].resource_type == "AWS::S3::Bucket"
    assert resources[0].resource_name == "MyBucket"


def test_kubernetes_parser(tmp_path):
    k8s_file = tmp_path / "pod.yaml"
    k8s_file.write_text('apiVersion: v1\nkind: Pod\nmetadata:\n  name: test-pod')

    resources = parse_kubernetes(str(k8s_file))
    assert len(resources) == 1
    assert resources[0].resource_type == "k8s/Pod"
    assert resources[0].resource_name == "test-pod"
