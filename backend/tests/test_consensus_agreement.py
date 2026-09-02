"""Tests for mathematical agreement scoring (Task 3.2)."""

import pytest

from agentshield.core.consensus import (
    compute_agreement,
    interval_jaccard,
    jaccard,
    location_agreement,
    normalize_resource,
    normalize_rule_id,
    resource_agreement,
    semantic_agreement,
    severity_agreement,
    severity_distance,
    text_similarity,
    tokenize,
)
from agentshield.core.schemas import LineRange, Severity, VulnerabilityFinding


def _finding(**overrides) -> VulnerabilityFinding:
    payload = {
        "rule_id": "AS-AWS-001",
        "title": "Public S3 Bucket",
        "description": "Bucket grants public read access.",
        "severity": Severity.HIGH,
        "confidence_score": 0.9,
        "affected_resource": "aws_s3_bucket.data_bucket",
    }
    payload.update(overrides)
    return VulnerabilityFinding(**payload)


# --------------------------------------------------------------------------
# Normalization primitives
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("aws_s3_bucket.data_bucket", "aws_s3_bucket.data_bucket"),
        ("resource.aws_s3_bucket.data_bucket", "aws_s3_bucket.data_bucket"),
        ('"aws_s3_bucket.data_bucket"', "aws_s3_bucket.data_bucket"),
        ("aws_s3_bucket/data_bucket", "aws_s3_bucket.data_bucket"),
        ("AWS_S3_BUCKET.Data_Bucket", "aws_s3_bucket.data_bucket"),
        ("module.storage.aws_s3_bucket.data_bucket", "aws_s3_bucket.data_bucket"),
    ],
)
def test_normalize_resource_collapses_spellings(raw: str, expected: str):
    assert normalize_resource(raw) == expected


def test_normalize_resource_handles_empty():
    assert normalize_resource("   ") == ""


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("CKV_AWS_20", "AWS20"),
        ("ckv_aws_20", "AWS20"),
        ("AS-AWS-001", "001"),
        ("CKV2_AWS_1", "AWS1"),
    ],
)
def test_normalize_rule_id_strips_vendor_prefix(raw: str, expected: str):
    assert normalize_rule_id(raw) == expected


def test_normalize_rule_id_keeps_prefix_only_ids():
    # Stripping must not annihilate an identifier down to the empty string.
    assert normalize_rule_id("AS") == "AS"


def test_tokenize_drops_stopwords_and_short_tokens():
    tokens = tokenize("The S3 bucket is a public security risk")
    assert "bucket" in tokens
    assert "public" in tokens
    # Stopwords and <=2 char tokens are discarded.
    assert "the" not in tokens
    assert "is" not in tokens
    assert "s3" not in tokens
    assert "security" not in tokens
    assert "risk" not in tokens


def test_jaccard_edge_cases():
    assert jaccard(set(), set()) == 1.0
    assert jaccard({"a"}, {"a"}) == 1.0
    assert jaccard({"a"}, {"b"}) == 0.0
    assert jaccard({"a", "b"}, {"b", "c"}) == pytest.approx(1 / 3)


def test_text_similarity_is_symmetric_and_bounded():
    left = "S3 bucket allows public read access to objects"
    right = "Bucket grants public read access to all objects"
    score = text_similarity(left, right)
    assert 0.0 < score < 1.0
    assert score == pytest.approx(text_similarity(right, left))


def test_severity_distance_ordinal():
    assert severity_distance(Severity.HIGH, Severity.HIGH) == 0
    assert severity_distance(Severity.HIGH, Severity.CRITICAL) == 1
    assert severity_distance(Severity.CRITICAL, Severity.INFORMATIONAL) == 4


def test_interval_jaccard_overlap():
    assert interval_jaccard((10, 20), (10, 20)) == 1.0
    assert interval_jaccard((10, 20), (30, 40)) == 0.0
    # Intersection 11..20 (10 lines), union 10..25 (16 lines).
    assert interval_jaccard((10, 20), (11, 25)) == pytest.approx(10 / 16)


# --------------------------------------------------------------------------
# Individual agreement signals
# --------------------------------------------------------------------------


def test_severity_agreement_full_and_partial():
    identical = [_finding(), _finding()]
    assert severity_agreement(identical) == 1.0

    # One level apart out of a maximum distance of 4.
    adjacent = [_finding(severity=Severity.HIGH), _finding(severity=Severity.CRITICAL)]
    assert severity_agreement(adjacent) == pytest.approx(0.75)

    opposed = [
        _finding(severity=Severity.CRITICAL),
        _finding(severity=Severity.INFORMATIONAL),
    ]
    assert severity_agreement(opposed) == 0.0


def test_resource_agreement_uses_normalized_identity():
    same = [
        _finding(affected_resource="aws_s3_bucket.data_bucket"),
        _finding(affected_resource="resource.aws_s3_bucket.data_bucket"),
    ]
    assert resource_agreement(same) == 1.0

    different = [
        _finding(affected_resource="aws_s3_bucket.data_bucket"),
        _finding(affected_resource="aws_db_instance.app_db"),
    ]
    assert resource_agreement(different) == 0.0


def test_semantic_agreement_rewards_shared_vocabulary():
    aligned = [
        _finding(title="Public bucket", description="Bucket grants public read access"),
        _finding(title="Public bucket", description="Bucket grants public read access"),
    ]
    assert semantic_agreement(aligned) == 1.0

    unrelated = [
        _finding(title="Public bucket", description="Bucket grants public read access"),
        _finding(title="Unencrypted volume", description="EBS volume lacks kms key"),
    ]
    assert semantic_agreement(unrelated) == 0.0


def test_location_agreement_is_none_when_ranges_missing():
    partial = [
        _finding(line_range=LineRange(start_line=10, end_line=20)),
        _finding(line_range=None),
    ]
    # Not measurable -> excluded from the weighted mean rather than defaulted.
    assert location_agreement(partial) is None


def test_location_agreement_measures_overlap():
    findings = [
        _finding(line_range=LineRange(start_line=10, end_line=20)),
        _finding(line_range=LineRange(start_line=11, end_line=25)),
    ]
    assert location_agreement(findings) == pytest.approx(10 / 16)


# --------------------------------------------------------------------------
# Composite agreement
# --------------------------------------------------------------------------


def test_compute_agreement_identical_findings_is_one():
    breakdown = compute_agreement([_finding(), _finding()])
    assert breakdown.score == 1.0
    assert breakdown.model_count == 2
    assert breakdown.signals["severity"] == 1.0
    assert breakdown.signals["resource"] == 1.0
    assert breakdown.signals["semantic"] == 1.0
    # No line ranges were supplied, so location must be absent.
    assert "location" not in breakdown.signals


def test_compute_agreement_excludes_unmeasurable_signals_from_weights():
    breakdown = compute_agreement([_finding(), _finding()])
    # Active weights renormalize to 1.0 across the three measurable signals.
    assert sum(breakdown.weights.values()) == pytest.approx(1.0)
    assert set(breakdown.weights) == {"severity", "resource", "semantic"}


def test_compute_agreement_includes_location_when_available():
    findings = [
        _finding(line_range=LineRange(start_line=10, end_line=20)),
        _finding(line_range=LineRange(start_line=10, end_line=20)),
    ]
    breakdown = compute_agreement(findings)
    assert breakdown.signals["location"] == 1.0
    assert sum(breakdown.weights.values()) == pytest.approx(1.0)
    assert breakdown.score == 1.0


def test_compute_agreement_penalizes_disagreement():
    findings = [
        _finding(severity=Severity.CRITICAL, description="Bucket grants public read"),
        _finding(severity=Severity.LOW, description="EBS volume lacks kms encryption"),
    ]
    breakdown = compute_agreement(findings)
    assert 0.0 < breakdown.score < 0.6


def test_compute_agreement_singleton_is_vacuously_one():
    """A lone finding has no cross-model evidence; the hallucination penalty
    is applied by the N_agreed/N_total term, not by the agreement score."""
    breakdown = compute_agreement([_finding()])
    assert breakdown.score == 1.0
    assert breakdown.model_count == 1
    assert breakdown.signals == {}


def test_agreement_breakdown_is_serializable():
    payload = compute_agreement([_finding(), _finding()]).as_dict()
    assert payload["score"] == 1.0
    assert payload["model_count"] == 2
    assert isinstance(payload["signals"], dict)
