"""Prompts and Templates Package for AgentShield AI."""

from agentshield.agents.prompts.templates import (
    ANALYST_SYSTEM_PROMPT,
    REMEDIATION_SYSTEM_PROMPT,
    build_analyst_user_prompt,
    build_remediation_user_prompt,
)

__all__ = [
    "ANALYST_SYSTEM_PROMPT",
    "REMEDIATION_SYSTEM_PROMPT",
    "build_analyst_user_prompt",
    "build_remediation_user_prompt",
]
