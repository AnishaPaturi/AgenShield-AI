"""Task 4.5 — Interactive Developer Feedback & Few-Shot Prompt Adaptation Engine.

Public API::

    from agentshield.feedback import FeedbackService

    service = FeedbackService()
    service.record_feedback(...)
    context = service.get_adaptation_context(...)

This package is self-contained: it stores developer decisions in a local JSON
file, retrieves similar historical feedback with deterministic scoring, and
builds few-shot prompt context for the Remediation Agent.  It performs no model
training and never executes patches or touches infrastructure.
"""

from .adaptation import (
    PromptAdaptationEngine,
    build_few_shot_context,
    format_negative_example,
    format_positive_example,
)
from .models import (
    FeedbackDecision,
    FeedbackQuery,
    FeedbackRecord,
    RetrievedFeedback,
)
from .retriever import FeedbackRetriever
from .service import FeedbackService
from .store import FeedbackStore, FeedbackStoreError

__all__ = [
    "FeedbackDecision",
    "FeedbackRecord",
    "FeedbackQuery",
    "RetrievedFeedback",
    "FeedbackStore",
    "FeedbackStoreError",
    "FeedbackRetriever",
    "PromptAdaptationEngine",
    "build_few_shot_context",
    "format_positive_example",
    "format_negative_example",
    "FeedbackService",
]