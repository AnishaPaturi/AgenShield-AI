"""Data contracts and schemas for Human Security Audit Queue & Triage (Task 3.4)."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from agentshield.core.schemas.remediation import PatchDiff
from agentshield.core.schemas.vulnerability import Severity, VulnerabilityFinding


class AuditStatus(StrEnum):
    """Lifecycle status of a finding in the Human Security Audit Queue."""

    PENDING_REVIEW = "PENDING_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class EscalationReason(StrEnum):
    """Categorized root causes for escalating a finding to human triage."""

    LOW_CONFIDENCE = "LOW_CONFIDENCE"
    MODEL_DISAGREEMENT = "MODEL_DISAGREEMENT"
    SINGLE_MODEL_HALLUCINATION = "SINGLE_MODEL_HALLUCINATION"
    CRITICAL_ATTACK_PATH = "CRITICAL_ATTACK_PATH"
    HIGH_BLAST_RADIUS = "HIGH_BLAST_RADIUS"
    MANUAL_ESCALATION = "MANUAL_ESCALATION"


class AuditDecision(BaseModel):
    """Security engineer decision payload for a queued audit finding."""

    decision: str = Field(..., description="Action to take: 'approve' or 'reject'")
    reviewer: str = Field(default="security_engineer", description="Identity or email of reviewer")
    comment: str | None = Field(default=None, description="Triage commentary or rationale")
    override_severity: Severity | None = Field(
        default=None, description="Optional manual override of finding severity"
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Timestamp of triage decision"
    )


class AuditQueueItem(BaseModel):
    """Individual item in the Human Security Audit Queue awaiting review."""

    item_id: str = Field(
        default_factory=lambda: str(uuid4()), description="Unique audit item identifier"
    )
    finding_id: str = Field(..., description="Referenced vulnerability finding ID")
    workspace_id: str = Field(..., description="Referenced workspace ID")
    file_path: str = Field(..., description="Target file path under assessment")
    finding: VulnerabilityFinding = Field(..., description="Original vulnerability finding payload")
    suggested_patch: PatchDiff | None = Field(
        default=None, description="Suggested code patch if generated"
    )
    status: AuditStatus = Field(
        default=AuditStatus.PENDING_REVIEW, description="Current triage review state"
    )
    escalation_reason: str = Field(
        ..., description="Human-readable explanation of why finding was escalated"
    )
    escalation_trigger: EscalationReason = Field(
        default=EscalationReason.LOW_CONFIDENCE,
        description="Categorized machine trigger for escalation",
    )
    priority_score: float = Field(
        default=50.0, ge=0.0, le=100.0, description="Task 3.3 combined risk priority score"
    )
    priority: str = Field(
        default="MEDIUM", description="Assigned priority label: CRITICAL, HIGH, MEDIUM, LOW"
    )
    attack_path: list[str] = Field(
        default_factory=list, description="Exploitability route from internet entry point"
    )
    blast_radius: int = Field(
        default=0, ge=0, description="Downstream reachable blast radius count"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="When item was enqueued"
    )
    reviewed_at: datetime | None = Field(
        default=None, description="When reviewer completed triage"
    )
    reviewer: str | None = Field(
        default=None, description="Identifier of the security engineer who reviewed"
    )
    reviewer_comment: str | None = Field(
        default=None, description="Engineer notes explaining approval or rejection"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional context or scanner telemetry"
    )
