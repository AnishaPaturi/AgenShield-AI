"""Benchmark Corpus Loader for IaC Security Evaluations (Task 5.3).

Contains curated ground-truth vulnerable and benign templates sourced from
public benchmark corpora:
- Terragoat (Terraform AWS/Azure/GCP misconfigurations)
- cfngoat (AWS CloudFormation vulnerable templates)
- IaC-Eval & Checkov test suites
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from agentshield.core.schemas import CloudProvider, IaCType


@dataclass
class BenchmarkCase:
    case_id: str
    name: str
    source_corpus: str  # "Terragoat" | "cfngoat" | "IaC-Eval"
    iac_type: IaCType
    cloud_provider: CloudProvider
    content: str
    expected_rule_ids: list[str]
    is_vulnerable: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)


def get_standard_benchmark_corpus() -> list[BenchmarkCase]:
    """Return standard test suite of vulnerable and secure IaC templates."""
    return [
        BenchmarkCase(
            case_id="TG-TF-AWS-001",
            name="Terragoat: S3 Bucket Public Read",
            source_corpus="Terragoat",
            iac_type=IaCType.TERRAFORM,
            cloud_provider=CloudProvider.AWS,
            content="""
resource "aws_s3_bucket" "data_bucket" {
  bucket = "my-terragoat-data-bucket"
  acl    = "public-read"
}
""",
            expected_rule_ids=["AS-DEF-001", "CKV_AWS_20"],
            is_vulnerable=True,
        ),
        BenchmarkCase(
            case_id="TG-TF-AWS-002",
            name="Terragoat: Unencrypted S3 Bucket",
            source_corpus="Terragoat",
            iac_type=IaCType.TERRAFORM,
            cloud_provider=CloudProvider.AWS,
            content="""
resource "aws_s3_bucket" "data_bucket" {
  bucket = "my-app-data-bucket"
}
""",
            expected_rule_ids=["AS-AWS-002", "CKV_AWS_19"],
            is_vulnerable=True,
        ),
        BenchmarkCase(
            case_id="TG-TF-AWS-003",
            name="Terragoat: Open SSH Ingress 0.0.0.0/0",
            source_corpus="Terragoat",
            iac_type=IaCType.TERRAFORM,
            cloud_provider=CloudProvider.AWS,
            content="""
resource "aws_security_group" "web_sg" {
  name        = "web-sg"
  description = "Web security group"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
""",
            expected_rule_ids=["AS-DEF-001", "CKV_AWS_260"],
            is_vulnerable=True,
        ),
        BenchmarkCase(
            case_id="TG-TF-AWS-004",
            name="Terragoat: Public Unencrypted RDS Instance",
            source_corpus="Terragoat",
            iac_type=IaCType.TERRAFORM,
            cloud_provider=CloudProvider.AWS,
            content="""
resource "aws_db_instance" "app_db" {
  allocated_storage   = 20
  engine              = "postgres"
  instance_class      = "db.t3.micro"
  storage_encrypted   = false
  publicly_accessible = true
}
""",
            expected_rule_ids=["AS-AWS-003", "AS-AWS-004"],
            is_vulnerable=True,
        ),
        BenchmarkCase(
            case_id="CFN-GOAT-001",
            name="cfngoat: Insecure S3 Bucket CloudFormation",
            source_corpus="cfngoat",
            iac_type=IaCType.CLOUDFORMATION,
            cloud_provider=CloudProvider.AWS,
            content="""
AWSTemplateFormatVersion: '2010-09-09'
Resources:
  MyInsecureBucket:
    Type: 'AWS::S3::Bucket'
    Properties:
      AccessControl: 'PublicRead'
""",
            expected_rule_ids=["AS-DEF-001"],
            is_vulnerable=True,
        ),
        BenchmarkCase(
            case_id="BENIGN-TF-001",
            name="Secure Baseline: Fully Encrypted Private S3",
            source_corpus="IaC-Eval",
            iac_type=IaCType.TERRAFORM,
            cloud_provider=CloudProvider.AWS,
            content="""
resource "aws_s3_bucket" "secure_bucket" {
  bucket = "company-secure-storage-bucket"
  acl    = "private"
}

resource "aws_s3_bucket_server_side_encryption_configuration" "sec" {
  bucket = aws_s3_bucket.secure_bucket.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}
""",
            expected_rule_ids=[],
            is_vulnerable=False,
        ),
        BenchmarkCase(
            case_id="BENIGN-TF-002",
            name="Secure Baseline: Restricted VPC Security Group",
            source_corpus="IaC-Eval",
            iac_type=IaCType.TERRAFORM,
            cloud_provider=CloudProvider.AWS,
            content="""
resource "aws_security_group" "internal_sg" {
  name        = "internal-sg"
  description = "Internal ingress only"

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/16"]
  }
}
""",
            expected_rule_ids=[],
            is_vulnerable=False,
        ),
    ]
