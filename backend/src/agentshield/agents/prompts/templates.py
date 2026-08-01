"""Prompt Templates and Prompt Engineering Engine for AgentShield AI.

Contains domain-engineered system prompts and prompt builders for:
1. Vulnerability Detection (Security Analyst Agent)
2. Automated Code Remediation & Patch Generation (Remediation Agent)
"""

import json
from typing import Any

from agentshield.core.schemas import IaCTemplate, VulnerabilityFinding

ANALYST_SYSTEM_PROMPT = """You are AgentShield AI's Senior DevSecOps Security Analyst Agent.
Your core mission is to perform deep context-aware security audits on IaC templates
(Terraform HCL, AWS CloudFormation, Kubernetes Manifests, Helm Charts).

Audit Guidelines:
1. **Analyze Context & AST**: Evaluate resource parameters, dynamic variable resolution,
   conditional logic, and cross-resource dependency structures.
2. **Identify Misconfigurations & Vulnerabilities**: Intercept risks such as unencrypted storage,
   wildcards in IAM policies, public exposure, missing access logs, and hardcoded credentials.
3. **Map Compliance Frameworks**: For each detected finding, map affected controls to mandates:
   - SOC2: CC6.1 (Logical Access), CC6.6 (Boundary Protection), CC6.7 (Data Transmission)
   - HIPAA: 164.312(a)(1) (Access Control), 164.312(e)(1) (Transmission Security)
   - PCI-DSS: Requirement-1.3 (Public Access), Requirement-3.4 (Data Encryption)
   - NIST-800-53: AC-2, SC-7, SC-8, AU-12
   - CIS-BENCHMARK: Platform-specific CIS benchmark controls
4. **Determine Severity & Confidence**:
   - Severity levels: CRITICAL, HIGH, MEDIUM, LOW, INFORMATIONAL
   - Confidence score: Float from 0.0 (uncertain) to 1.0 (certain)
5. **Output Requirement**: You MUST respond in valid JSON format conforming to schema.
"""

REMEDIATION_SYSTEM_PROMPT = """You are AgentShield AI's Remediation Agent.
Your sole mission is to generate executable, syntactically valid code diff patches
to remediate security findings in Infrastructure-as-Code (IaC) templates.

Remediation Guidelines:
1. **Targeted Code Fix**: Generate the exact `original_code` block containing the vulnerability
   and the drop-in replacement `patched_code` block.
2. **Preserve Functionality**: Fix security defects without removing necessary business logic,
   resource names, or structural dependencies.
3. **Format Integrity**: Maintain original syntax formatting (indents, brackets, block types).
4. **No Natural Language Hallucinations**: Return ONLY valid JSON adhering strictly to schema.
"""


def build_analyst_user_prompt(
    template: IaCTemplate,
    static_findings: list[dict[str, Any]] | None = None,
    context_docs: list[str] | None = None,
) -> str:
    """Construct a context-rich prompt for the Security Analyst Agent."""
    ast_summary = "None (AST not parsed)"
    if template.parsed_ast:
        ast_summary = json.dumps(
            {
                "root_node_id": template.parsed_ast.node_id,
                "root_node_type": template.parsed_ast.node_type,
                "children_count": len(template.parsed_ast.children),
            },
            indent=2,
        )

    static_alert_block = "None"
    if static_findings:
        static_alert_block = json.dumps(static_findings, indent=2)

    context_block = "None"
    if context_docs:
        context_block = "\n".join(f"- {doc}" for doc in context_docs)

    prompt = f"""Target IaC File: {template.file_path}
IaC Platform: {template.iac_type.value}
Target Cloud Provider: {template.cloud_provider.value}

--- RAW IAC TEMPLATE CODE ---
{template.raw_content}

--- AST STRUCTURE SUMMARY ---
{ast_summary}

--- BASELINE STATIC SCANNER ALERTS ---
{static_alert_block}

--- RETRIEVED SECURITY POLICIES & CONTEXT ---
{context_block}

INSTRUCTION: Perform a security audit on the IaC code above. Identify security vulnerabilities.
Return a list of findings matching the requested JSON schema.
"""
    return prompt


def build_remediation_user_prompt(
    template: IaCTemplate, finding: VulnerabilityFinding
) -> str:
    """Construct a targeted prompt for the Remediation Agent."""
    prompt = f"""Target IaC File: {template.file_path}
IaC Engine: {template.iac_type.value}

--- VULNERABILITY FINDING TO FIX ---
Rule ID: {finding.rule_id}
Title: {finding.title}
Severity: {finding.severity.value}
Description: {finding.description}
Affected Resource: {finding.affected_resource}
Resource Type: {finding.resource_type or 'Unknown'}
Remediation Guidance: {finding.remediation_hint or 'None provided'}

--- FULL TARGET IAC CODE ---
{template.raw_content}

INSTRUCTION: Generate an exact code fix for resource '{finding.affected_resource}'.
Provide `original_code` snippet, `patched_code` replacement, and explanation.
Return the output matching the requested PatchDiff JSON schema.
"""
    return prompt
