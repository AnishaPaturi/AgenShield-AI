"""AgentShield AI — FastAPI application entrypoint.

Run with:
    uv run uvicorn agentshield.api.main:app --reload --port 8000

interactive API docs at http://localhost:8000/docs
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from agentshield.api.routers import audit, health, patches, scan, workspaces

app = FastAPI(
    title="AgentShield AI API",
    description="Backend API for the AgentShield AI autonomous IaC security framework.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(scan.router)
app.include_router(workspaces.router)
app.include_router(patches.router)
app.include_router(audit.router)

