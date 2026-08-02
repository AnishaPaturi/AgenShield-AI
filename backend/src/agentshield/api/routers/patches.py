"""Patch review endpoints.

Lets a developer accept or reject a generated PatchDiff from the dashboard
(Task 4.5's feedback loop starts here — every accept/reject decision is
recorded in the workspace's execution_logs for the future few-shot
prompt-adaptation store).
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from agentshield.api.store import workspace_store
from agentshield.core.schemas import PatchDiff, RemediationStatus

router = APIRouter(prefix="/api", tags=["patches"])


class PatchDecision(BaseModel):
    decision: str  # "accept" | "reject"


@router.post("/workspaces/{workspace_id}/patches/{patch_id}/decision", response_model=PatchDiff)
def decide_patch(workspace_id: str, patch_id: str, decision: PatchDecision) -> PatchDiff:
    if decision.decision not in {"accept", "reject"}:
        raise HTTPException(status_code=400, detail="decision must be 'accept' or 'reject'.")

    ws = workspace_store.get(workspace_id)
    if ws is None:
        raise HTTPException(status_code=404, detail="Workspace not found.")

    patch = next((p for p in ws.patches if p.patch_id == patch_id), None)
    if patch is None:
        raise HTTPException(status_code=404, detail="Patch not found in this workspace.")

    patch.remediation_status = (
        RemediationStatus.APPLIED if decision.decision == "accept" else RemediationStatus.REJECTED
    )
    ws.execution_logs.append(
        {"agent": "Developer", "action": "patch_decision", "patch_id": patch_id, "decision": decision.decision}
    )
    workspace_store.save(ws)
    return patch
