"""
Unit tests for multi-cloud IaC parsers.
"""

from agentshield.parsers import parse_terraform, parse_cloudformation, parse_kubernetes, parse_helm


def test_terraform_multicloud_and_deps(tmp_path):
    tf_file = tmp_path / "main.tf"
    tf_file.write_text('''
variable "bucket_name" {
  default = "my-bucket"
}

resource "aws_iam_role" "role" {
  name = "s3_role"
}

resource "aws_s3_bucket" "my_bucket" {
  bucket = var.bucket_name
  role   = aws_iam_role.role.arn
}

resource "azurerm_storage_account" "azure_store" {
  name = "storeacc"
}

resource "google_storage_bucket" "gcp_bucket" {
  name = "gcpbucket"
}
''')

    resources = parse_terraform(str(tf_file))
    assert len(resources) == 4

    aws_res = [r for r in resources if r.provider == "aws"]
    azure_res = [r for r in resources if r.provider == "azure"]
    gcp_res = [r for r in resources if r.provider == "gcp"]

    assert len(aws_res) == 2
    assert len(azure_res) == 1
    assert len(gcp_res) == 1

    bucket_res = next(r for r in resources if r.resource_name == "my_bucket")
    assert "aws_iam_role.role" in bucket_res.dependencies
    assert "bucket_name" in bucket_res.variables


def test_cloudformation_parser(tmp_path):
    cfn_file = tmp_path / "cfn.json"
    cfn_file.write_text('''{
      "Parameters": {"EnvName": {"Default": "prod"}},
      "Resources": {
        "MyRole": {"Type": "AWS::IAM::Role"},
        "MyBucket": {"Type": "AWS::S3::Bucket", "DependsOn": "MyRole"}
      }
    }''')

    resources = parse_cloudformation(str(cfn_file))
    assert len(resources) == 2

    bucket_res = next(r for r in resources if r.resource_name == "MyBucket")
    assert "MyRole" in bucket_res.dependencies
    assert "EnvName" in bucket_res.variables


def test_kubernetes_parser(tmp_path):
    k8s_file = tmp_path / "pod.yaml"
    k8s_file.write_text('apiVersion: v1\nkind: Pod\nmetadata:\n  name: test-pod')

    resources = parse_kubernetes(str(k8s_file))
    assert len(resources) == 1
    assert resources[0].resource_type == "k8s/Pod"
    assert resources[0].resource_name == "test-pod"


def test_helm_parser(tmp_path):
    helm_file = tmp_path / "chart.yaml"
    helm_file.write_text('apiVersion: v1\nkind: Service\nmetadata:\n  name: helm-service')

    resources = parse_helm(str(helm_file))
    assert len(resources) == 1
    assert resources[0].provider == "helm"
    assert resources[0].environment_context == "helm_chart"
