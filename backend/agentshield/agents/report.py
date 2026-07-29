"""
Agent 8: Report Generator Agent
Formats unified security reports mapped to compliance frameworks (SOC 2, HIPAA, PCI-DSS, NIST 800-53)
and captures developer feedback for continuous prompt tuning.
"""

from typing import Dict, Any, List
from agentshield.state import AgentShieldState


def report_agent_node(state: AgentShieldState) -> AgentShieldState:
    """
    Generates final unified security and compliance report.
    """
    findings = state.get("security_findings", [])
    secrets = state.get("secret_findings", [])
    patches = state.get("remediation_patches", [])
    validations = state.get("validation_results", [])
    execution_log = state.get("execution_log", [])

    total_vulns = len(findings) + len(secrets)
    compliance_summary: Dict[str, int] = {
        "SOC 2": 0,
        "HIPAA": 0,
        "PCI-DSS": 0,
        "NIST 800-53": 0
    }

    for f in findings:
        for std in f.get("compliance_standards", []):
            if "SOC2" in std:
                compliance_summary["SOC 2"] += 1
            if "HIPAA" in std:
                compliance_summary["HIPAA"] += 1
            if "PCI" in std:
                compliance_summary["PCI-DSS"] += 1
            if "NIST" in std:
                compliance_summary["NIST 800-53"] += 1

    report_content = f"""# AgentShield AI - Unified Multi-Cloud Security & Compliance Audit Report

## Executive Summary
* **Total Misconfigurations Detected:** {len(findings)}
* **Hardcoded Secret Leaks Intercepted:** {len(secrets)}
* **Total Security Issues:** {total_vulns}
* **Auto-Generated Code Patches:** {len(patches)}
* **Sandbox Verified Patches:** {len([v for v in validations if v.get('sandbox_passed')])}
* **Human Security Escalation Needed:** {state.get('needs_human_review', False)}

---

## Regulatory Compliance Impact Breakdown
* **SOC 2 Controls Flagged:** {compliance_summary['SOC 2']}
* **HIPAA Security Rule Violations:** {compliance_summary['HIPAA']}
* **PCI-DSS Requirements Flagged:** {compliance_summary['PCI-DSS']}
* **NIST 800-53 Control Gaps:** {compliance_summary['NIST 800-53']}

---

## Secrets & Credential Leakage (Secrets Scanner Agent)
"""
    if secrets:
        for sec in secrets:
            report_content += f"- **[{sec.get('severity')}] {sec.get('secret_type')}** in `{sec.get('file_path')}` at line {sec.get('line_number')}\n  `{sec.get('snippet')}`\n"
    else:
        report_content += "No hardcoded credentials or API tokens detected.\n"

    report_content += "\n---\n\n## Vulnerability Findings & Multi-LLM Ensemble Voting\n"
    for finding in findings:
        votes = finding.get("model_votes", {})
        vote_str = ", ".join([f"{k}: {v}" for k, v in votes.items()])
        report_content += f"""### [{finding.get('severity')}] {finding.get('title')} ({finding.get('rule_id')})
* **Resource:** `{finding.get('resource_id')}`
* **File & Line:** `{finding.get('file_path')}:L{finding.get('line_number')}`
* **Compliance Frameworks:** {', '.join(finding.get('compliance_standards', []))}
* **Calibrated Confidence Score:** {finding.get('confidence_score')}
* **Multi-LLM Voting:** {vote_str}
* **Description:** {finding.get('description')}

"""

    report_content += "---\n\n## Executable Remediation Diff Patches\n"
    for patch in patches:
        report_content += f"### Diff Patch for Finding `{patch.get('finding_id')}`\n```diff\n{patch.get('diff_text')}\n```\n"

    status_log = execution_log
    status_log.append("[Report Agent] Generated final unified compliance & vulnerability audit report.")

    return {
        **state,
        "final_report": report_content,
        "execution_log": status_log,
        "current_agent": "COMPLETE"
    }
