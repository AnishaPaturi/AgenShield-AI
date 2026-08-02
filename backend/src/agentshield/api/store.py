"""Workspace Store for AgentShield AI API Layer.

Lightweight persistence for `AgentShieldWorkspace` objects. Deliberately avoids
introducing a database dependency for the demo/hackathon deployment: each
workspace is kept in memory for the lifetime of the process and mirrored to a
JSON file on disk so it survives an API restart. Swappable later for a real
DB (e.g. Postgres) behind the same `WorkspaceStore` interface.
"""

from __future__ import annotations

import json
from pathlib import Path
from threading import Lock

from agentshield.core.schemas import AgentShieldWorkspace

# backend/workspace_data — sibling of backend/src, backend/data, backend/tests
DATA_DIR = Path(__file__).resolve().parents[3] / "workspace_data"
DATA_DIR.mkdir(parents=True, exist_ok=True)


class WorkspaceStore:
    """Thread-safe in-memory + disk-backed store for AgentShieldWorkspace records."""

    def __init__(self, persist_dir: Path = DATA_DIR) -> None:
        self._persist_dir = persist_dir
        self._persist_dir.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()
        self._cache: dict[str, AgentShieldWorkspace] = {}
        self._load_existing()

    def _load_existing(self) -> None:
        for f in self._persist_dir.glob("*.json"):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                ws = AgentShieldWorkspace.model_validate(data)
                self._cache[ws.workspace_id] = ws
            except Exception:
                # Skip corrupt/partial files rather than crashing API startup
                continue

    def _path(self, workspace_id: str) -> Path:
        return self._persist_dir / f"{workspace_id}.json"

    def save(self, workspace: AgentShieldWorkspace) -> AgentShieldWorkspace:
        with self._lock:
            self._cache[workspace.workspace_id] = workspace
            self._path(workspace.workspace_id).write_text(
                workspace.model_dump_json(indent=2), encoding="utf-8"
            )
        return workspace

    def get(self, workspace_id: str) -> AgentShieldWorkspace | None:
        return self._cache.get(workspace_id)

    def list_all(self) -> list[AgentShieldWorkspace]:
        return sorted(self._cache.values(), key=lambda w: w.created_at, reverse=True)

    def delete(self, workspace_id: str) -> bool:
        with self._lock:
            existed = workspace_id in self._cache
            self._cache.pop(workspace_id, None)
            path = self._path(workspace_id)
            if path.exists():
                path.unlink()
            return existed


# Singleton store instance shared across the API process
workspace_store = WorkspaceStore()
