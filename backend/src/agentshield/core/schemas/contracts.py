"""Unified Core Data Contracts for AgentShield AI.

Consolidates all fundamental Pydantic v2 data models (IaCTemplate, ASTNode,
VulnerabilityReport, PatchDiff) into a unified interface module.
"""

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from agentshield.core.schemas.iac import ASTNode, CloudProvider, IaCTemplate, IaCType, LineRange
from agentshield.core.schemas.remediation import (
    PatchDiff,
    RemediationStatus,
    ValidationCheckResult,
)
from agentshield.core.schemas.vulnerability import (
    ComplianceFramework,
    ComplianceMapping,
    Severity,
    VulnerabilityFinding,
    VulnerabilityReport,
    VulnerabilitySummary,
)


class AgentShieldWorkspace(BaseModel):
    """Aggregate state contract managing complete evaluation workspace across 8 agent nodes."""

    workspace_id: str = Field(
        default_factory=lambda: str(uuid4()), description="Unique workspace session ID"
    )
    template: IaCTemplate = Field(..., description="Target Infrastructure-as-Code template model")
    report: VulnerabilityReport | None = Field(
        default=None, description="Security vulnerability assessment report"
    )
    patches: list[PatchDiff] = Field(
        default_factory=list, description="Generated code remediation patches"
    )
    active_agent: str | None = Field(
        default=None, description="Currently executing LangGraph agent node"
    )
    status: str = Field(
        default="INITIALIZED", description="Workflow state (e.g. INGESTED, PARSED, REMEDIATED)"
    )
    execution_logs: list[dict[str, Any]] = Field(
        default_factory=list, description="Audit trace log of agent actions"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Workspace creation timestamp"
    )


__all__ = [
    "IaCTemplate",
    "ASTNode",
    "LineRange",
    "IaCType",
    "CloudProvider",
    "VulnerabilityReport",
    "VulnerabilityFinding",
    "VulnerabilitySummary",
    "Severity",
    "ComplianceFramework",
    "ComplianceMapping",
    "PatchDiff",
    "RemediationStatus",
    "ValidationCheckResult",
    "AgentShieldWorkspace",
]
