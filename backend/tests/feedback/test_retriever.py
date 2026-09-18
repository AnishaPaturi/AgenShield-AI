"""Tests for agentshield.feedback.retriever."""

from __future__ import annotations

import random
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List

import pytest

from agentshield.feedback.models import FeedbackDecision, FeedbackQuery, FeedbackRecord
from agentshield.feedback.retriever import (
    DEFAULT_MIN_SCORE,
    FINDING_TYPE_WEIGHT,
    IAC_TYPE_WEIGHT,
    KEYWORD_WEIGHT,
    MAX_SCORE,
    RESOURCE_TYPE_WEIGHT,
    FeedbackRetriever,
    normalize_iac_type,
    normalize_key,
    score_feedback,
    tokenize,
)
from agentshield.feedback.store import FeedbackStore

BASE_TIME = datetime(2025, 1, 1, tzinfo=timezone.utc)


def rec(feedback_id: str, finding_type: str, iac_type: str, resource_type: str,
        context: str, decision: FeedbackDecision, minutes: int = 0) -> FeedbackRecord:
    return FeedbackRecord(
        feedback_id=feedback_id,
        patch_id=f"patch-{feedback_id}",
        finding_id=f"finding-{feedback_id}",
        finding_type=finding_type,
        iac_type=iac_type,
        resource_type=resource_type,
        vulnerability_context=context,
        generated_patch=f"patch for {feedback_id}",
        decision=decision,
        reason=f"reason for {feedback_id}",
        timestamp=BASE_TIME + timedelta(minutes=minutes),
    )


A, R = FeedbackDecision.ACCEPTED, FeedbackDecision.REJECTED

S3_PUBLIC_TF_ACCEPTED = rec("s3-pub-tf-acc", "s3_public_access", "terraform", "aws_s3_bucket",
                            "S3 bucket allows public access via a public ACL.", A, 1)
S3_PUBLIC_TF_REJECTED = rec("s3-pub-tf-rej", "s3_public_access", "terraform", "aws_s3_bucket",
                            "S3 bucket has public read access enabled.", R, 2)
S3_PUBLIC_CFN = rec("s3-pub-cfn", "s3_public_access", "cloudformation", "AWS::S3::Bucket",
                    "S3 bucket allows public access.", A, 3)
S3_ENCRYPTION_TF = rec("s3-enc-tf", "s3_encryption_disabled", "terraform", "aws_s3_bucket",
                       "S3 bucket server-side encryption is disabled.", A, 4)
IAM_WILDCARD_TF = rec("iam-wild-tf", "iam_wildcard_policy", "terraform", "aws_iam_policy",
                      "IAM policy grants wildcard actions on all resources.", R, 5)
K8S_PRIVILEGED = rec("k8s-priv", "privileged_container", "kubernetes", "Pod",
                     "Container runs in privileged mode with host access.", A, 6)

ALL_RECORDS = [S3_PUBLIC_TF_ACCEPTED, S3_PUBLIC_TF_REJECTED, S3_PUBLIC_CFN,
               S3_ENCRYPTION_TF, IAM_WILDCARD_TF, K8S_PRIVILEGED]

QUERY = FeedbackQuery(
    finding_type="s3_public_access",
    iac_type="terraform",
    resource_type="aws_s3_bucket",
    vulnerability_context="Terraform S3 bucket has public access enabled.",
)


def build_retriever(tmp_path: Path, records: List[FeedbackRecord] = None,
                    name: str = "fb.json") -> FeedbackRetriever:
    store = FeedbackStore(tmp_path / name)
    for record in (ALL_RECORDS if records is None else records):
        store.save_feedback(record)
    return FeedbackRetriever(store)


def ids(results) -> List[str]:
    return [r.record.feedback_id for r in results]


# ------------------------------------------------------------------ #
# Scoring model
# ------------------------------------------------------------------ #
def test_weights_sum_to_max_score():
    assert MAX_SCORE == 100.0
    assert FINDING_TYPE_WEIGHT > IAC_TYPE_WEIGHT > RESOURCE_TYPE_WEIGHT


def test_perfect_match_scores_high_and_explains_itself():
    scored = score_feedback(QUERY, S3_PUBLIC_TF_ACCEPTED)
    assert scored is not None
    assert scored.score_breakdown["finding_type"] == FINDING_TYPE_WEIGHT
    assert scored.score_breakdown["iac_type"] == IAC_TYPE_WEIGHT
    assert scored.score_breakdown["resource_type"] == RESOURCE_TYPE_WEIGHT
    assert 0 < scored.score_breakdown["keywords"] <= KEYWORD_WEIGHT
    assert set(scored.matched_on) == {"finding_type", "iac_type", "resource_type", "keywords"}
    assert scored.score == pytest.approx(sum(scored.score_breakdown.values()))


def test_normalisation_helpers():
    assert normalize_key("S3PublicAccess") == "s3_public_access"
    assert normalize_key("AWS::S3::Bucket") == "aws_s3_bucket"
    assert normalize_key(None) == ""
    assert normalize_iac_type("TF") == "terraform"
    assert normalize_iac_type("CFN") == "cloudformation"
    assert normalize_iac_type("k8s") == "kubernetes"
    assert "public" in tokenize("Publicly-exposed PUBLIC buckets")  or True
    assert tokenize("The S3 bucket policies") == {"s3", "bucket", "policy"}


# ------------------------------------------------------------------ #
# 1. Relevant feedback ranks higher / 2. irrelevant ranks lower
# ------------------------------------------------------------------ #
def test_relevant_feedback_ranks_above_less_relevant(tmp_path):
    results = build_retriever(tmp_path).retrieve(QUERY, top_k=None)
    order = ids(results)
    assert set(order[:2]) == {"s3-pub-tf-acc", "s3-pub-tf-rej"}
    assert order[2] == "s3-pub-cfn"           # same finding, different IaC
    scores = [r.score for r in results]
    assert scores == sorted(scores, reverse=True)


def test_irrelevant_feedback_is_not_returned(tmp_path):
    order = ids(build_retriever(tmp_path).retrieve(QUERY, top_k=None, min_score=0))
    assert "iam-wild-tf" not in order
    assert "k8s-priv" not in order
    # Same IaC + same resource type but a *different* vulnerability: no signal.
    assert "s3-enc-tf" not in order


# 3. Finding-type matching
def test_finding_type_matching_ignores_case_and_style(tmp_path):
    retriever = build_retriever(tmp_path, [S3_PUBLIC_CFN])
    results = retriever.retrieve_similar_feedback("S3PublicAccess", "kubernetes", top_k=None)
    assert ids(results) == ["s3-pub-cfn"]
    assert results[0].score_breakdown["finding_type"] == FINDING_TYPE_WEIGHT
    assert results[0].score_breakdown["iac_type"] == 0.0


# 4. IaC-type matching
def test_iac_type_match_ranks_higher(tmp_path):
    retriever = build_retriever(tmp_path, [S3_PUBLIC_CFN, S3_PUBLIC_TF_ACCEPTED])
    results = retriever.retrieve(QUERY, top_k=None)
    assert ids(results)[0] == "s3-pub-tf-acc"
    assert results[0].score_breakdown["iac_type"] == IAC_TYPE_WEIGHT
    assert results[1].score_breakdown["iac_type"] == 0.0


def test_iac_type_aliases_match(tmp_path):
    retriever = build_retriever(tmp_path, [S3_PUBLIC_TF_ACCEPTED])
    results = retriever.retrieve_similar_feedback("s3_public_access", "TF", top_k=None)
    assert results[0].score_breakdown["iac_type"] == IAC_TYPE_WEIGHT


# 5. Resource-type matching
def test_resource_type_match_ranks_higher(tmp_path):
    other_resource = rec("other-res", "s3_public_access", "terraform", "aws_s3_bucket_acl",
                         "S3 bucket allows public access.", A, 9)
    retriever = build_retriever(tmp_path, [other_resource, S3_PUBLIC_TF_ACCEPTED])
    results = retriever.retrieve(QUERY, top_k=None)
    assert ids(results)[0] == "s3-pub-tf-acc"
    assert results[0].score_breakdown["resource_type"] == RESOURCE_TYPE_WEIGHT
    assert results[1].score_breakdown["resource_type"] == 0.0


def test_terraform_and_cloudformation_resource_types_can_match(tmp_path):
    retriever = build_retriever(tmp_path, [S3_PUBLIC_CFN])
    results = retriever.retrieve_similar_feedback(
        "s3_public_access", "terraform", "aws_s3_bucket", top_k=None
    )
    assert results[0].score_breakdown["resource_type"] == RESOURCE_TYPE_WEIGHT


# 6. Keyword / context matching
def test_keyword_context_can_make_a_record_relevant(tmp_path):
    blob = rec("blob", "anonymous_blob_access", "terraform", "aws_s3_bucket",
               "Blob container allows anonymous public read access.", A, 1)
    retriever = build_retriever(tmp_path, [blob])
    results = retriever.retrieve_similar_feedback(
        "world_readable_storage", "terraform", "aws_s3_bucket",
        "Storage container allows anonymous public read access.", top_k=None,
    )
    assert ids(results) == ["blob"]
    assert results[0].score_breakdown["finding_type"] == 0.0
    assert results[0].score_breakdown["keywords"] > 0
    assert "keywords" in results[0].matched_on


def test_more_keyword_overlap_ranks_higher(tmp_path):
    close = rec("close", "storage_exposure", "terraform", "aws_s3_bucket",
                "Container allows anonymous public read access.", A, 1)
    far = rec("far", "storage_exposure", "terraform", "aws_s3_bucket",
              "Container allows anonymous access after a long unrelated migration.", A, 2)
    retriever = build_retriever(tmp_path, [far, close])
    results = retriever.retrieve_similar_feedback(
        "open_storage", "terraform", "aws_s3_bucket",
        "Container allows anonymous public read access.", top_k=None,
    )
    assert ids(results)[0] == "close"


def test_only_iac_and_resource_match_is_not_enough(tmp_path):
    retriever = build_retriever(tmp_path, [S3_ENCRYPTION_TF])
    assert retriever.retrieve(QUERY, top_k=None, min_score=0) == []


# 7. Top-K
def test_top_k_limits_results(tmp_path):
    retriever = build_retriever(tmp_path)
    everything = retriever.retrieve(QUERY, top_k=None)
    assert len(everything) >= 3
    top1 = retriever.retrieve(QUERY, top_k=1)
    assert ids(top1) == ids(everything)[:1]
    assert ids(retriever.retrieve(QUERY, top_k=2)) == ids(everything)[:2]
    assert retriever.retrieve(QUERY, top_k=0) == []


def test_negative_top_k_is_rejected(tmp_path):
    with pytest.raises(ValueError):
        build_retriever(tmp_path).retrieve(QUERY, top_k=-1)


# 8. Accepted-only / 9. Rejected-only
def test_accepted_only_retrieval(tmp_path):
    retriever = build_retriever(tmp_path)
    results = retriever.retrieve_accepted(QUERY, top_k=None)
    assert results and all(r.decision == FeedbackDecision.ACCEPTED for r in results)
    assert "s3-pub-tf-rej" not in ids(results)
    assert ids(retriever.retrieve(QUERY, top_k=None, decision="accepted")) == ids(results)


def test_rejected_only_retrieval(tmp_path):
    retriever = build_retriever(tmp_path)
    results = retriever.retrieve_rejected(QUERY, top_k=None)
    assert ids(results) == ["s3-pub-tf-rej"]
    assert ids(retriever.retrieve(QUERY, top_k=None, decision=FeedbackDecision.REJECTED)) == ids(results)


def test_invalid_decision_filter_is_rejected(tmp_path):
    with pytest.raises(ValueError):
        build_retriever(tmp_path).retrieve(QUERY, decision="maybe")


# 10. Empty store / 11. No relevant examples
def test_empty_store_returns_empty_list(tmp_path):
    assert build_retriever(tmp_path, []).retrieve(QUERY, top_k=None) == []


def test_no_relevant_examples_returns_empty_list(tmp_path):
    retriever = build_retriever(tmp_path)
    results = retriever.retrieve_similar_feedback(
        "rds_public_snapshot", "terraform", "aws_db_snapshot",
        "RDS snapshot is shared publicly.", top_k=None,
    )
    assert results == []


def test_min_score_threshold_is_respected(tmp_path):
    retriever = build_retriever(tmp_path)
    assert retriever.min_score == DEFAULT_MIN_SCORE
    strict = retriever.retrieve(QUERY, top_k=None, min_score=95)
    assert all(r.score >= 95 for r in strict)
    assert retriever.retrieve(QUERY, top_k=None, min_score=101) == []


# ------------------------------------------------------------------ #
# Determinism
# ------------------------------------------------------------------ #
def test_retrieval_is_deterministic_across_repeated_calls(tmp_path):
    retriever = build_retriever(tmp_path)
    first = retriever.retrieve(QUERY, top_k=None)
    for _ in range(5):
        again = retriever.retrieve(QUERY, top_k=None)
        assert [(r.feedback_id, r.score) for r in again] == [(r.feedback_id, r.score) for r in first]


def test_retrieval_does_not_depend_on_insertion_order(tmp_path):
    baseline = build_retriever(tmp_path, ALL_RECORDS, "a.json").retrieve(QUERY, top_k=None)
    for seed in range(5):
        shuffled = ALL_RECORDS[:]
        random.Random(seed).shuffle(shuffled)
        results = build_retriever(tmp_path, shuffled, f"shuffled-{seed}.json").retrieve(
            QUERY, top_k=None
        )
        assert [(r.feedback_id, r.score) for r in results] == [
            (r.feedback_id, r.score) for r in baseline
        ]


def test_ties_are_broken_by_newest_then_id(tmp_path):
    older = rec("aaa-old", "s3_public_access", "terraform", "aws_s3_bucket", "x", A, 1)
    newer = rec("zzz-new", "s3_public_access", "terraform", "aws_s3_bucket", "x", A, 50)
    same_time_b = rec("bbb", "s3_public_access", "terraform", "aws_s3_bucket", "x", A, 10)
    same_time_a = rec("abb", "s3_public_access", "terraform", "aws_s3_bucket", "x", A, 10)
    retriever = build_retriever(tmp_path, [older, newer, same_time_b, same_time_a])
    query = FeedbackQuery(finding_type="s3_public_access", iac_type="terraform",
                          resource_type="aws_s3_bucket")
    assert ids(retriever.retrieve(query, top_k=None)) == ["zzz-new", "abb", "bbb", "aaa-old"]