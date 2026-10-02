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
import uuid
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
                """
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    password TEXT NOT NULL,
                    org_name TEXT,
                    phone TEXT,
                    avatar TEXT,
                    providers TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                """
            )
            # Ensure phone and avatar columns exist in existing SQLite databases
            for col_name, col_type in [("phone", "TEXT"), ("avatar", "TEXT")]:
                try:
                    conn.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type};")
                except sqlite3.OperationalError:
                    pass

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS verification_codes (
                    email TEXT PRIMARY KEY,
                    code TEXT NOT NULL,
                    expires_at REAL NOT NULL,
                    created_at TEXT NOT NULL
                );
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_workspaces_created_at ON workspaces(created_at DESC);"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_workspaces_status ON workspaces(status);"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_verification_codes_email ON verification_codes(email);"
            )
            # Pre-seed default enterprise accounts in database
            now_str = datetime.now(UTC).isoformat()
            default_accounts = [
                ("usr-admin-001", "admin@agentshield.ai", "Security Admin", "Password123!", "AgentShield Enterprise", "+1 (555) 019-2834", "", "email,google,github"),
                ("usr-alex-002", "alex@company.com", "Alex Henderson", "Password123!", "Acme Cloud Infrastructure", "+1 (555) 438-9102", "", "email,github"),
                ("usr-support-003", "agentsheildai@gmail.com", "AgentShield AI Admin", "Password123!", "AgentShield Security", "+1 (555) 892-3710", "", "email,google,github"),
            ]
            for uid, em, nm, pw, org, ph, av, prov in default_accounts:
                conn.execute(
                    """
                    INSERT INTO users (user_id, email, name, password, org_name, phone, avatar, providers, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(email) DO UPDATE SET
                        phone = coalesce(users.phone, excluded.phone);
                    """,
                    (uid, em.strip().lower(), nm, pw, org, ph, av, prov, now_str, now_str),
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

    def get_user_by_email(self, email: str) -> dict[str, Any] | None:
        """Retrieve a user by email address."""
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT user_id, email, name, password, org_name, phone, avatar, providers, created_at, updated_at FROM users WHERE lower(email) = lower(?)",
                    (email.strip(),),
                )
                row = cursor.fetchone()
                if row is None:
                    return None
                return dict(row)

    def update_user_password(self, email: str, new_password: str) -> bool:
        """Update a user's password in the database."""
        now_str = datetime.now(UTC).isoformat()
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE users SET password = ?, updated_at = ? WHERE lower(email) = lower(?)",
                    (new_password, now_str, email.strip()),
                )
                conn.commit()
                return cursor.rowcount > 0

    def update_user_profile(
        self,
        email: str,
        name: str | None = None,
        phone: str | None = None,
        org_name: str | None = None,
        avatar: str | None = None,
    ) -> dict[str, Any] | None:
        """Update user profile fields in SQLite database."""
        now_str = datetime.now(UTC).isoformat()
        fields_to_update = []
        values = []
        if name is not None:
            fields_to_update.append("name = ?")
            values.append(name.strip())
        if phone is not None:
            fields_to_update.append("phone = ?")
            values.append(phone.strip())
        if org_name is not None:
            fields_to_update.append("org_name = ?")
            values.append(org_name.strip())
        if avatar is not None:
            fields_to_update.append("avatar = ?")
            values.append(avatar.strip())

        if not fields_to_update:
            return self.get_user_by_email(email)

        fields_to_update.append("updated_at = ?")
        values.append(now_str)
        values.append(email.strip().lower())

        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                query = f"UPDATE users SET {', '.join(fields_to_update)} WHERE lower(email) = lower(?)"
                cursor.execute(query, tuple(values))
                conn.commit()

        return self.get_user_by_email(email)

    def update_user_email(self, old_email: str, new_email: str) -> bool:
        """Update a user's email address in the database."""
        now_str = datetime.now(UTC).isoformat()
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE users SET email = ?, updated_at = ? WHERE lower(email) = lower(?)",
                    (new_email.strip().lower(), now_str, old_email.strip().lower()),
                )
                conn.commit()
                return cursor.rowcount > 0

    def save_user(
        self, email: str, name: str, password: str, org_name: str = "", phone: str = "", avatar: str = "", providers: str = "email"
    ) -> dict[str, Any]:
        """Save a new user or update an existing user with automatic provider linking."""
        clean_email = email.strip().lower()
        now_str = datetime.now(UTC).isoformat()

        # Check if user already exists to merge providers and preserve custom data
        existing = self.get_user_by_email(clean_email)
        if existing:
            user_id = existing.get("user_id") or f"usr-{int(datetime.now(UTC).timestamp())}"
            # Merge providers
            ex_provs = {p.strip().lower() for p in (existing.get("providers") or "").split(",") if p.strip()}
            new_provs = {p.strip().lower() for p in providers.split(",") if p.strip()}
            merged_providers = ",".join(sorted(ex_provs | new_provs))

            # Preserve existing non-empty password if new password is blank
            effective_password = password if password else (existing.get("password") or "")
            # Preserve existing customized name if new name is a generic placeholder
            placeholders = {"google user", "github developer", "github_user", "agentshield user", ""}
            effective_name = (
                name.strip()
                if name and name.strip().lower() not in placeholders
                else (existing.get("name") or name.strip() or "Security Operator")
            )
            effective_org = org_name.strip() if org_name.strip() else (existing.get("org_name") or "")
            effective_phone = phone.strip() if phone.strip() else (existing.get("phone") or "")
            effective_avatar = avatar.strip() if avatar.strip() else (existing.get("avatar") or "")
            created_at = existing.get("created_at") or now_str
        else:
            user_id = f"usr-{uuid.uuid4().hex[:12]}"
            merged_providers = ",".join(sorted({p.strip().lower() for p in providers.split(",") if p.strip()}))
            effective_password = password
            effective_name = name.strip() or "Security Operator"
            effective_org = org_name.strip()
            effective_phone = phone.strip()
            effective_avatar = avatar.strip()
            created_at = now_str

        with self._lock:
            with self._get_connection() as conn:
                conn.execute(
                    """
                    INSERT INTO users (user_id, email, name, password, org_name, phone, avatar, providers, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(email) DO UPDATE SET
                        name = excluded.name,
                        password = excluded.password,
                        org_name = excluded.org_name,
                        phone = excluded.phone,
                        avatar = excluded.avatar,
                        providers = excluded.providers,
                        updated_at = excluded.updated_at;
                    """,
                    (
                        user_id,
                        clean_email,
                        effective_name,
                        effective_password,
                        effective_org,
                        effective_phone,
                        effective_avatar,
                        merged_providers,
                        created_at,
                        now_str,
                    ),
                )
                conn.commit()
        return self.get_user_by_email(clean_email) or {}

    def unlink_user_provider(self, email: str, provider: str) -> dict[str, Any]:
        """Safely unlink an OAuth provider from a user account."""
        clean_email = email.strip().lower()
        clean_provider = provider.strip().lower()
        user = self.get_user_by_email(clean_email)
        if not user:
            raise ValueError("User not found.")

        current_provs = {p.strip().lower() for p in (user.get("providers") or "").split(",") if p.strip()}
        if clean_provider not in current_provs:
            return user

        has_password = bool(user.get("password") and user.get("password").strip())
        remaining_provs = current_provs - {clean_provider}

        if not has_password and len(remaining_provs) == 0:
            raise ValueError(
                f"Cannot disconnect {provider.title()}. It is the only sign-in method on your account. Please set a password first."
            )

        updated_provs_str = ",".join(sorted(remaining_provs))
        now_str = datetime.now(UTC).isoformat()
        with self._lock:
            with self._get_connection() as conn:
                conn.execute(
                    "UPDATE users SET providers = ?, updated_at = ? WHERE lower(email) = lower(?)",
                    (updated_provs_str, now_str, clean_email),
                )
                conn.commit()
        return self.get_user_by_email(clean_email) or {}

    def save_verification_code(self, email: str, code: str, ttl_seconds: int = 600) -> None:
        """Store a verification code with an expiry timestamp (default 10 minutes)."""
        now_ts = datetime.now(UTC).timestamp()
        expires_at = now_ts + ttl_seconds
        now_str = datetime.now(UTC).isoformat()
        with self._lock:
            with self._get_connection() as conn:
                conn.execute(
                    """
                    INSERT INTO verification_codes (email, code, expires_at, created_at)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(email) DO UPDATE SET
                        code = excluded.code,
                        expires_at = excluded.expires_at,
                        created_at = excluded.created_at;
                    """,
                    (email.strip().lower(), code.strip(), expires_at, now_str),
                )
                conn.commit()

    def verify_code(self, email: str, code: str) -> bool:
        """Verify if a code matches and has not expired."""
        now_ts = datetime.now(UTC).timestamp()
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT code, expires_at FROM verification_codes WHERE lower(email) = lower(?)",
                    (email.strip(),),
                )
                row = cursor.fetchone()
                if not row:
                    return False
                if row["expires_at"] < now_ts:
                    return False
                return str(row["code"]).strip() == str(code).strip()

    def clear_verification_code(self, email: str) -> None:
        """Remove a verification code after successful password reset."""
        with self._lock:
            with self._get_connection() as conn:
                conn.execute(
                    "DELETE FROM verification_codes WHERE lower(email) = lower(?)",
                    (email.strip(),),
                )
                conn.commit()


# Singleton store instance shared across the API process
workspace_store = WorkspaceStore()

