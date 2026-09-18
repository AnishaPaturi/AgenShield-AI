"""High-level service for Task 4.5 — Developer Feedback & Prompt Adaptation.

:class:`FeedbackService` is the single entry point other parts of AgentShield-AI
should use.  It composes:

* :class:`~agentshield.feedback.store.FeedbackStore`          - persistence
* :class:`~agentshield.feedback.retriever.FeedbackRetriever`  - similarity search
* :class:`~agentshield.feedback.adaptation.PromptAdaptationEngine` - prompt text

Typical integration (done later, outside this module)::

    service = FeedbackService()

    # 1. A developer accepts / rejects a generated patch
    service.record_feedback(
        patch_id="patch-1", finding_id="finding-9",
        finding_type="s3_public_access", iac_type="terraform",
        generated_patch="- public_access = true\\n+ public_access = false",
        decision="ACCEPTED", reason="Correct and minimal.",
    )

    # 2. Before generating a new patch, fetch few-shot context
    context = service.get_adaptation_context(
        finding_type="s3_public_access", iac_type="terraform",
        resource_type="aws_s3_bucket",
        vulnerability_context="S3 bucket has public access enabled.",
    )
    # -> insert ``context`` into the Remediation Agent prompt

The service never executes patches, calls AWS/LocalStack, or runs Terraform,
CloudFormation, kubectl or Helm.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import List, Optional, Sequence, Union

from .adaptation import PromptAdaptationEngine
from .models import FeedbackDecision, FeedbackQuery, FeedbackRecord, RetrievedFeedback
from .retriever import FeedbackRetriever
from .store import FeedbackStore


class FeedbackService:
    """Record developer feedback and turn history into few-shot prompt context."""

    def __init__(
        self,
        store: Optional[FeedbackStore] = None,
        retriever: Optional[FeedbackRetriever] = None,
        adaptation_engine: Optional[PromptAdaptationEngine] = None,
        *,
        storage_path: Optional[Union[str, Path]] = None,
    ) -> None:
        """Create the service.

        Args:
            store: An existing store. Mutually exclusive with ``storage_path``.
            retriever: Custom retriever (defaults to one bound to ``store``).
            adaptation_engine: Custom engine (defaults to default limits).
            storage_path: Location of the JSON file when no ``store`` is given.
        """
        if store is not None and storage_path is not None:
            raise ValueError("Provide either 'store' or 'storage_path', not both")
        self._store = store if store is not None else FeedbackStore(storage_path)
        self._retriever = (
            retriever if retriever is not None else FeedbackRetriever(self._store)
        )
        self._engine = (
            adaptation_engine if adaptation_engine is not None else PromptAdaptationEngine()
        )

    # ------------------------------------------------------------------ #
    # Components (read-only access)
    # ------------------------------------------------------------------ #
    @property
    def store(self) -> FeedbackStore:
        return self._store

    @property
    def retriever(self) -> FeedbackRetriever:
        return self._retriever

    @property
    def adaptation_engine(self) -> PromptAdaptationEngine:
        return self._engine

    # ------------------------------------------------------------------ #
    # Recording and reading feedback
    # ------------------------------------------------------------------ #
    def record_feedback(
        self,
        patch_id: str,
        finding_id: str,
        finding_type: str,
        iac_type: str,
        generated_patch: str,
        decision: Union[FeedbackDecision, str],
        reason: Optional[str] = None,
        *,
        resource_type: Optional[str] = None,
        file_path: Optional[str] = None,
        original_code: Optional[str] = None,
        vulnerability_context: Optional[str] = None,
        validation_status: Optional[str] = None,
        validation_errors: Optional[Sequence[str]] = None,
        feedback_id: Optional[str] = None,
        timestamp: Optional[datetime] = None,
    ) -> FeedbackRecord:
        """Validate and persist a developer decision about a generated patch.

        ``decision`` may be a :class:`FeedbackDecision` or the strings
        ``"ACCEPTED"`` / ``"REJECTED"`` (case-insensitive).  Invalid input raises
        :class:`pydantic.ValidationError`.
        """
        data = {
            "patch_id": patch_id,
            "finding_id": finding_id,
            "finding_type": finding_type,
            "iac_type": iac_type,
            "generated_patch": generated_patch,
            "decision": decision,
            "reason": reason,
            "resource_type": resource_type,
            "file_path": file_path,
            "original_code": original_code,
            "vulnerability_context": vulnerability_context,
            "validation_status": validation_status,
            "validation_errors": list(validation_errors) if validation_errors else [],
        }
        # Let the model generate feedback_id / timestamp unless supplied.
        if feedback_id is not None:
            data["feedback_id"] = feedback_id
        if timestamp is not None:
            data["timestamp"] = timestamp
        record = FeedbackRecord(**data)
        return self._store.save_feedback(record)

    def get_feedback(self, feedback_id: str) -> Optional[FeedbackRecord]:
        """Return one record by id, or ``None``."""
        return self._store.get_feedback(feedback_id)

    def get_all_feedback(self) -> List[FeedbackRecord]:
        """Return every stored record."""
        return self._store.get_all_feedback()

    def get_feedback_by_patch(self, patch_id: str) -> List[FeedbackRecord]:
        return self._store.get_feedback_by_patch(patch_id)

    def get_feedback_by_finding(self, finding_id: str) -> List[FeedbackRecord]:
        return self._store.get_feedback_by_finding(finding_id)

    def delete_feedback(self, feedback_id: str) -> bool:
        return self._store.delete_feedback(feedback_id)

    def clear_feedback(self) -> int:
        """Remove all stored developer feedback and return the number removed."""
        return self._store.clear_feedback()

    # ------------------------------------------------------------------ #
    # Retrieval and adaptation
    # ------------------------------------------------------------------ #
    def find_similar_feedback(
        self,
        finding_type: str,
        iac_type: str,
        resource_type: Optional[str] = None,
        vulnerability_context: Optional[str] = None,
        *,
        top_k: Optional[int] = 5,
        decision: Optional[Union[FeedbackDecision, str]] = None,
        min_score: Optional[float] = None,
    ) -> List[RetrievedFeedback]:
        """Return historical feedback relevant to a new finding, best first."""
        return self._retriever.retrieve_similar_feedback(
            finding_type,
            iac_type,
            resource_type,
            vulnerability_context,
            top_k=top_k,
            decision=decision,
            min_score=min_score,
        )

    def get_adaptation_context(
        self,
        finding_type: str,
        iac_type: str,
        resource_type: Optional[str] = None,
        vulnerability_context: Optional[str] = None,
    ) -> str:
        """Return the few-shot prompt context for a new finding.

        Steps: retrieve similar feedback -> separate ACCEPTED and REJECTED ->
        hand both lists to the adaptation engine -> return the prompt string.
        Always returns a valid string, even when no feedback exists.
        """
        query = FeedbackQuery(
            finding_type=finding_type,
            iac_type=iac_type,
            resource_type=resource_type,
            vulnerability_context=vulnerability_context,
        )
        # Retrieve each class separately so one cannot crowd out the other.
        accepted = self._retriever.retrieve_accepted(
            query, top_k=self._engine.max_positive_examples
        )
        rejected = self._retriever.retrieve_rejected(
            query, top_k=self._engine.max_negative_examples
        )
        return self._engine.build_few_shot_context(query, accepted, rejected)