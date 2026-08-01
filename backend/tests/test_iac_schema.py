"""Tests for IaCTemplate and ASTNode Pydantic v2 schemas."""

import pytest
from pydantic import ValidationError

from agentshield.core.schemas.iac import ASTNode, IaCTemplate, IaCType, LineRange


def test_line_range_valid():
    lr = LineRange(start_line=5, end_line=15)
    assert lr.start_line == 5
    assert lr.end_line == 15


def test_line_range_invalid():
    with pytest.raises(ValidationError):
        LineRange(start_line=20, end_line=10)


def test_ast_node_traversal(sample_ast_root: ASTNode):
    resource_nodes = sample_ast_root.find_nodes_by_type("resource")
    assert len(resource_nodes) == 2
    assert {n.name for n in resource_nodes} == {"data_bucket", "app_role"}

    s3_nodes = sample_ast_root.find_resources_by_resource_type("aws_s3_bucket")
    assert len(s3_nodes) == 1
    assert s3_nodes[0].name == "data_bucket"


def test_iac_template_autodetect():
    tf_template = IaCTemplate(
        file_path="infra/main.tf", raw_content='resource "aws_s3_bucket" "b" {}'
    )
    assert tf_template.auto_detect_type() == IaCType.TERRAFORM

    cfn_content = "AWSTemplateFormatVersion: '2010-09-09'\nResources:"
    cfn_template = IaCTemplate(file_path="template.yaml", raw_content=cfn_content)
    assert cfn_template.auto_detect_type() == IaCType.CLOUDFORMATION

    k8s_content = "apiVersion: apps/v1\nkind: Deployment"
    k8s_template = IaCTemplate(file_path="deploy.yaml", raw_content=k8s_content)
    assert k8s_template.auto_detect_type() == IaCType.KUBERNETES

    helm_template = IaCTemplate(file_path="chart/Chart.yaml", raw_content="name: my-chart")
    assert helm_template.auto_detect_type() == IaCType.HELM
