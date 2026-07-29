"""
Agent 2: Hybrid AST Parser Agent
Extracts ASTs, constructs resource dependency graphs, pre-evaluates dynamic parameters,
and enriches attributes via static scanners (Checkov, tfsec, KICS).
"""

from typing import List
from agentshield.state import AgentShieldState
from agentshield.parsers.schemas import IaCResource
from agentshield.parsers import parse_terraform, parse_cloudformation, parse_kubernetes, parse_helm
from agentshield.utils.static_scanners import enrich_ast_resources


def parser_agent_node(state: AgentShieldState) -> AgentShieldState:
    """
    Parses Terraform, CloudFormation, Kubernetes, and Helm templates into IaCResource AST objects
    and enriches attributes using Checkov, tfsec, and KICS static scanners.
    """
    target_files = state.get("target_files", [])
    input_path = state.get("input_path", "")
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

    # Perform Hybrid AST Parsing & Static Scanner Enrichment (Checkov, tfsec, KICS)
    raw_ast_dicts = [res.model_dump() for res in all_resources]
    enriched_ast = enrich_ast_resources(raw_ast_dicts, target_path=input_path)

    status_log = state.get("execution_log", [])
    status_log.append(f"[Hybrid AST Parser Agent] Extracted {len(all_resources)} resource AST block(s) and enriched attributes via Checkov, tfsec, & KICS static scanners.")

    return {
        **state,
        "ast_resources": enriched_ast,
        "execution_log": status_log,
        "current_agent": "Secrets Scanner"
    }
