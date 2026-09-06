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


@router.post("/workspaces/{workspace_id}/patches/{patch_id}/validate", response_model=PatchDiff)
def validate_patch_endpoint(workspace_id: str, patch_id: str) -> PatchDiff:
    """Validate a specific patch on demand using static linters."""
    ws = workspace_store.get(workspace_id)
    if ws is None:
        raise HTTPException(status_code=404, detail="Workspace not found.")

    patch = next((p for p in ws.patches if p.patch_id == patch_id), None)
    if patch is None:
        raise HTTPException(status_code=404, detail="Patch not found in this workspace.")

    from agentshield.agents import RemediationAgent, ValidatorAgent

    validator = ValidatorAgent()
    remediator = RemediationAgent()
    finding = None
    if ws.report and ws.report.findings:
        finding = next((f for f in ws.report.findings if f.finding_id == patch.finding_id), None)

    validated = validator.validate_patch(
        template=ws.template,
        patch=patch,
        finding=finding,
        remediator=remediator,
    )
    for idx, p in enumerate(ws.patches):
        if p.patch_id == patch_id:
            ws.patches[idx] = validated
            break

    ws.execution_logs.append(
        {
            "agent": "ValidatorAgent",
            "action": "on_demand_patch_validation",
            "patch_id": patch_id,
            "status": validated.remediation_status.value,
        }
    )
    workspace_store.save(ws)
    return validated


@router.post("/workspaces/{workspace_id}/validate-patches", response_model=list[PatchDiff])
def validate_all_patches_endpoint(workspace_id: str) -> list[PatchDiff]:
    """Validate all patches in a workspace using static linters."""
    ws = workspace_store.get(workspace_id)
    if ws is None:
        raise HTTPException(status_code=404, detail="Workspace not found.")

    from agentshield.agents import RemediationAgent, ValidatorAgent

    validator = ValidatorAgent()
    remediator = RemediationAgent()

    validated = validator.validate_patches(
        template=ws.template,
        patches=ws.patches,
        report=ws.report,
        remediator=remediator,
    )
    ws.patches = validated
    ws.execution_logs.append(
        {
            "agent": "ValidatorAgent",
            "action": "on_demand_validate_all",
            "count": len(validated),
        }
    )
    workspace_store.save(ws)
    return validated

