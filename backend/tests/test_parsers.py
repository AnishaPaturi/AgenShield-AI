import os
from agentshield.parsers import parse_cfn_file, parse_k8s_file, ParsedResource

def test_parse_cfn_file_success():
    target_path = "./infrastructure/cloudformation/s3_bucket.json"
    assert os.path.exists(target_path)
    
    resources = parse_cfn_file(target_path)
    
    assert isinstance(resources, list)
    assert len(resources) == 1
    
    res = resources[0]
    assert isinstance(res, ParsedResource)
    assert res.resource_id == "VulnerableS3Bucket"
    assert res.resource_type == "AWS::S3::Bucket"
    assert res.cloud_provider == "aws"
    assert res.iac_format == "cloudformation"
    assert res.properties["AccessControl"] == "PublicRead"
    assert res.properties["BucketName"] == "agentshield-cfn-vulnerable-bucket"
    assert "__start_line__" not in res.properties
    
    # Verify line range and snippet
    assert res.line_range is not None
    assert len(res.line_range) == 2
    assert res.line_range[0] < res.line_range[1]
    assert "Type" in res.raw_snippet
    assert "VulnerableS3Bucket" in res.raw_snippet

def test_parse_k8s_file_success():
    target_path = "./infrastructure/kubernetes/pod_root.yaml"
    assert os.path.exists(target_path)
    
    resources = parse_k8s_file(target_path)
    
    assert isinstance(resources, list)
    assert len(resources) == 2
    
    # Resource 1: privileged-pod
    res1 = resources[0]
    assert isinstance(res1, ParsedResource)
    assert res1.resource_id == "privileged-pod"
    assert res1.resource_type == "Pod"
    assert res1.cloud_provider == "k8s"
    assert res1.iac_format == "kubernetes"
    assert res1.properties["spec"]["containers"][0]["securityContext"]["privileged"] is True
    assert "__start_line__" not in res1.properties
    assert res1.line_range is not None
    assert "privileged-pod" in res1.raw_snippet

    # Resource 2: safe-pod
    res2 = resources[1]
    assert isinstance(res2, ParsedResource)
    assert res2.resource_id == "safe-pod"
    assert res2.resource_type == "Pod"
    assert res2.cloud_provider == "k8s"
    assert res2.iac_format == "kubernetes"
    assert res2.properties["spec"]["containers"][0]["securityContext"]["runAsNonRoot"] is True
    assert "__start_line__" not in res2.properties
    assert res2.line_range is not None
    assert "safe-pod" in res2.raw_snippet
