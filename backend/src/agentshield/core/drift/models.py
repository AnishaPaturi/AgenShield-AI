"""Data contracts for Live Cloud Infrastructure Drift Detection (Task 5.2)."""

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from agentshield.core.schemas import CloudProvider, PatchDiff


class DriftType(StrEnum):
    """Categorization of infrastructure drift against IaC baseline."""

    MODIFIED = "MODIFIED"  # Existing attribute changed in live cloud out-of-band
    OUT_OF_BAND_ADDITION = "OUT_OF_BAND_ADDITION"  # New resource/rule added directly in console
    DELETED = "DELETED"  # Declared IaC resource was deleted in cloud
    SECURITY_DEGRADATION = "SECURITY_DEGRADATION"  # Security posture explicitly weakened


class DriftSeverity(StrEnum):
    """Severity classification of the security risk caused by the drift."""

    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class DriftItem(BaseModel):
    """Represents a single detected delta between IaC definition and live cloud reality."""

    drift_id: str = Field(
        default_factory=lambda: str(uuid4()), description="Unique drift finding ID"
    )
    resource_id: str = Field(..., description="Target resource identifier (e.g. aws_security_group.web)")
    resource_type: str = Field(..., description="Resource type (e.g. aws_security_group)")
    cloud_provider: CloudProvider = Field(default=CloudProvider.AWS)
    drift_type: DriftType = Field(..., description="Type of drift detected")
    severity: DriftSeverity = Field(default=DriftSeverity.HIGH)
    attribute_path: str = Field(..., description="Divergent property path (e.g. ingress.cidr_blocks)")
    expected_iac_value: Any = Field(..., description="Expected baseline value defined in IaC template")
    actual_live_value: Any = Field(..., description="Observed reality in live cloud environment")
    security_implication: str = Field(
        default="", description="Detailed explanation of the risk introduced by this drift"
    )
    reconciliation_suggestion: str = Field(
        default="", description="Recommended action to remediate drift and synchronize state"
    )
    reconciliation_patch: PatchDiff | None = Field(
        default=None, description="Unified diff patch reconciling IaC with desired security baseline"
    )
    detected_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Detection timestamp"
    )


class DriftReport(BaseModel):
    """Aggregated drift report comparing an IaCTemplate against live cloud resources."""

    report_id: str = Field(
        default_factory=lambda: str(uuid4()), description="Unique drift report ID"
    )
    workspace_id: str | None = Field(default=None, description="Optional associated workspace ID")
    file_path: str = Field(default="", description="Evaluated IaC template path")
    cloud_provider: CloudProvider = Field(default=CloudProvider.AWS)
    total_drifts: int = Field(default=0)
    critical_count: int = Field(default=0)
    high_count: int = Field(default=0)
    medium_count: int = Field(default=0)
    low_count: int = Field(default=0)
    drifts: list[DriftItem] = Field(default_factory=list)
    scanned_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    status: str = Field(default="IN_SYNC")  # IN_SYNC | DRIFT_DETECTED | CRITICAL_DRIFT

    def recalculate(self) -> None:
        self.total_drifts = len(self.drifts)
        self.critical_count = sum(1 for d in self.drifts if d.severity == DriftSeverity.CRITICAL)
        self.high_count = sum(1 for d in self.drifts if d.severity == DriftSeverity.HIGH)
        self.medium_count = sum(1 for d in self.drifts if d.severity == DriftSeverity.MEDIUM)
        self.low_count = sum(1 for d in self.drifts if d.severity == DriftSeverity.LOW)

        if self.critical_count > 0:
            self.status = "CRITICAL_DRIFT"
        elif self.total_drifts > 0:
            self.status = "DRIFT_DETECTED"
        else:
            self.status = "IN_SYNC"
