"""Dynamic few-shot prompt adaptation engine for AgentShield AI (Task 4.5).

Connects developer accept/reject decisions to LLM prompting routines:
- Injects negative few-shot examples into Security Analyst prompts to suppress false positives.
- Injects positive few-shot examples into Remediation Agent prompts to guide code patch generation.
"""

from __future__ import annotations

import logging
from typing import Any

from agentshield.core.feedback.models import FeedbackEntry
from agentshield.core.feedback.store import FeedbackStore, feedback_store

logger = logging.getLogger("agentshield.core.feedback.adaptation")


class FeedbackPromptAdaptor:
    """Formats developer feedback history into dynamic few-shot prompt context."""

    def __init__(self, store: FeedbackStore | None = None) -> None:
        self.store = store or feedback_store

    def build_analyst_negative_shot_prompt(
        self,
        rule_ids: list[str] | None = None,
        limit: int = 3,
    ) -> str:
        """Construct negative-shot instructions informing the Analyst of past false positives."""
        exemplars: list[FeedbackEntry] = []
        if rule_ids:
            for rid in rule_ids:
                exemplars.extend(self.store.get_negative_exemplars(rule_id=rid, limit=limit))
        else:
            exemplars = self.store.get_negative_exemplars(limit=limit)

        if not exemplars:
            return ""

        lines = [
            "### TEAM FEEDBACK & FALSE POSITIVE SUPPRESSION RULES:",
            "The engineering team previously REJECTED the following finding patterns as false positives or intended architecture:",
        ]

        for idx, entry in enumerate(exemplars[:limit], 1):
            resource_info = f" on {entry.resource_type}" if entry.resource_type else ""
            lines.append(
                f"{idx}. [Rule {entry.rule_id}{resource_info}] Reason: \"{entry.reason}\" (Category: {entry.category.value})"
            )
            if entry.original_code:
                lines.append(f"   Context snippet: `{entry.original_code.strip()}`")

        lines.append(
            "CRITICAL: Do NOT report a finding if the resource configuration matches any of the approved team exceptions above."
        )
        return "\n".join(lines)

    def build_remediation_few_shot_prompt(
        self,
        rule_id: str | None = None,
        limit: int = 3,
    ) -> str:
        """Construct positive few-shot examples showing accepted patch styles."""
        exemplars = self.store.get_positive_exemplars(rule_id=rule_id, limit=limit)
        if not exemplars:
            return ""

        lines = [
            "### APPROVED TEAM REMEDIATION EXAMPLES (Few-Shot Context):",
            "The engineering team has previously accepted and merged the following patch patterns:",
        ]

        for idx, entry in enumerate(exemplars[:limit], 1):
            lines.append(f"Example {idx} (Rule: {entry.rule_id}):")
            if entry.reason:
                lines.append(f"Developer Note: {entry.reason}")
            if entry.original_code and entry.patched_code:
                lines.append("```diff")
                lines.append(f"--- Original:\n{entry.original_code.strip()}")
                lines.append(f"+++ Patched:\n{entry.patched_code.strip()}")
                lines.append("```")

        lines.append(
            "Follow these verified coding conventions and formatting practices when generating candidate patches."
        )
        return "\n".join(lines)


# Singleton prompt adaptor
feedback_adaptor = FeedbackPromptAdaptor()
