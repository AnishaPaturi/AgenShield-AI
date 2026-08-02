import pytest

from agentshield.core.schemas.vulnerability import Severity
from agentshield.scanners.static_adapters import (
    CheckovAdapter,
    KicsAdapter,
    StaticScannerRegistry,
    TfsecAdapter,
)


def test_checkov_adapter_parse():
    mock_checkov_json = {
        "results": {
            "failed_checks": [
                {
                    "check_id": "CKV_AWS_20",
                    "check_name": "Ensure S3 bucket does not allow public read access",
                    "check_result": {"result": "FAILED"},
                    "resource": "aws_s3_bucket.my_bucket",
                    "file_line_range": [10, 15],
                    "guideline": "https://docs.bridgecrew.io/docs/aws_20",
                    "severity": "HIGH",
                }
            ]
        }
    }

    adapter = CheckovAdapter()
    findings = adapter.parse_json_report(mock_checkov_json)

    assert len(findings) == 1
    f = findings[0]
    assert f.rule_id == "CKV_AWS_20"
    assert "S3 bucket" in f.title
    assert f.severity == Severity.HIGH
    assert f.affected_resource == "aws_s3_bucket.my_bucket"


def test_tfsec_adapter_parse():
    mock_tfsec_json = {
        "results": [
            {
                "rule_id": "AWS002",
                "rule_description": "S3 bucket does not have logging enabled",
                "severity": "MEDIUM",
                "resource": "aws_s3_bucket.app_data",
                "location": {"start_line": 20, "end_line": 25},
                "resolution": "Add a logging block to the S3 bucket resource.",
            }
        ]
    }

    adapter = TfsecAdapter()
    findings = adapter.parse_json_report(mock_tfsec_json)

    assert len(findings) == 1
    f = findings[0]
    assert f.rule_id == "AWS002"
    assert f.affected_resource == "aws_s3_bucket.app_data"


def test_kics_adapter_parse():
    mock_kics_json = {
        "queries": [
            {
                "query_id": "kics_q100",
                "query_name": "Unencrypted Storage Volume",
                "severity": "HIGH",
                "description": "EBS Volume is unencrypted",
                "files": [
                    {
                        "file_name": "ebs.tf",
                        "resource_name": "aws_ebs_volume.storage",
                        "line": 8,
                    }
                ],
            }
        ]
    }

    adapter = KicsAdapter()
    findings = adapter.parse_json_report(mock_kics_json)

    assert len(findings) == 1
    f = findings[0]
    assert f.rule_id == "kics_q100"
    assert f.severity == Severity.HIGH


def test_static_scanner_registry():
    registry = StaticScannerRegistry()

    checkov_sample = {"results": {"failed_checks": [{"check_id": "CKV_1", "resource": "res1"}]}}
    tfsec_sample = {"results": [{"rule_id": "TF1", "resource": "res2"}]}

    all_findings = registry.parse_reports(checkov_data=checkov_sample, tfsec_data=tfsec_sample)

    assert len(all_findings) == 2
    rule_ids = [f.rule_id for f in all_findings]
    assert "CKV_1" in rule_ids
    assert "TF1" in rule_ids
