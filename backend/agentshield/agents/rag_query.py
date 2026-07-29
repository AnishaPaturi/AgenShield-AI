"""
Agent 4: RAG-Query Agent
Queries vector databases (Qdrant / Knowledge Base Core) for security policies, CIS benchmarks, and regulatory compliance standards.
"""

from typing import List, Dict, Any
from agentshield.state import AgentShieldState
from agentshield.knowledge_base import KnowledgeBaseManager


def rag_query_agent_node(state: AgentShieldState) -> AgentShieldState:
    """
    Enriches AST resources with matching RAG policy rules and compliance standards (SOC 2, HIPAA, PCI-DSS, NIST 800-53).
    """
    ast_resources = state.get("ast_resources", [])
    kb_manager = KnowledgeBaseManager()
    rag_contexts: List[Dict[str, Any]] = []

    for res in ast_resources:
        res_type = res.get("resource_type", "")
        raw_code = res.get("attributes", {}).get("raw_code", str(res.get("attributes", {})))
        
        matched_rules = kb_manager.query_compliance_context(res_type, raw_code)
        if matched_rules:
            rag_contexts.append({
                "resource_id": f"{res_type}.{res.get('resource_name', 'unnamed')}",
                "file_path": res.get("file_path", ""),
                "line_number": res.get("line_start", 1),
                "matched_rules": matched_rules
            })

    status_log = state.get("execution_log", [])
    status_log.append(f"[RAG-Query Agent] Retrieved compliance context for {len(rag_contexts)} resource block(s) across SOC 2, HIPAA, PCI-DSS, and NIST 800-53 controls.")

    return {
        **state,
        "rag_context": rag_contexts,
        "execution_log": status_log,
        "current_agent": "Security Analyst Agent"
    }
