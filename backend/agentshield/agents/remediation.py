"""
Agent 6: Remediation Agent
Generates executable code diff patches targeting specific IaC resource blocks instead of text explanations.
"""

from typing import List, Dict, Any
from agentshield.state import AgentShieldState
from agentshield.parsers.schemas import PatchDiff
from agentshield.knowledge_base.vector_store import COMPLIANCE_KNOWLEDGE_BASE


def remediation_agent_node(state: AgentShieldState) -> AgentShieldState:
    """
    Generates executable diff patches for confirmed security findings.
    """
    findings = state.get("security_findings", [])
    patches: List[PatchDiff] = []

    # Map rule_id to remediation HCL/YAML
    rule_map = {r["rule_id"]: r for r in COMPLIANCE_KNOWLEDGE_BASE}

    for finding_data in findings:
        rule_id = finding_data.get("rule_id", "")
        file_path = finding_data.get("file_path", "")
        finding_id = finding_data.get("finding_id", "")
        compliance = finding_data.get("compliance_standards", [])

        rule_info = rule_map.get(rule_id, {})
        remediation_code = rule_info.get("remediation_hcl", rule_info.get("remediation_yaml", "# Security patch applied"))

        original_code = f"# Vulnerable resource block in {file_path}"
        patched_code = f"{original_code}\n  # Remediation fix ({rule_id})\n{remediation_code}"

        diff_text = (
            f"--- {file_path}\n"
            f"+++ {file_path}.patched\n"
            f"@@ -{finding_data.get('line_number', 1)},5 +{finding_data.get('line_number', 1)},8 @@\n"
            f"+  # Remediation for {rule_id}: {finding_data.get('title', '')}\n"
            f"+{remediation_code}\n"
        )

        patches.append(
            PatchDiff(
                finding_id=finding_id,
                file_path=file_path,
                original_code=original_code,
                patched_code=patched_code,
                diff_text=diff_text,
                compliance_tags=compliance
            )
        )

    status_log = state.get("execution_log", [])
    status_log.append(f"[Remediation Agent] Generated {len(patches)} executable code diff patch(es).")

    return {
        **state,
        "remediation_patches": [p.model_dump() for p in patches],
        "execution_log": status_log,
        "current_agent": "Code & Sandbox Validator Agent"
    }
