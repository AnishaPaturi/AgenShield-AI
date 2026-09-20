"""Workspace Store for AgentShield AI API Layer.

Persistent SQLite database storage for `AgentShieldWorkspace` objects.
Workspaces are stored in an SQLite database (`agentshield.db`) with indexed
metadata columns (workspace_id, file_path, status, risk_score, total_findings,
created_at, updated_at) and a complete JSON payload column.

Provides thread-safe CRUD operations, WAL (Write-Ahead Logging) mode for
high concurrency, and automatic migration for any legacy JSON workspace files.
"""

from __future__ import annotations

import json
import logging
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from threading import RLock

from agentshield.core.schemas import AgentShieldWorkspace

logger = logging.getLogger("agentshield.api.store")

# backend/workspace_data — sibling of backend/src, backend/data, backend/tests
DATA_DIR = Path(__file__).resolve().parents[3] / "workspace_data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DEFAULT_DB_PATH = DATA_DIR / "agentshield.db"


class WorkspaceStore:
    """Thread-safe SQLite-backed store for AgentShieldWorkspace records."""

    def __init__(
        self,
        persist_dir: Path | str | None = None,
        db_path: Path | str | None = None,
    ) -> None:
        if db_path is not None:
            self._db_path = Path(db_path)
            self._persist_dir = self._db_path.parent
        elif persist_dir is not None:
            p = Path(persist_dir)
            if p.suffix in {".db", ".sqlite", ".sqlite3"}:
                self._db_path = p
                self._persist_dir = p.parent
            else:
                self._persist_dir = p
                self._db_path = p / "agentshield.db"
        else:
            self._persist_dir = DATA_DIR
            self._db_path = DEFAULT_DB_PATH

        self._persist_dir.mkdir(parents=True, exist_ok=True)
        self._lock = RLock()
        self._init_db()
        self._migrate_legacy_json()

    def _get_connection(self) -> sqlite3.Connection:
        """Create a configured SQLite connection with WAL mode and row factory."""
        conn = sqlite3.connect(
            str(self._db_path),
            timeout=30.0,
            check_same_thread=False,
        )
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        conn.execute("PRAGMA busy_timeout=5000;")
        return conn

    def _init_db(self) -> None:
        """Initialize the SQLite database schema and indices."""
        with self._lock, self._get_connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS workspaces (
                    workspace_id TEXT PRIMARY KEY,
                    file_path TEXT,
                    status TEXT,
                    risk_score REAL,
                    total_findings INTEGER,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    data JSON NOT NULL
                );
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_workspaces_created_at ON workspaces(created_at DESC);"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_workspaces_status ON workspaces(status);"
            )
            conn.commit()

    def _migrate_legacy_json(self) -> None:
        """Migrate any legacy JSON workspace files in persist_dir into SQLite."""
        if not self._persist_dir.exists():
            return

        for f in self._persist_dir.glob("*.json"):
            # Skip known non-workspace files like audit_queue.json
            if f.name in {"audit_queue.json", "feedback_store.json"}:
                continue
            try:
                content = f.read_text(encoding="utf-8")
                data = json.loads(content)
                ws = AgentShieldWorkspace.model_validate(data)
                # Save into SQLite if not already present
                if self.get(ws.workspace_id) is None:
                    self.save(ws)
                    logger.info("Migrated legacy workspace %s from %s into SQLite", ws.workspace_id, f.name)
            except Exception as exc:
                logger.debug("Skipping non-workspace or invalid JSON file %s: %s", f.name, exc)
                continue

    def save(self, workspace: AgentShieldWorkspace) -> AgentShieldWorkspace:
        """Persist or update an AgentShieldWorkspace in SQLite."""
        file_path = workspace.template.file_path if workspace.template else ""
        risk_score = (
            workspace.report.summary.risk_score
            if (workspace.report and workspace.report.summary)
            else None
        )
        total_findings = (
            workspace.report.summary.total_vulnerabilities
            if (workspace.report and workspace.report.summary)
            else None
        )
        created_at = (
            workspace.created_at.isoformat()
            if hasattr(workspace.created_at, "isoformat")
            else str(workspace.created_at)
        )
        updated_at = datetime.now(UTC).isoformat()
        serialized_json = workspace.model_dump_json()

        with self._lock:
            with self._get_connection() as conn:
                conn.execute(
                    """
                    INSERT INTO workspaces (
                        workspace_id, file_path, status, risk_score, total_findings,
                        created_at, updated_at, data
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(workspace_id) DO UPDATE SET
                        file_path = excluded.file_path,
                        status = excluded.status,
                        risk_score = excluded.risk_score,
                        total_findings = excluded.total_findings,
                        created_at = excluded.created_at,
                        updated_at = excluded.updated_at,
                        data = excluded.data;
                    """,
                    (
                        workspace.workspace_id,
                        file_path,
                        workspace.status,
                        risk_score,
                        total_findings,
                        created_at,
                        updated_at,
                        serialized_json,
                    ),
                )
                conn.commit()
        return workspace

    def get(self, workspace_id: str) -> AgentShieldWorkspace | None:
        """Retrieve an AgentShieldWorkspace by its unique workspace_id."""
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT data FROM workspaces WHERE workspace_id = ?",
                    (workspace_id,),
                )
                row = cursor.fetchone()
                if row is None:
                    return None
                return AgentShieldWorkspace.model_validate_json(row["data"])

    def list_all(self) -> list[AgentShieldWorkspace]:
        """Retrieve all workspaces ordered by creation date descending."""
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT data FROM workspaces ORDER BY created_at DESC")
                rows = cursor.fetchall()
                workspaces: list[AgentShieldWorkspace] = []
                for row in rows:
                    try:
                        workspaces.append(AgentShieldWorkspace.model_validate_json(row["data"]))
                    except Exception as exc:
                        logger.warning("Failed to deserialize workspace row: %s", exc)
                return workspaces

    def delete(self, workspace_id: str) -> bool:
        """Delete a workspace by ID. Returns True if existed and deleted, False otherwise."""
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM workspaces WHERE workspace_id = ?",
                    (workspace_id,),
                )
                conn.commit()
                return cursor.rowcount > 0

    def clear(self) -> None:
        """Delete all workspaces from the store (used for test isolation)."""
        with self._lock:
            with self._get_connection() as conn:
                conn.execute("DELETE FROM workspaces")
                conn.commit()


# Singleton store instance shared across the API process
workspace_store = WorkspaceStore()
