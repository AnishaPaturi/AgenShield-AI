"""
Agent 1: Manager / Router Agent
Orchestrates execution state and manages state transitions in the LangGraph workflow.
"""

import os
from typing import List
from agentshield.state import AgentShieldState


def manager_agent_node(state: AgentShieldState) -> AgentShieldState:
    """
    Manager/Router Agent inspects input paths, identifies IaC target files,
    and initializes state for workflow orchestration.
    """
    input_path = state.get("input_path", "")
    target_files: List[str] = []

    if os.path.isfile(input_path):
        target_files.append(input_path)
    elif os.path.isdir(input_path):
        for root, _, files in os.walk(input_path):
            for file in files:
                if file.endswith((".tf", ".tf.json", ".json", ".yaml", ".yml")):
                    target_files.append(os.path.join(root, file))

    status_log = state.get("execution_log", [])
    status_log.append(f"[Manager Agent] Discovered {len(target_files)} IaC file(s) under '{input_path}'. Routing to AST Parser and Secrets Scanner.")

    return {
        **state,
        "target_files": target_files,
        "execution_log": status_log,
        "current_agent": "Hybrid AST Parser & Secrets Scanner"
    }
