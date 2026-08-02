"""Workspace retrieval + report export endpoints.

GET /api/workspaces                    list all scanned workspaces (summary)
GET /api/workspaces/{id}                full workspace (template + report + patches)
GET /api/workspaces/{id}/export/{fmt}   report export: json | markdown | html | sarif | pdf
DELETE /api/workspaces/{id}             remove a workspace
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel

from agentshield.api.report_export import MEDIA_TYPES, RENDERERS
from agentshield.api.store import workspace_store
from agentshield.core.schemas import AgentShieldWorkspace

router = APIRouter(prefix="/api", tags=["workspaces"])


class WorkspaceSummary(BaseModel):
    workspace_id: str
    file_path: str
    status: str
    risk_score: float | None = None
    total_findings: int | None = None
    created_at: str


def _to_summary(ws: AgentShieldWorkspace) -> WorkspaceSummary:
    return WorkspaceSummary(
        workspace_id=ws.workspace_id,
        file_path=ws.template.file_path,
        status=ws.status,
        risk_score=ws.report.summary.risk_score if ws.report else None,
        total_findings=ws.report.summary.total_vulnerabilities if ws.report else None,
        created_at=ws.created_at.isoformat(),
    )


@router.get("/workspaces", response_model=list[WorkspaceSummary])
def list_workspaces() -> list[WorkspaceSummary]:
    return [_to_summary(ws) for ws in workspace_store.list_all()]


@router.get("/workspaces/{workspace_id}", response_model=AgentShieldWorkspace)
def get_workspace(workspace_id: str) -> AgentShieldWorkspace:
    ws = workspace_store.get(workspace_id)
    if ws is None:
        raise HTTPException(status_code=404, detail="Workspace not found.")
    return ws


@router.delete("/workspaces/{workspace_id}")
def delete_workspace(workspace_id: str) -> dict[str, bool]:
    deleted = workspace_store.delete(workspace_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Workspace not found.")
    return {"deleted": True}


@router.get("/workspaces/{workspace_id}/export/{fmt}")
def export_workspace(workspace_id: str, fmt: str) -> Response:
    fmt = fmt.lower()
    if fmt not in RENDERERS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported export format '{fmt}'. Supported: {sorted(RENDERERS)}",
        )

    ws = workspace_store.get(workspace_id)
    if ws is None:
        raise HTTPException(status_code=404, detail="Workspace not found.")

    content = RENDERERS[fmt](ws)
    media_type = MEDIA_TYPES[fmt]
    body = content if isinstance(content, bytes) else content.encode("utf-8")

    extension = "md" if fmt == "markdown" else fmt
    filename = f"agentshield_report_{workspace_id[:8]}.{extension}"

    return Response(
        content=body,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
