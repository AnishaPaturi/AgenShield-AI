"""FastAPI router for Live Cloud Drift Detection (Task 5.2)."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from agentshield.api.store import workspace_store
from agentshield.core.drift import DriftDetector, DriftReport

router = APIRouter(prefix="/api", tags=["drift"])

_detector = DriftDetector()
_drift_cache: dict[str, DriftReport] = {}


@router.post("/workspaces/{workspace_id}/drift/scan", response_model=DriftReport)
def scan_workspace_drift(workspace_id: str) -> DriftReport:
    """Scan live cloud infrastructure for out-of-band drifts against workspace IaC template."""
    ws = workspace_store.get(workspace_id)
    if ws is None:
        raise HTTPException(status_code=404, detail="Workspace not found.")

    report = _detector.detect_drift(ws.template, workspace_id=workspace_id)
    _drift_cache[workspace_id] = report

    ws.execution_logs.append(
        {
            "agent": "DriftDetector",
            "action": "drift_scan_completed",
            "total_drifts": report.total_drifts,
            "status": report.status,
        }
    )
    workspace_store.save(ws)
    return report


@router.get("/workspaces/{workspace_id}/drift", response_model=DriftReport)
def get_workspace_drift(workspace_id: str) -> DriftReport:
    """Retrieve the latest drift report for a given workspace."""
    if workspace_id in _drift_cache:
        return _drift_cache[workspace_id]

    # Run scan on demand if not cached
    return scan_workspace_drift(workspace_id)
