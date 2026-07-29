"""
Unit tests for Static Scanner Integration (Checkov, tfsec, KICS).
"""

from agentshield.utils.static_scanners import StaticScannerManager, enrich_ast_resources


def test_static_scanner_enrichment():
    sample_ast = [
        {
            "file_path": "main.tf",
            "resource_type": "aws_s3_bucket",
            "resource_name": "public_bucket",
            "provider": "aws",
            "line_start": 1,
            "line_end": 5,
            "attributes": {"raw_code": 'resource "aws_s3_bucket" "public_bucket" {\n  acl = "public-read"\n}'}
        }
    ]

    enriched = enrich_ast_resources(sample_ast)
    assert len(enriched) == 1

    attr = enriched[0]["attributes"]
    assert "static_scanner_enrichment" in attr

    enrichment = attr["static_scanner_enrichment"]
    assert "Checkov" in enrichment["scanners_evaluated"]
    assert "tfsec" in enrichment["scanners_evaluated"]
    assert "KICS" in enrichment["scanners_evaluated"]
    assert len(enrichment["failed_checks"]) > 0
