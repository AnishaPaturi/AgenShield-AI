"""Audit Queue Manager and Automated Escalation Engine (Task 3.4)."""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from threading import Lock
from typing import Any

from agentshield.core.audit.models import (
    AuditDecision,
    AuditQueueItem,
    AuditStatus,
    EscalationReason,
)
from agentshield.core.schemas.contracts import AgentShieldWorkspace
from agentshield.core.schemas.vulnerability import (
    AUTO_PATCH_THRESHOLD,
    Severity,
    VulnerabilityFinding,
)

logger = logging.getLogger("agentshield.core.audit")

# Default persistence location for audit queue
DATA_DIR = Path(__file__).resolve().parents[4] / "workspace_data"
AUDIT_FILE = DATA_DIR / "audit_queue.json"


class AuditQueueManager:
    """Thread-safe manager for Human Security Audit Queue with automated escalation."""

    def __init__(self, persist_file: Path = AUDIT_FILE) -> None:
        self._persist_file = persist_file
        self._lock = Lock()
        self._items: dict[str, AuditQueueItem] = {}
        self._load()

    def _load(self) -> None:
        """Load stored audit items from JSON disk storage."""
        if not self._persist_file.exists():
            return
        try:
            data = json.loads(self._persist_file.read_text(encoding="utf-8"))
            for raw in data:
                item = AuditQueueItem.model_validate(raw)
                self._items[item.item_id] = item
        except Exception:
            logger.exception("Failed to load audit queue from %s", self._persist_file)

    def _save(self) -> None:
        """Serialize audit queue to disk atomically."""
        try:
            self._persist_file.parent.mkdir(parents=True, exist_ok=True)
            serialized = [item.model_dump(mode="json") for item in self._items.values()]
            self._persist_file.write_text(json.dumps(serialized, indent=2), encoding="utf-8")
        except Exception:
            logger.exception("Failed to save audit queue to %s", self._persist_file)

    def evaluate_finding_for_escalation(
        self,
        finding: VulnerabilityFinding,
        workspace_id: str,
        file_path: str,
        patch_map: dict[str, Any] | None = None,
    ) -> AuditQueueItem | None:
        """Evaluate whether a finding should be automatically escalated to human review.

        Escalation Rules:
        1. Low Confidence: finding.confidence_score < 0.85
        2. Model Disagreement / Non-Consensus: consensus_score < 0.80 or requires_human_review=True
        3. Single-Model Hallucination: model disagreement / divergent finding
        4. Critical Exploitability Route: Critical severity with active attack path
        5. Large Blast Radius: Blast radius affects >= 5 downstream resources
        """
        escalation_trigger: EscalationReason | None = None
        escalation_reason: str | None = None

        # Rule 1 & 2: Low confidence or explicit human review flag
        if finding.requires_human_review or finding.confidence_score < AUTO_PATCH_THRESHOLD:
            escalation_trigger = EscalationReason.LOW_CONFIDENCE
            escalation_reason = (
                finding.escalation_reason
                or f"Confidence score ({finding.confidence_score:.2f}) is below the auto-patch threshold ({AUTO_PATCH_THRESHOLD})."
            )

        # Rule 3: Model disagreement or non-consensus
        if finding.consensus_score is not None and finding.consensus_score < 0.80:
            escalation_trigger = EscalationReason.MODEL_DISAGREEMENT
            escalation_reason = (
                f"Multi-LLM consensus score ({finding.consensus_score:.2f}) indicates model disagreement. "
                f"Agreed models: {', '.join(finding.model_agreements) if finding.model_agreements else 'none'}."
            )

        # Rule 4: Critical severity with active attack path from internet
        if (
            finding.severity == Severity.CRITICAL
            and finding.attack_path
            and not escalation_trigger
        ):
            escalation_trigger = EscalationReason.CRITICAL_ATTACK_PATH
            escalation_reason = (
                f"Critical severity finding exposed via active exploitability route: "
                f"{' → '.join(finding.attack_path)}. Mandatory human audit sign-off required."
            )

        # Rule 5: High blast radius impact
        blast_count = finding.raw_details.get("blast_radius", 0)
        if blast_count >= 5 and not escalation_trigger:
            escalation_trigger = EscalationReason.HIGH_BLAST_RADIUS
            escalation_reason = (
                f"Compromise blast radius affects {blast_count} downstream resources. "
                "Manual review required before auto-patch execution."
            )

        if not escalation_trigger:
            return None

        # Determine priority metadata
        priority_score = float(finding.raw_details.get("priority_score", 50.0))
        priority = str(finding.raw_details.get("priority", "MEDIUM"))

        suggested_patch = None
        if patch_map and finding.finding_id in patch_map:
            suggested_patch = patch_map[finding.finding_id]

        item = AuditQueueItem(
            finding_id=finding.finding_id,
            workspace_id=workspace_id,
            file_path=file_path,
            finding=finding,
            suggested_patch=suggested_patch,
            status=AuditStatus.PENDING_REVIEW,
            escalation_reason=escalation_reason,
            escalation_trigger=escalation_trigger,
            priority_score=priority_score,
            priority=priority,
            attack_path=finding.attack_path,
            blast_radius=blast_count,
        )

        return item

    def enqueue(self, item: AuditQueueItem) -> AuditQueueItem:
        """Enqueue an item into the audit queue, updating if already present."""
        with self._lock:
            # Check for existing pending item for same finding in workspace
            existing = self._find_existing(item.workspace_id, item.finding_id)
            if existing:
                # Update existing rather than creating duplicate
                existing.finding = item.finding
                existing.suggested_patch = item.suggested_patch or existing.suggested_patch
                existing.escalation_reason = item.escalation_reason
                existing.escalation_trigger = item.escalation_trigger
                existing.priority_score = item.priority_score
                existing.priority = item.priority
                existing.attack_path = item.attack_path
                existing.blast_radius = item.blast_radius
                self._save()
                return existing

            self._items[item.item_id] = item
            self._save()
            return item

    def _find_existing(self, workspace_id: str, finding_id: str) -> AuditQueueItem | None:
        """Find existing item matching workspace and finding ID."""
        for item in self._items.values():
            if item.workspace_id == workspace_id and item.finding_id == finding_id:
                return item
        return None

    def evaluate_and_enqueue(self, workspace: AgentShieldWorkspace) -> list[AuditQueueItem]:
        """Automatically evaluate all findings in a workspace and enqueue flagged findings."""
        if not workspace.report:
            return []

        patch_map = {p.finding_id: p for p in workspace.patches}
        enqueued: list[AuditQueueItem] = []

        for finding in workspace.report.findings:
            item = self.evaluate_finding_for_escalation(
                finding=finding,
                workspace_id=workspace.workspace_id,
                file_path=workspace.template.file_path,
                patch_map=patch_map,
            )
            if item:
                saved = self.enqueue(item)
                enqueued.append(saved)

        return enqueued

    def submit_decision(
        self,
        item_id: str,
        decision: AuditDecision,
        workspace_store: Any | None = None,
    ) -> AuditQueueItem:
        """Process a security engineer's triage decision (approve / reject)."""
        with self._lock:
            item = self._items.get(item_id)
            if not item:
                raise KeyError(f"Audit queue item not found: {item_id}")

            norm_decision = decision.decision.strip().lower()
            if norm_decision not in {"approve", "reject"}:
                raise ValueError(f"Invalid decision '{decision.decision}'; must be 'approve' or 'reject'")

            item.status = AuditStatus.APPROVED if norm_decision == "approve" else AuditStatus.REJECTED
            item.reviewed_at = datetime.now(UTC)
            item.reviewer = decision.reviewer
            item.reviewer_comment = decision.comment

            if decision.override_severity is not None:
                item.finding.severity = decision.override_severity

            # Sync decision back to workspace finding in workspace_store if available
            if workspace_store:
                try:
                    ws = workspace_store.get(item.workspace_id)
                    if ws and ws.report:
                        for f in ws.report.findings:
                            if f.finding_id == item.finding_id:
                                if item.status == AuditStatus.APPROVED:
                                    f.requires_human_review = False
                                    f.auto_patchable = True
                                    f.raw_details["triage_status"] = "APPROVED"
                                    f.raw_details["triage_reviewer"] = decision.reviewer
                                    f.raw_details["triage_comment"] = decision.comment
                                else:
                                    f.requires_human_review = False
                                    f.auto_patchable = False
                                    f.raw_details["triage_status"] = "REJECTED_FALSE_POSITIVE"
                                    f.raw_details["triage_reviewer"] = decision.reviewer
                                    f.raw_details["triage_comment"] = decision.comment
                                if decision.override_severity:
                                    f.severity = decision.override_severity
                        ws.report.recalculate_summary()
                        ws.execution_logs.append({
                            "agent": "HumanAuditQueue",
                            "action": f"triage_{norm_decision}",
                            "item_id": item_id,
                            "finding_id": item.finding_id,
                            "reviewer": decision.reviewer,
                        })
                        workspace_store.save(ws)
                except Exception:
                    logger.exception("Failed to sync audit decision back to workspace %s", item.workspace_id)

            self._save()
            return item

    def get_item(self, item_id: str) -> AuditQueueItem | None:
        """Fetch an individual audit queue item by ID."""
        return self._items.get(item_id)

    def list_items(
        self,
        status: AuditStatus | str | None = None,
        workspace_id: str | None = None,
        priority: str | None = None,
    ) -> list[AuditQueueItem]:
        """List audit queue items matching optional filters, sorted by priority score."""
        results: list[AuditQueueItem] = []

        status_str = status.value if isinstance(status, AuditStatus) else status
        if status_str:
            status_str = status_str.upper()

        for item in self._items.values():
            if status_str and item.status.value != status_str:
                continue
            if workspace_id and item.workspace_id != workspace_id:
                continue
            if priority and item.priority.upper() != priority.upper():
                continue
            results.append(item)

        # Sort descending by priority_score, then created_at
        return sorted(results, key=lambda x: (x.priority_score, x.created_at), reverse=True)

    def get_queue_summary(self) -> dict[str, Any]:
        """Aggregate summary metrics for the audit queue triage dashboard."""
        total = len(self._items)
        pending = sum(1 for i in self._items.values() if i.status == AuditStatus.PENDING_REVIEW)
        approved = sum(1 for i in self._items.values() if i.status == AuditStatus.APPROVED)
        rejected = sum(1 for i in self._items.values() if i.status == AuditStatus.REJECTED)

        crit_pending = sum(
            1 for i in self._items.values()
            if i.status == AuditStatus.PENDING_REVIEW and i.priority == "CRITICAL"
        )
        high_pending = sum(
            1 for i in self._items.values()
            if i.status == AuditStatus.PENDING_REVIEW and i.priority == "HIGH"
        )

        confidences = [i.finding.confidence_score for i in self._items.values()]
        avg_confidence = round(sum(confidences) / len(confidences), 4) if confidences else 1.0

        return {
            "total_items": total,
            "pending_count": pending,
            "approved_count": approved,
            "rejected_count": rejected,
            "critical_pending": crit_pending,
            "high_pending": high_pending,
            "avg_confidence": avg_confidence,
        }

    def clear(self) -> None:
        """Clear all audit queue items (used in test teardown)."""
        with self._lock:
            self._items.clear()
            if self._persist_file.exists():
                try:
                    self._persist_file.unlink()
                except Exception:
                    pass


# Process-wide singleton audit queue manager
audit_queue_manager = AuditQueueManager()
