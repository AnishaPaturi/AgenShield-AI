"""
State definitions for the AgentShield AI LangGraph orchestration state machine.
"""

from typing import TypedDict, List, Dict, Any


class AgentShieldState(TypedDict, total=False):
    """
    State container passed through the 8-agent LangGraph workflow.
    """
    input_path: str
    target_files: List[str]
    ast_resources: List[Dict[str, Any]]
    secret_findings: List[Dict[str, Any]]
    rag_context: List[Dict[str, Any]]
    security_findings: List[Dict[str, Any]]
    needs_human_review: bool
    remediation_patches: List[Dict[str, Any]]
    validation_results: List[Dict[str, Any]]
    final_report: str
    execution_log: List[str]
    current_agent: str
