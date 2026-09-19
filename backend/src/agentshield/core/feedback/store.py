"""Thread-safe persistent feedback store (Task 4.5)."""

from __future__ import annotations

import json
import logging
import threading
from pathlib import Path
from typing import Any

from agentshield.core.feedback.models import FeedbackCategory, FeedbackDecision, FeedbackEntry

logger = logging.getLogger("agentshield.core.feedback.store")

DEFAULT_FEEDBACK_DIR = Path(".agentshield")
DEFAULT_FEEDBACK_FILE = DEFAULT_FEEDBACK_DIR / "feedback_store.json"


class FeedbackStore:
    """Thread-safe persistent repository of developer patch feedback."""

    def __init__(self, storage_path: Path | str | None = None) -> None:
        self.storage_path = Path(storage_path) if storage_path else DEFAULT_FEEDBACK_FILE
        self._lock = threading.RLock()
        self._entries: dict[str, FeedbackEntry] = {}
        self._load()

    def _load(self) -> None:
        with self._lock:
            if self.storage_path.exists():
                try:
                    data = json.loads(self.storage_path.read_text(encoding="utf-8"))
                    self._entries = {
                        item["entry_id"]: FeedbackEntry.model_validate(item)
                        for item in data
                    }
                    logger.info("Loaded %d developer feedback entries from %s", len(self._entries), self.storage_path)
                except Exception as exc:
                    logger.warning("Failed to load feedback store from %s: %s", self.storage_path, exc)
                    self._entries = {}
            else:
                self._entries = {}

    def _save(self) -> None:
        with self._lock:
            try:
                self.storage_path.parent.mkdir(parents=True, exist_ok=True)
                serialized = [entry.model_dump(mode="json") for entry in self._entries.values()]
                self.storage_path.write_text(json.dumps(serialized, indent=2), encoding="utf-8")
            except Exception as exc:
                logger.warning("Failed to save feedback store to %s: %s", self.storage_path, exc)

    def record_feedback(self, entry: FeedbackEntry) -> FeedbackEntry:
        """Record developer decision and synchronize with storage."""
        with self._lock:
            self._entries[entry.entry_id] = entry
            self._save()
            logger.info(
                "Recorded %s feedback for rule %s (entry %s)",
                entry.decision.value.upper(),
                entry.rule_id,
                entry.entry_id,
            )
            return entry

    def get_entry(self, entry_id: str) -> FeedbackEntry | None:
        with self._lock:
            return self._entries.get(entry_id)

    def list_entries(
        self,
        decision: FeedbackDecision | str | None = None,
        rule_id: str | None = None,
        category: FeedbackCategory | str | None = None,
    ) -> list[FeedbackEntry]:
        """List feedback entries matching optional filters."""
        with self._lock:
            results = list(self._entries.values())

            if decision is not None:
                dec_val = decision.value if isinstance(decision, FeedbackDecision) else str(decision).lower()
                results = [e for e in results if e.decision.value == dec_val]

            if rule_id is not None:
                results = [e for e in results if e.rule_id.lower() == rule_id.lower()]

            if category is not None:
                cat_val = category.value if isinstance(category, FeedbackCategory) else str(category)
                results = [e for e in results if e.category.value == cat_val]

            return sorted(results, key=lambda e: e.created_at, reverse=True)

    def get_negative_exemplars(
        self, rule_id: str | None = None, limit: int = 3
    ) -> list[FeedbackEntry]:
        """Retrieve rejected findings to serve as negative few-shot examples."""
        entries = self.list_entries(decision=FeedbackDecision.REJECT, rule_id=rule_id)
        return entries[:limit]

    def get_positive_exemplars(
        self, rule_id: str | None = None, limit: int = 3
    ) -> list[FeedbackEntry]:
        """Retrieve accepted patches to serve as positive few-shot examples."""
        entries = self.list_entries(decision=FeedbackDecision.ACCEPT, rule_id=rule_id)
        return entries[:limit]

    def get_stats(self) -> dict[str, Any]:
        """Compute aggregate feedback statistics."""
        with self._lock:
            total = len(self._entries)
            accepts = sum(1 for e in self._entries.values() if e.decision == FeedbackDecision.ACCEPT)
            rejects = sum(1 for e in self._entries.values() if e.decision == FeedbackDecision.REJECT)
            by_category: dict[str, int] = {}
            for e in self._entries.values():
                cat = e.category.value
                by_category[cat] = by_category.get(cat, 0) + 1

            return {
                "total_feedback": total,
                "accepted_patches": accepts,
                "rejected_patches": rejects,
                "acceptance_rate": round(accepts / total, 3) if total > 0 else 1.0,
                "category_breakdown": by_category,
            }

    def clear(self) -> None:
        """Clear all feedback in memory and disk (for testing)."""
        with self._lock:
            self._entries.clear()
            self._save()


# Singleton feedback store instance
feedback_store = FeedbackStore()
