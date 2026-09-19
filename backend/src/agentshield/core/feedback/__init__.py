"""AgentShield AI Developer Feedback & Prompt Adaptation Package (Task 4.5)."""

from agentshield.core.feedback.adaptation import FeedbackPromptAdaptor, feedback_adaptor
from agentshield.core.feedback.models import FeedbackCategory, FeedbackDecision, FeedbackEntry
from agentshield.core.feedback.store import FeedbackStore, feedback_store

__all__ = [
    "FeedbackDecision",
    "FeedbackCategory",
    "FeedbackEntry",
    "FeedbackStore",
    "feedback_store",
    "FeedbackPromptAdaptor",
    "feedback_adaptor",
]
