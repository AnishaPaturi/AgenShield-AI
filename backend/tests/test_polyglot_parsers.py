from pathlib import Path
import tempfile
import pytest

from agentshield.parsers import (
    autodetect_template_format,
    extract_cloudformation_resources,
    extract_helm_resources,
    extract_kubernetes_resources,
    parse_cloudformation_file,
    parse_iac_template,
    parse_kubernetes_file,
)


def test_cloudformation_parser():
    yaml_content = """
    AWSTemplateFormatVersion: '2010-09-09'
    Description: Sample S3 and Security Group
    Resources:
      AppBucket:
        Type: AWS::S3::Bucket
        Properties:
          BucketName: my-cfn-bucket
          AccessControl: PublicRead
      AppSG:
        Type: AWS::EC2::SecurityGroup
        Properties:
          GroupDescription: SSH Access
    """
    with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False) as tmp:
        tmp.write(yaml_content)
        tmp_path = tmp.name

    try:
        fmt = autodetect_template_format(tmp_path)
        assert fmt == "cloudformation"

        parsed = parse_cloudformation_file(tmp_path)
        assert "Resources" in parsed

        resources = extract_cloudformation_resources(parsed)
        assert len(resources) == 2
        assert resources[0]["resource_type"] == "AWS::S3::Bucket"
        assert resources[0]["resource_name"] == "AppBucket"
        assert resources[1]["resource_type"] == "AWS::EC2::SecurityGroup"

        # Test unified dispatcher
        dispatched_res = parse_iac_template(tmp_path)
        assert len(dispatched_res) == 2
    finally:
        Path(tmp_path).unlink(missing_ok=True)


def test_kubernetes_parser():
    k8s_content = """
apiVersion: v1
kind: Pod
metadata:
  name: test-pod
  namespace: prod
spec:
  containers:
  - name: nginx
    image: nginx:latest
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-deployment
spec:
  replicas: 3
    """
    with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False) as tmp:
        tmp.write(k8s_content)
        tmp_path = tmp.name

    try:
        fmt = autodetect_template_format(tmp_path)
        assert fmt == "kubernetes"

        docs = parse_kubernetes_file(tmp_path)
        assert len(docs) == 2

        resources = extract_kubernetes_resources(docs)
        assert len(resources) == 2
        assert resources[0]["resource_id"] == "k8s.Pod.test-pod"
        assert resources[0]["kind"] == "Pod"
        assert resources[0]["namespace"] == "prod"
        assert resources[1]["kind"] == "Deployment"

        # Test unified dispatcher
        dispatched_res = parse_iac_template(tmp_path)
        assert len(dispatched_res) == 2
    finally:
        Path(tmp_path).unlink(missing_ok=True)


def test_helm_parser():
    values_content = """
    replicaCount: 2
    image:
      repository: nginx
      tag: stable
    service:
      type: ClusterIP
      port: 80
    """
    with tempfile.NamedTemporaryFile("w", prefix="values", suffix=".yaml", delete=False) as tmp:
        tmp.write(values_content)
        tmp_path = tmp.name

    try:
        fmt = autodetect_template_format(tmp_path)
        assert fmt == "helm"

        resources = parse_iac_template(tmp_path, template_format="helm")
        assert len(resources) >= 1
        assert resources[0]["resource_type"] == "helm/values"
        assert resources[0]["properties"]["replicaCount"] == 2
    finally:
        Path(tmp_path).unlink(missing_ok=True)
