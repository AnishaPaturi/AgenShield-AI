"""Tests for agentshield.feedback.models."""

from __future__ import annotations

import json
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from agentshield.feedback.models import (
    FeedbackDecision,
    FeedbackQuery,
    FeedbackRecord,
    RetrievedFeedback,
)


def make_record(**overrides) -> FeedbackRecord:
    data = {
        "feedback_id": "fb-1",
        "patch_id": "patch-1",
        "finding_id": "finding-1",
        "finding_type": "s3_public_access",
        "iac_type": "terraform",
        "resource_type": "aws_s3_bucket",
        "file_path": "main.tf",
        "vulnerability_context": "S3 bucket allows public access.",
        "original_code": "public_access = true",
        "generated_patch": "- public_access = true\n+ public_access = false",
        "decision": FeedbackDecision.ACCEPTED,
        "reason": "Correct and minimal.",
        "validation_status": "PASSED",
        "validation_errors": [],
        "timestamp": datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc),
    }
    data.update(overrides)
    return FeedbackRecord(**data)


# 1. Valid accepted feedback
def test_valid_accepted_feedback():
    record = make_record()
    assert record.decision == FeedbackDecision.ACCEPTED
    assert record.is_accepted is True
    assert record.is_rejected is False
    assert record.reason == "Correct and minimal."


# 2. Valid rejected feedback
def test_valid_rejected_feedback():
    record = make_record(
        decision=FeedbackDecision.REJECTED,
        reason="Removed permissions the application needs.",
        validation_status="FAILED",
        validation_errors=["terraform validate failed"],
    )
    assert record.decision == FeedbackDecision.REJECTED
    assert record.is_rejected is True
    assert record.validation_errors == ["terraform validate failed"]


def test_decision_string_is_case_insensitive():
    assert make_record(decision="accepted").decision == FeedbackDecision.ACCEPTED
    assert make_record(decision=" Rejected ").decision == FeedbackDecision.REJECTED


# 3. Invalid decision
@pytest.mark.parametrize("bad", ["MAYBE", "", "approve", None, 42])
def test_invalid_decision_rejected(bad):
    with pytest.raises(ValidationError):
        make_record(decision=bad)


# 4. Empty patch
@pytest.mark.parametrize("patch", ["", "   ", "\n\t"])
def test_empty_patch_rejected(patch):
    with pytest.raises(ValidationError):
        make_record(generated_patch=patch)


def test_patch_whitespace_is_preserved_verbatim():
    patch = "  resource {\n    a = 1\n  }\n"
    assert make_record(generated_patch=patch).generated_patch == patch


# 5. Missing / blank required identifiers
REQUIRED = ["feedback_id", "patch_id", "finding_id", "finding_type", "iac_type"]


@pytest.mark.parametrize("field", REQUIRED)
def test_blank_required_identifier_rejected(field):
    with pytest.raises(ValidationError):
        make_record(**{field: "   "})


@pytest.mark.parametrize("field", ["patch_id", "finding_id", "finding_type", "iac_type",
                                   "generated_patch", "decision"])
def test_missing_required_field_rejected(field):
    data = make_record().to_dict()
    del data[field]
    with pytest.raises(ValidationError):
        FeedbackRecord.from_dict(data)


def test_feedback_id_generated_when_omitted():
    data = make_record().to_dict()
    del data["feedback_id"]
    record = FeedbackRecord.from_dict(data)
    assert record.feedback_id.startswith("fb-")
    assert FeedbackRecord.from_dict(data).feedback_id != record.feedback_id


def test_identifiers_are_stripped():
    record = make_record(patch_id="  patch-9  ", finding_type=" s3_public_access ")
    assert record.patch_id == "patch-9"
    assert record.finding_type == "s3_public_access"


def test_optional_fields_default_and_blank_to_none():
    record = FeedbackRecord(
        patch_id="p", finding_id="f", finding_type="t", iac_type="terraform",
        generated_patch="x", decision="ACCEPTED", reason="   ", resource_type="",
        validation_errors=None,
    )
    assert record.reason is None
    assert record.resource_type is None
    assert record.file_path is None
    assert record.validation_errors == []
    assert record.timestamp.tzinfo is not None


def test_naive_timestamp_becomes_utc():
    record = make_record(timestamp=datetime(2025, 5, 5, 10, 0))
    assert record.timestamp.tzinfo == timezone.utc


# 6. Serialization
def test_to_dict_is_json_safe():
    payload = make_record().to_dict()
    json.dumps(payload)  # must not raise
    assert payload["decision"] == "ACCEPTED"
    assert isinstance(payload["timestamp"], str)
    assert payload["feedback_id"] == "fb-1"


def test_to_json_returns_valid_json():
    parsed = json.loads(make_record().to_json())
    assert parsed["finding_type"] == "s3_public_access"


# 7. Deserialization
def test_dict_round_trip():
    record = make_record(decision=FeedbackDecision.REJECTED, validation_errors=["e1", "e2"])
    assert FeedbackRecord.from_dict(record.to_dict()) == record


def test_json_round_trip():
    record = make_record()
    assert FeedbackRecord.from_json(record.to_json()) == record


def test_unknown_fields_are_ignored_on_load():
    data = make_record().to_dict()
    data["some_future_field"] = "x"
    assert FeedbackRecord.from_dict(data).feedback_id == "fb-1"


# Query / retrieved models
def test_query_requires_finding_and_iac_type():
    with pytest.raises(ValidationError):
        FeedbackQuery(finding_type=" ", iac_type="terraform")
    with pytest.raises(ValidationError):
        FeedbackQuery(finding_type="x", iac_type="")
    query = FeedbackQuery(finding_type="x", iac_type="terraform", resource_type=" ")
    assert query.resource_type is None


def test_retrieved_feedback_serialization_round_trip():
    retrieved = RetrievedFeedback(
        record=make_record(), score=87.5, matched_on=["finding_type"],
        score_breakdown={"finding_type": 40.0},
    )
    payload = retrieved.to_dict()
    json.dumps(payload)
    restored = RetrievedFeedback.from_dict(payload)
    assert restored == retrieved
    assert restored.decision == FeedbackDecision.ACCEPTED
    assert restored.feedback_id == "fb-1"