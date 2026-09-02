"""API router for Human Security Audit Queue & Triage (Task 3.4).

GET  /api/audit-queue                 List queued findings
GET  /api/audit-queue/stats           Triage dashboard metrics
GET  /api/audit-queue/{item_id}       Get finding audit details
POST /api/audit-queue/{item_id}/decision Submit approve / reject decision
POST /api/audit-queue/evaluate/{id}   Evaluate workspace findings for audit queue
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from agentshield.api.store import workspace_store
from agentshield.core.audit import (
    AuditDecision,
    AuditQueueItem,
    AuditStatus,
    audit_queue_manager,
)

router = APIRouter(prefix="/api/audit-queue", tags=["audit-queue"])


class TriageDecisionRequest(BaseModel):
    decision: str
    reviewer: str = "security_engineer"
    comment: str | None = None
    override_severity: str | None = None


@router.get("", response_model=list[AuditQueueItem])
def list_audit_queue(
    status: str | None = Query(default=None, description="Filter by status: PENDING_REVIEW, APPROVED, REJECTED"),
    priority: str | None = Query(default=None, description="Filter by priority: CRITICAL, HIGH, MEDIUM, LOW"),
    workspace_id: str | None = Query(default=None, description="Filter by workspace session ID"),
) -> list[AuditQueueItem]:
    """Retrieve items from the human security audit queue."""
    return audit_queue_manager.list_items(
        status=status,
        priority=priority,
        workspace_id=workspace_id,
    )


@router.get("/stats")
def get_audit_queue_stats() -> dict[str, Any]:
    """Return aggregate triage dashboard metrics."""
    return audit_queue_manager.get_queue_summary()


@router.get("/{item_id}", response_model=AuditQueueItem)
def get_audit_item(item_id: str) -> AuditQueueItem:
    """Retrieve detailed information for a single queued finding."""
    item = audit_queue_manager.get_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Audit queue item not found.")
    return item


@router.post("/{item_id}/decision", response_model=AuditQueueItem)
def submit_triage_decision(
    item_id: str,
    payload: TriageDecisionRequest,
) -> AuditQueueItem:
    """Process security engineer decision to approve or reject a flagged finding."""
    try:
        from agentshield.core.schemas.vulnerability import Severity

        override_sev = None
        if payload.override_severity:
            try:
                override_sev = Severity(payload.override_severity.upper())
            except Exception:
                pass

        decision = AuditDecision(
            decision=payload.decision,
            reviewer=payload.reviewer,
            comment=payload.comment,
            override_severity=override_sev,
        )

        return audit_queue_manager.submit_decision(
            item_id=item_id,
            decision=decision,
            workspace_store=workspace_store,
        )
    except KeyError:
        raise HTTPException(status_code=404, detail="Audit queue item not found.")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/evaluate/{workspace_id}", response_model=list[AuditQueueItem])
def evaluate_workspace(workspace_id: str) -> list[AuditQueueItem]:
    """Evaluate all findings in a workspace and enqueue non-consensus/low-confidence findings."""
    ws = workspace_store.get(workspace_id)
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found.")
    return audit_queue_manager.evaluate_and_enqueue(ws)
