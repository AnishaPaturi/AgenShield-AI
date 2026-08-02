"""Scan submission endpoint.

POST /api/scan — upload a single IaC file, run it through:
    parse -> RAG context -> Security Analyst Agent -> Remediation Agent
and persist + return the resulting AgentShieldWorkspace.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, File, HTTPException, UploadFile

from agentshield.api.orchestrator import run_scan
from agentshield.api.store import workspace_store
from agentshield.core.schemas import AgentShieldWorkspace

logger = logging.getLogger("agentshield.api.routers.scan")
router = APIRouter(prefix="/api", tags=["scan"])

MAX_UPLOAD_BYTES = 5 * 1024 * 1024  # 5 MB is generous for a single IaC file


@router.post("/scan", response_model=AgentShieldWorkspace)
async def scan_template(file: UploadFile = File(...)) -> AgentShieldWorkspace:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Uploaded file must have a filename.")

    raw_bytes = await file.read()
    if not raw_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    if len(raw_bytes) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="File exceeds 5MB upload limit.")

    try:
        workspace = run_scan(file.filename, raw_bytes)
    except Exception as exc:  # pragma: no cover - defensive guard for API stability
        logger.exception("Scan pipeline failed for %s", file.filename)
        raise HTTPException(status_code=500, detail=f"Scan failed: {exc}") from exc

    workspace_store.save(workspace)
    return workspace
