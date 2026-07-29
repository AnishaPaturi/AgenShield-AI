"""
Agent 2: Hybrid AST Parser Agent
Extracts ASTs, constructs resource dependency graphs, and resolves dynamic parameters across multi-cloud IaC templates.
"""

from typing import List
from agentshield.state import AgentShieldState
from agentshield.parsers.schemas import IaCResource
from agentshield.parsers import parse_terraform, parse_cloudformation, parse_kubernetes, parse_helm


def parser_agent_node(state: AgentShieldState) -> AgentShieldState:
    """
    Parses Terraform, CloudFormation, Kubernetes, and Helm files into IaCResource AST objects.
    """
    target_files = state.get("target_files", [])
    all_resources: List[IaCResource] = []

    for file_path in target_files:
        if file_path.endswith(".tf"):
            all_resources.extend(parse_terraform(file_path))
        elif file_path.endswith(".json"):
            # Attempt CloudFormation or Terraform JSON
            res = parse_cloudformation(file_path)
            if not res:
                res = parse_terraform(file_path)
            all_resources.extend(res)
        elif file_path.endswith((".yaml", ".yml")):
            if "helm" in file_path.lower() or "templates" in file_path.lower():
                all_resources.extend(parse_helm(file_path))
            else:
                res = parse_kubernetes(file_path)
                if not res:
                    res = parse_cloudformation(file_path)
                all_resources.extend(res)

    status_log = state.get("execution_log", [])
    status_log.append(f"[Hybrid AST Parser Agent] Extracted {len(all_resources)} resource AST block(s).")

    return {
        **state,
        "ast_resources": [res.model_dump() for res in all_resources],
        "execution_log": status_log,
        "current_agent": "Secrets Scanner"
    }
