"""Data models for Task 4.5 — Developer Feedback & Few-Shot Prompt Adaptation.

This module defines the strongly typed, serialisable models used by the rest
of the feedback package:

* :class:`FeedbackDecision`  – ACCEPTED / REJECTED.
* :class:`FeedbackRecord`    – one developer decision about one generated patch.
* :class:`FeedbackQuery`     – the *new* finding we want historical feedback for.
* :class:`RetrievedFeedback` – a stored record plus its relevance score.

The models are pure data containers.  Nothing in this module touches the
filesystem, the network, cloud APIs or any infrastructure tooling.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator


class FeedbackDecision(str, Enum):
    """The decision a developer made about a generated remediation patch."""

    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"


def _utc_now() -> datetime:
    """Return the current time as a timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)


def _new_feedback_id() -> str:
    """Generate a unique feedback identifier."""
    return f"fb-{uuid4().hex}"


def _blank_to_none(value: Optional[str]) -> Optional[str]:
    """Convert ``None`` / whitespace-only strings to ``None``."""
    if value is None:
        return None
    if not str(value).strip():
        return None
    return value


class FeedbackRecord(BaseModel):
    """A single developer decision about a generated remediation patch.

    Required (non-blank) fields: ``feedback_id``, ``patch_id``, ``finding_id``,
    ``finding_type``, ``iac_type``, ``generated_patch`` and ``decision``.
    Everything else is optional.
    """

    model_config = ConfigDict(extra="ignore")

    feedback_id: str = Field(default_factory=_new_feedback_id)
    patch_id: str
    finding_id: str
    finding_type: str
    iac_type: str
    resource_type: Optional[str] = None
    file_path: Optional[str] = None
    vulnerability_context: Optional[str] = None
    original_code: Optional[str] = None
    generated_patch: str
    decision: FeedbackDecision
    reason: Optional[str] = None
    validation_status: Optional[str] = None
    validation_errors: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=_utc_now)

    # ------------------------------------------------------------------ #
    # Validators
    # ------------------------------------------------------------------ #
    @field_validator(
        "feedback_id", "patch_id", "finding_id", "finding_type", "iac_type",
        mode="after",
    )
    @classmethod
    def _required_identifier(cls, value: str, info: Any) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError(f"{info.field_name} must not be empty")
        return stripped

    @field_validator("generated_patch", mode="after")
    @classmethod
    def _patch_not_blank(cls, value: str) -> str:
        # The patch is stored verbatim (indentation matters in IaC), but it
        # must contain something other than whitespace.
        if not value.strip():
            raise ValueError("generated_patch must not be empty")
        return value

    @field_validator("decision", mode="before")
    @classmethod
    def _normalise_decision(cls, value: Any) -> Any:
        # Accept "accepted" / "Rejected" etc. Anything else is rejected by the
        # enum validation that runs afterwards.
        if isinstance(value, str) and not isinstance(value, FeedbackDecision):
            return value.strip().upper()
        return value

    @field_validator(
        "resource_type", "file_path", "vulnerability_context", "reason",
        "validation_status", "original_code",
        mode="after",
    )
    @classmethod
    def _optional_text(cls, value: Optional[str]) -> Optional[str]:
        return _blank_to_none(value)

    @field_validator("validation_errors", mode="before")
    @classmethod
    def _errors_default(cls, value: Any) -> Any:
        return [] if value is None else value

    @field_validator("timestamp", mode="after")
    @classmethod
    def _timestamp_aware(cls, value: datetime) -> datetime:
        # Naive datetimes are interpreted as UTC so ordering is unambiguous.
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value

    # ------------------------------------------------------------------ #
    # Convenience
    # ------------------------------------------------------------------ #
    @property
    def is_accepted(self) -> bool:
        return self.decision == FeedbackDecision.ACCEPTED

    @property
    def is_rejected(self) -> bool:
        return self.decision == FeedbackDecision.REJECTED

    def to_dict(self) -> Dict[str, Any]:
        """Return a JSON-safe dictionary (enum -> str, datetime -> ISO-8601)."""
        return self.model_dump(mode="json")

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FeedbackRecord":
        """Build a record from a dictionary produced by :meth:`to_dict`."""
        return cls.model_validate(data)

    def to_json(self, **kwargs: Any) -> str:
        """Serialise the record to a JSON string."""
        return json.dumps(self.to_dict(), ensure_ascii=False, **kwargs)

    @classmethod
    def from_json(cls, payload: str) -> "FeedbackRecord":
        """Deserialise a record from a JSON string."""
        return cls.from_dict(json.loads(payload))


class FeedbackQuery(BaseModel):
    """Description of a *new* finding for which feedback should be retrieved."""

    model_config = ConfigDict(extra="ignore")

    finding_type: str
    iac_type: str
    resource_type: Optional[str] = None
    vulnerability_context: Optional[str] = None

    @field_validator("finding_type", "iac_type", mode="after")
    @classmethod
    def _required_text(cls, value: str, info: Any) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError(f"{info.field_name} must not be empty")
        return stripped

    @field_validator("resource_type", "vulnerability_context", mode="after")
    @classmethod
    def _optional_text(cls, value: Optional[str]) -> Optional[str]:
        return _blank_to_none(value)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(mode="json")


class RetrievedFeedback(BaseModel):
    """A stored feedback record together with its relevance to a query.

    ``score`` is in the range ``0.0 – 100.0``.  ``score_breakdown`` shows how
    many points each scoring component contributed and ``matched_on`` lists the
    components that matched (useful for debugging and explainability).
    """

    model_config = ConfigDict(extra="ignore")

    record: FeedbackRecord
    score: float = 0.0
    matched_on: List[str] = Field(default_factory=list)
    score_breakdown: Dict[str, float] = Field(default_factory=dict)

    @property
    def decision(self) -> FeedbackDecision:
        return self.record.decision

    @property
    def feedback_id(self) -> str:
        return self.record.feedback_id

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(mode="json")

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RetrievedFeedback":
        return cls.model_validate(data)