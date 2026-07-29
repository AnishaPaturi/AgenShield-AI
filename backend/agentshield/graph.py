"""
LangGraph Orchestration State Machine for AgentShield AI.
Constructs and compiles the 8-agent state graph.
"""

from typing import Dict, Any
from langgraph.graph import StateGraph, START, END
from agentshield.state import AgentShieldState
from agentshield.agents import (
    manager_agent_node,
    parser_agent_node,
    secrets_agent_node,
    rag_query_agent_node,
    analyst_agent_node,
    remediation_agent_node,
    validator_agent_node,
    report_agent_node
)


def build_agentshield_graph():
    """
    Constructs the 8-agent LangGraph state machine workflow.
    """
    workflow = StateGraph(AgentShieldState)

    # Add all 8 specialized agent nodes
    workflow.add_node("manager_agent", manager_agent_node)
    workflow.add_node("parser_agent", parser_agent_node)
    workflow.add_node("secrets_agent", secrets_agent_node)
    workflow.add_node("rag_query_agent", rag_query_agent_node)
    workflow.add_node("analyst_agent", analyst_agent_node)
    workflow.add_node("remediation_agent", remediation_agent_node)
    workflow.add_node("validator_agent", validator_agent_node)
    workflow.add_node("report_agent", report_agent_node)

    # Set up edges
    workflow.add_edge(START, "manager_agent")
    workflow.add_edge("manager_agent", "parser_agent")
    workflow.add_edge("parser_agent", "secrets_agent")
    workflow.add_edge("secrets_agent", "rag_query_agent")
    workflow.add_edge("rag_query_agent", "analyst_agent")
    workflow.add_edge("analyst_agent", "remediation_agent")
    workflow.add_edge("remediation_agent", "validator_agent")
    workflow.add_edge("validator_agent", "report_agent")
    workflow.add_edge("report_agent", END)

    return workflow.compile()


class AgentShieldOrchestrator:
    """
    High-level state machine orchestrator interface.
    """
    def __init__(self):
        self.app = build_agentshield_graph()

    def run(self, input_path: str) -> Dict[str, Any]:
        initial_state: AgentShieldState = {
            "input_path": input_path,
            "target_files": [],
            "ast_resources": [],
            "secret_findings": [],
            "rag_context": [],
            "security_findings": [],
            "needs_human_review": False,
            "remediation_patches": [],
            "validation_results": [],
            "final_report": "",
            "execution_log": ["Initializing AgentShield AI LangGraph Orchestration State Machine..."],
            "current_agent": "Manager Agent"
        }
        return self.app.invoke(initial_state)
