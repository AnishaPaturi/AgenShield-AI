"""Data contracts for Developer Feedback & Prompt Adaptation (Task 4.5)."""

from datetime import UTC, datetime
from enum import StrEnum
from uuid import uuid4

from pydantic import BaseModel, Field


class FeedbackDecision(StrEnum):
    """Developer accept/reject decision on candidate patches."""

    ACCEPT = "accept"
    REJECT = "reject"


class FeedbackCategory(StrEnum):
    """Categorization of developer feedback rationale."""

    TRUE_POSITIVE_APPROVED = "TRUE_POSITIVE_APPROVED"
    FALSE_POSITIVE_FINDING = "FALSE_POSITIVE_FINDING"
    SUBOPTIMAL_PATCH_STYLE = "SUBOPTIMAL_PATCH_STYLE"
    INTENDED_BEHAVIOR = "INTENDED_BEHAVIOR"
    OTHER = "OTHER"


class FeedbackEntry(BaseModel):
    """Recorded developer decision with full finding and patch context for few-shot learning."""

    entry_id: str = Field(
        default_factory=lambda: str(uuid4()), description="Unique feedback record identifier"
    )
    workspace_id: str = Field(..., description="Source workspace ID")
    patch_id: str = Field(..., description="Target PatchDiff ID")
    finding_id: str = Field(..., description="Associated VulnerabilityFinding ID")
    rule_id: str = Field(..., description="Detection rule ID (e.g. CKV_AWS_20)")
    resource_type: str = Field(
        default="", description="Affected IaC resource type (e.g. aws_s3_bucket)"
    )
    decision: FeedbackDecision = Field(..., description="Developer accept or reject decision")
    category: FeedbackCategory = Field(
        default=FeedbackCategory.OTHER, description="Feedback category classification"
    )
    reason: str = Field(
        default="", description="Developer commentary explaining the rationale"
    )
    original_code: str = Field(default="", description="Original code prior to patching")
    patched_code: str = Field(default="", description="Proposed remediated code snippet")
    reviewer: str = Field(default="developer", description="Identifier of the reviewer")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Timestamp when decision was submitted",
    )
