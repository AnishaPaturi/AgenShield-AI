"""Scan Orchestrator for AgentShield AI API Layer.

Coordinates a single end-to-end scan across the pipeline built by the other
three members, and returns a fully populated `AgentShieldWorkspace`:

    raw file bytes
        -> IaCTemplate                         (this module)
        -> ASTNode tree (Terraform only today) 
        -> RAG context                          (core.knowledge_base )
        -> VulnerabilityReport                  (agents.analyst)
        -> list[PatchDiff]                      (agents.remediator)
        -> AgentShieldWorkspace                 (this module)

The API layer (routers/) only ever talks to `run_scan`; it never has to know
how the individual agents work.
"""

from __future__ import annotations

import logging
import tempfile
from pathlib import Path

from agentshield.agents import RemediationAgent, SecurityAnalystAgent
from agentshield.core.schemas import (
    AgentShieldWorkspace,
    ASTNode,
    CloudProvider,
    IaCTemplate,
    IaCType,
)
from agentshield.parsers.normalizer import normalize_terraform_resources
from agentshield.parsers.terraform import extract_terraform_resources, parse_terraform_file

logger = logging.getLogger("agentshield.api.orchestrator")

# Shared agent instances (LLMClient defaults to MOCK provider unless configured
# via env vars — see agentshield.core.llm.LLMConfig — so `uv run` works offline
# out of the box, and swaps to real providers with zero code changes once
# OPENAI_API_KEY / ANTHROPIC_API_KEY are set).
_analyst = SecurityAnalystAgent()
_remediator = RemediationAgent()


def _detect_cloud_provider(raw_content: str) -> CloudProvider:
    lowered = raw_content.lower()
    if "aws_" in lowered or "provider \"aws\"" in lowered:
        return CloudProvider.AWS
    if "azurerm_" in lowered or "provider \"azurerm\"" in lowered:
        return CloudProvider.AZURE
    if "google_" in lowered or "provider \"google\"" in lowered:
        return CloudProvider.GCP
    return CloudProvider.UNKNOWN


def _build_terraform_ast(file_path: str, resources: list[dict]) -> ASTNode:
    """Convert Member 1's normalized resource dicts into an ASTNode tree."""
    children: list[ASTNode] = []
    for res in resources:
        start = res.get("start_line")
        end = res.get("end_line")
        line_range = None
        if isinstance(start, int) and isinstance(end, int) and end >= start:
            from agentshield.core.schemas import LineRange

            line_range = LineRange(start_line=start, end_line=end)

        children.append(
            ASTNode(
                node_id=res["resource_id"],
                node_type="resource",
                resource_type=res.get("resource_type"),
                name=res.get("resource_name", res["resource_id"]),
                attributes=res.get("properties", {}),
                line_range=line_range,
                parent_id="root",
            )
        )

    return ASTNode(
        node_id="root",
        node_type="module",
        name=Path(file_path).stem,
        children=children,
    )


def build_iac_template(filename: str, raw_bytes: bytes) -> IaCTemplate:
    """Parse an uploaded IaC file into an IaCTemplate (+ AST when supported)."""
    raw_content = raw_bytes.decode("utf-8", errors="replace")

    template = IaCTemplate(
        file_path=filename,
        raw_content=raw_content,
        cloud_provider=_detect_cloud_provider(raw_content),
    )
    template.auto_detect_type()

    if template.iac_type == IaCType.TERRAFORM:

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".tf", delete=False, encoding="utf-8"
        ) as tmp:
            tmp.write(raw_content)
            tmp_path = tmp.name
        try:
            parsed = parse_terraform_file(tmp_path)
            resources = normalize_terraform_resources(extract_terraform_resources(parsed))
            template.parsed_ast = _build_terraform_ast(filename, resources)
        except Exception:
            logger.exception("Terraform parsing failed for %s; continuing without AST", filename)
        finally:
            Path(tmp_path).unlink(missing_ok=True)
    else:
        logger.info(
            "AST parsing for iac_type=%s is not implemented yet; analyzing raw content only.",
            template.iac_type,
        )

    return template


def _retrieve_rag_context(template: IaCTemplate) -> list[str]:
    """Best-effort RAG context lookup. Degrades gracefully if the vector DB
        hasn't been built yet in this environment,
    so scanning still works without the knowledge base being present."""
    try:
        from agentshield.core.knowledge_base import retrieve_context

        query = f"Security best practices for {template.iac_type.value} {template.cloud_provider.value} infrastructure"
        result = retrieve_context(query, top_k=5)
        return [result["context"]] if result.get("context") else []
    except Exception:
        logger.warning(
            "RAG context retrieval unavailable (knowledge base not built or Qdrant "
            "unreachable) — proceeding with analysis without retrieved context."
        )
        return []


def run_scan(filename: str, raw_bytes: bytes) -> AgentShieldWorkspace:
    """Execute the full scan -> analyze -> remediate pipeline for one uploaded file."""
    template = build_iac_template(filename, raw_bytes)

    workspace = AgentShieldWorkspace(template=template, status="PARSED")
    workspace.execution_logs.append(
        {"agent": "Orchestrator", "action": "parsed_template", "iac_type": template.iac_type.value}
    )

    context_docs = _retrieve_rag_context(template)
    workspace.active_agent = "SecurityAnalystAgent"
    report = _analyst.analyze(template, context_docs=context_docs or None)
    workspace.report = report
    workspace.status = "ANALYZED"
    workspace.execution_logs.append(
        {
            "agent": "SecurityAnalystAgent",
            "action": "analyzed",
            "findings": len(report.findings),
            "risk_score": report.summary.risk_score,
        }
    )

    workspace.active_agent = "RemediationAgent"
    actionable = [f for f in report.findings if f.rule_id != "AS-INFO-000"]
    patches = _remediator.generate_patches(template, report.model_copy(update={"findings": actionable}))
    workspace.patches = patches
    workspace.status = "REMEDIATED"
    workspace.active_agent = None
    workspace.execution_logs.append(
        {"agent": "RemediationAgent", "action": "patches_generated", "count": len(patches)}
    )

    return workspace
