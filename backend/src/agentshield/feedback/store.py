"""JSON persistence for developer feedback (Task 4.5).

:class:`FeedbackStore` is a small, dependency-free, file-backed store.

Storage location
----------------
The location is resolved in this order:

1. The ``storage_path`` argument passed to :class:`FeedbackStore`.
2. The ``AGENTSHIELD_FEEDBACK_STORE`` environment variable.
3. ``~/.agentshield/feedback/feedback.json`` (outside the repository, so
   runtime data is never committed by accident).

The file *and* its parent directories are created automatically, and a new
store starts as an empty JSON list: ``[]``.

Robustness guarantees
---------------------
* Writes are atomic (temporary file + ``os.replace``), so a crash never leaves
  a half-written store.
* Read-modify-write cycles are guarded by a lock, so concurrent threads in one
  process cannot lose each other's records.  (Cross-process locking is out of
  scope for this standalone JSON store.)
  * Adding a record never drops existing entries - even entries that no longer
  validate as :class:`FeedbackRecord` are preserved in the store.
* A malformed / unreadable store is *quarantined*: the bad file is renamed to
  ``feedback.json.corrupt-<timestamp>`` and a fresh empty store is created, so
  the application keeps working and the bad data is never silently destroyed.

This module never executes patches or touches any infrastructure.
"""

from __future__ import annotations

import json
import logging
import os
import tempfile
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, List, Optional, Union

from pydantic import ValidationError

from .models import FeedbackRecord

logger = logging.getLogger(__name__)

#: Environment variable that overrides the default storage path.
STORAGE_PATH_ENV_VAR = "AGENTSHIELD_FEEDBACK_STORE"

_DEFAULT_RELATIVE_PATH = Path(".agentshield") / "feedback" / "feedback.json"


class FeedbackStoreError(Exception):
    """Raised when the feedback store cannot be read from or written to."""


def default_storage_path() -> Path:
    """Return the default location of ``feedback.json``."""
    override = os.environ.get(STORAGE_PATH_ENV_VAR)
    if override and override.strip():
        return Path(override).expanduser()
    try:
        base = Path.home()
    except (RuntimeError, KeyError):  # pragma: no cover - no HOME available
        base = Path.cwd()
    return base / _DEFAULT_RELATIVE_PATH


class FeedbackStore:
    """File-backed store for :class:`FeedbackRecord` objects."""

    def __init__(self, storage_path: Optional[Union[str, Path]] = None) -> None:
        self._path: Path = (
            Path(storage_path).expanduser()
            if storage_path is not None
            else default_storage_path()
        )
        self._lock = threading.RLock()
        self._ensure_storage()

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    @property
    def storage_path(self) -> Path:
        """Path of the JSON file backing this store."""
        return self._path

    def save_feedback(self, record: FeedbackRecord) -> FeedbackRecord:
        """Persist ``record``.

        If a record with the same ``feedback_id`` already exists it is replaced
        in place (e.g. a developer changed their mind); otherwise the record is
        appended.  All other entries are left untouched.
        """
        if not isinstance(record, FeedbackRecord):
            raise TypeError("record must be a FeedbackRecord")
        payload = record.to_dict()
        with self._lock:
            raw = self._read_raw()
            for index, item in enumerate(raw):
                if isinstance(item, dict) and item.get("feedback_id") == record.feedback_id:
                    raw[index] = payload
                    break
            else:
                raw.append(payload)
            self._write_raw(raw)
        return record

    def get_feedback(self, feedback_id: str) -> Optional[FeedbackRecord]:
        """Return the record with ``feedback_id`` or ``None``."""
        wanted = (feedback_id or "").strip()
        for record in self.get_all_feedback():
            if record.feedback_id == wanted:
                return record
        return None

    def get_all_feedback(self) -> List[FeedbackRecord]:
        """Return every valid record, in storage (insertion) order."""
        with self._lock:
            raw = self._read_raw()
        return self._parse_records(raw)

    def get_feedback_by_patch(self, patch_id: str) -> List[FeedbackRecord]:
        """Return all records that belong to ``patch_id``."""
        wanted = (patch_id or "").strip()
        return [r for r in self.get_all_feedback() if r.patch_id == wanted]

    def get_feedback_by_finding(self, finding_id: str) -> List[FeedbackRecord]:
        """Return all records that belong to ``finding_id``."""
        wanted = (finding_id or "").strip()
        return [r for r in self.get_all_feedback() if r.finding_id == wanted]

    def delete_feedback(self, feedback_id: str) -> bool:
        """Delete the record with ``feedback_id``. Returns ``True`` if removed."""
        wanted = (feedback_id or "").strip()
        with self._lock:
            raw = self._read_raw()
            kept = [
                item for item in raw
                if not (isinstance(item, dict) and item.get("feedback_id") == wanted)
            ]
            if len(kept) == len(raw):
                return False
            self._write_raw(kept)
        return True

    def clear_feedback(self) -> int:
        """Remove every entry from the store. Returns the number removed."""
        with self._lock:
            removed = len(self._read_raw())
            self._write_raw([])
        return removed

    def count(self) -> int:
        """Number of valid records currently stored."""
        return len(self.get_all_feedback())

    # ------------------------------------------------------------------ #
    # Internals
    # ------------------------------------------------------------------ #
    def _ensure_storage(self) -> None:
        """Create the parent directory and an empty ``[]`` file if missing."""
        with self._lock:
            if self._path.exists():
                return
            try:
                self._path.parent.mkdir(parents=True, exist_ok=True)
            except OSError as exc:
                raise FeedbackStoreError(
                    f"Cannot create feedback directory {self._path.parent}: {exc}"
                ) from exc
            self._write_raw([])

    def _read_raw(self) -> List[Any]:
        """Read the JSON list from disk (quarantining corrupt files)."""
        self._ensure_storage()
        try:
            text = self._path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            self._quarantine("file is not valid UTF-8")
            return []
        except OSError as exc:
            raise FeedbackStoreError(
                f"Cannot read feedback store {self._path}: {exc}"
            ) from exc

        if not text.strip():
            return []  # empty file == empty store

        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            self._quarantine(f"malformed JSON ({exc.msg})")
            return []

        if not isinstance(data, list):
            self._quarantine("top-level JSON value is not a list")
            return []
        return data

    def _write_raw(self, data: List[Any]) -> None:
        """Atomically write ``data`` to disk as pretty-printed JSON."""
        tmp_name: Optional[str] = None
        try:
            fd, tmp_name = tempfile.mkstemp(
                dir=str(self._path.parent), prefix=".feedback-", suffix=".tmp"
            )
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(data, handle, indent=2, ensure_ascii=False)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(tmp_name, self._path)
            tmp_name = None
        except OSError as exc:
            raise FeedbackStoreError(
                f"Cannot write feedback store {self._path}: {exc}"
            ) from exc
        finally:
            if tmp_name is not None and os.path.exists(tmp_name):
                try:
                    os.unlink(tmp_name)
                except OSError:  # pragma: no cover - best effort cleanup
                    logger.warning("Could not remove temporary file %s", tmp_name)

    def _quarantine(self, reason: str) -> None:
        """Move an unreadable store aside and start a fresh empty one."""
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%f")
        backup = self._path.with_name(f"{self._path.name}.corrupt-{stamp}")
        try:
            os.replace(self._path, backup)
        except OSError as exc:
            raise FeedbackStoreError(
                f"Feedback store {self._path} is corrupt ({reason}) and could "
                f"not be moved aside: {exc}"
            ) from exc
        logger.warning(
            "Feedback store %s was corrupt (%s); preserved as %s and "
            "started a new empty store.",
            self._path, reason, backup,
        )
        self._write_raw([])

    @staticmethod
    def _parse_records(raw: List[Any]) -> List[FeedbackRecord]:
        records: List[FeedbackRecord] = []
        for index, item in enumerate(raw):
            if not isinstance(item, dict):
                logger.warning("Skipping non-object feedback entry at index %d", index)
                continue
            try:
                records.append(FeedbackRecord.model_validate(item))
            except ValidationError as exc:
                logger.warning(
                    "Skipping invalid feedback entry at index %d: %s", index, exc
                )
        return records