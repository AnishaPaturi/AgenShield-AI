"""Remediation Schema Contracts for AgentShield AI.

Defines core data structures for code diff patches, remediation status lifecycle,
and validation check results from static linters and sandbox runtime tests.
"""

import difflib
from datetime import UTC, datetime
from enum import StrEnum
from uuid import uuid4

from pydantic import BaseModel, Field, model_validator


class RemediationStatus(StrEnum):
    """Lifecycle status of a generated code patch."""

    PENDING = "PENDING"
    SYNTAX_VALIDATED = "SYNTAX_VALIDATED"
    SANDBOX_PASSED = "SANDBOX_PASSED"
    APPLIED = "APPLIED"
    REJECTED = "REJECTED"
    FAILED = "FAILED"


class ValidationCheckResult(BaseModel):
    """Result of a single linter or sandbox validation check."""

    check_name: str = Field(
        ..., description="Check engine (e.g. terraform_validate, cfn_lint, localstack_dryrun)"
    )
    passed: bool = Field(..., description="Whether the validation check passed successfully")
    output: str = Field(default="", description="Standard output or log from check execution")
    error: str | None = Field(
        default=None, description="Error message or stderr if check failed"
    )


class PatchDiff(BaseModel):
    """Represents a generated code patch diff targeting a specific IaC vulnerability."""

    patch_id: str = Field(
        default_factory=lambda: str(uuid4()), description="Unique patch identifier"
    )
    finding_id: str = Field(..., description="ID of VulnerabilityFinding being remediated")
    target_file: str = Field(..., description="Path to target IaC file being patched")
    original_code: str = Field(..., description="Original unpatched code snippet or file section")
    patched_code: str = Field(..., description="Remediated code snippet or file section")
    unified_diff: str = Field(
        default="", description="Git-style unified diff representation of changes"
    )
    target_resource: str = Field(
        ..., description="node_id or resource path targeted by the patch"
    )
    remediation_status: RemediationStatus = Field(
        default=RemediationStatus.PENDING, description="Current lifecycle state of the patch"
    )
    auto_patchable: bool = Field(
        default=True,
        description="Whether patch was derived from a high-confidence finding (C >= 0.85) eligible for automated application",
    )
    requires_human_review: bool = Field(
        default=False,
        description="Whether patch requires human security engineer audit/approval prior to merge (C < 0.85)",
    )
    validation_results: list[ValidationCheckResult] = Field(
        default_factory=list, description="Linter and sandbox test results"
    )
    explanation: str = Field(
        default="", description="Explanation of why and how the patch resolves the issue"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Patch generation timestamp",
    )

    @model_validator(mode="after")
    def ensure_unified_diff(self) -> "PatchDiff":
        """Automatically generate unified_diff if not explicitly provided."""
        if not self.unified_diff and self.original_code and self.patched_code:
            self.generate_unified_diff()
        return self

    def generate_unified_diff(self) -> str:
        """Compute git-style unified diff string from original_code and patched_code."""
        orig_lines = self.original_code.splitlines(keepends=True)
        patch_lines = self.patched_code.splitlines(keepends=True)

        diff_gen = difflib.unified_diff(
            orig_lines,
            patch_lines,
            fromfile=f"a/{self.target_file}",
            tofile=f"b/{self.target_file}",
        )
        self.unified_diff = "".join(diff_gen)
        return self.unified_diff
