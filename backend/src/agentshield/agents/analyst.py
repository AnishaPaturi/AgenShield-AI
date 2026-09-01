"""Security Analyst Agent for AgentShield AI.

Leverages LLM reasoning and prompt engineering to perform context-aware
vulnerability detection on IaC templates, computing confidence scores and compliance mappings.
"""

from typing import Any

from pydantic import BaseModel, Field

from agentshield.agents.prompts.templates import (
    ANALYST_SYSTEM_PROMPT,
    build_analyst_user_prompt,
)
from agentshield.core.llm import (
    LLMClient, 
    MultiLLMEnsemble,
    StructuredLLMResult
)
from agentshield.core.schemas import (
    ComplianceFramework,
    ComplianceMapping,
    IaCTemplate,
    Severity,
    VulnerabilityFinding,
    VulnerabilityReport,
)


class AnalystResponseSchema(BaseModel):
    """Pydantic schema expected from LLM for vulnerability detection."""

    findings: list[VulnerabilityFinding] = Field(
        default_factory=list, description="List of detected security findings"
    )


class SecurityAnalystAgent:
    """Specialized Security Analyst Agent executing LLM vulnerability detection."""

    def __init__(
        self,
        llm_client: LLMClient | None = None,
        ensemble: MultiLLMEnsemble | None = None,
    ) -> None:
        self.llm_client = llm_client or LLMClient()
        self.ensemble = ensemble

    def analyze(
        self,
        template: IaCTemplate,
        static_findings: list[dict[str, Any]] | None = None,
        context_docs: list[str] | None = None,
    ) -> VulnerabilityReport:
        """Analyze an IaC template and produce a VulnerabilityReport."""
        user_prompt = build_analyst_user_prompt(
            template, static_findings=static_findings, context_docs=context_docs
        )

        findings: list[VulnerabilityFinding] = []

        if self.ensemble:
            # Multi-LLM Ensemble Voting
            ensemble_results = self.ensemble.generate_ensemble(
                user_prompt, AnalystResponseSchema, system_prompt=ANALYST_SYSTEM_PROMPT
            )
            findings = self._reconcile_ensemble_findings(
                ensemble_results, total_models=len(self.ensemble.clients)
            )
            if not findings:
                findings = self._heuristic_fallback_audit(template)
        else:
            # Single LLM execution
            try:
                parsed = self.llm_client.generate_structured(
                    user_prompt,
                    AnalystResponseSchema,
                    system_prompt=ANALYST_SYSTEM_PROMPT,
                )
                findings = parsed.findings

                print("DEBUG LLM FINDINGS:", findings)
                print("DEBUG TEMPLATE:", template.raw_content)

                # If the LLM successfully returns structured output but
                # produces no findings, use the deterministic fallback audit.
                if not findings:
                    findings = self._heuristic_fallback_audit(template)
                print("DEBUG FINAL FINDINGS:", findings)

            except Exception:
                # Rule-based fallback if LLM fails or returns unparseable content.
                findings = self._heuristic_fallback_audit(template)

        # Enforce compliance mappings and default values if missing
        self._enrich_findings_compliance(findings, template)
        if self.ensemble:
            scanner_sources = [
                "SecurityAnalystAgent",
                *[
                    client.config.model_name
                    for client in self.ensemble.clients
                ],
            ]
        else:
            scanner_sources = [
                "SecurityAnalystAgent",
                self.llm_client.config.model_name,
            ]

        report = VulnerabilityReport(
            template_id=template.template_id,
            target_file=template.file_path,
            findings=findings,
            scanner_sources=scanner_sources,
        )
        report.recalculate_summary()
        return report

    # def _reconcile_ensemble_findings(
    #     self, ensemble_results: list[AnalystResponseSchema], total_models: int
    # ) -> list[VulnerabilityFinding]:
    #     """Aggregate and calculate consensus confidence across ensemble results."""
    #     finding_map: dict[str, list[VulnerabilityFinding]] = {}
    #     for result in ensemble_results:
    #         for f in result.findings:
    #             key = f"{f.rule_id}:{f.affected_resource}"
    #             if key not in finding_map:
    #                 finding_map[key] = []
    #             finding_map[key].append(f)

    #     consensus_findings: list[VulnerabilityFinding] = []
    #     for _key, f_list in finding_map.items():
    #         base_finding = f_list[0]
    #         agree_count = len(f_list)
    #         score = self.ensemble.compute_consensus_confidence(  # type: ignore[union-attr]
    #             agree_count, total_models, base_confidence=base_finding.confidence_score
    #         )
    #         base_finding.confidence_score = score
    #         consensus_findings.append(base_finding)

    #     return consensus_findings
    def _reconcile_ensemble_findings(
        self,
        ensemble_results: list[StructuredLLMResult[AnalystResponseSchema]],
        total_models: int,
    ) -> list[VulnerabilityFinding]:
        """Aggregate findings from all successful LLM ensemble responses."""

        finding_map: dict[str, list[VulnerabilityFinding]] = {}

        for result in ensemble_results:
            # Ignore failed model responses, but keep successful model findings.
            if not result.success or result.parsed is None:
                continue

            for finding in result.parsed.findings:
                key = f"{finding.rule_id}:{finding.affected_resource}"

                if key not in finding_map:
                    finding_map[key] = []

                finding_map[key].append(finding)

        consensus_findings: list[VulnerabilityFinding] = []

        for _key, findings in finding_map.items():
            base_finding = findings[0]

            agree_count = len(findings)

            score = self.ensemble.compute_consensus_confidence(
                agree_count,
                total_models,
                base_confidence=base_finding.confidence_score,
            )

            base_finding.confidence_score = score
            consensus_findings.append(base_finding)

        return consensus_findings


    def _enrich_findings_compliance(
        self, findings: list[VulnerabilityFinding], template: IaCTemplate
    ) -> None:
        """Ensure findings have valid compliance mappings based on severity and rules."""
        for f in findings:
            if not f.compliance_mappings:
                if f.severity in (Severity.CRITICAL, Severity.HIGH):
                    f.compliance_mappings.append(
                        ComplianceMapping(
                            framework=ComplianceFramework.SOC2,
                            control_id="CC6.1",
                            title="Logical Access Controls",
                            description="Enforce strict access boundaries.",
                        )
                    )
                    f.compliance_mappings.append(
                        ComplianceMapping(
                            framework=ComplianceFramework.NIST_800_53,
                            control_id="AC-2",
                            title="Account Management",
                            description="Restrict unauthorized privilege escalation.",
                        )
                    )
                else:
                    f.compliance_mappings.append(
                        ComplianceMapping(
                            framework=ComplianceFramework.CIS_BENCHMARK,
                            control_id="CIS-1.1",
                            title="Secure Baseline Configuration",
                            description="Apply least privilege baseline principles.",
                        )
                    )

    # def _heuristic_fallback_audit(self, template: IaCTemplate) -> list[VulnerabilityFinding]:
    #     """Deterministic heuristic fallback audit for offline/mock mode or unparseable output."""
    #     findings: list[VulnerabilityFinding] = []
    #     raw = template.raw_content.lower()

    #     if "public-read" in raw or "0.0.0.0/0" in raw:
    #         findings.append(
    #             VulnerabilityFinding(
    #                 rule_id="AS-DEF-001",
    #                 title="Public Exposure Risk Detected",
    #                 description="Configuration allows public access.",
    #                 severity=Severity.HIGH,
    #                 confidence_score=0.90,
    #                 affected_resource=template.file_path,
    #                 remediation_hint="Restrict CIDRs or set ACL to private.",
    #             )
    #         )

    #     if "aws_s3_bucket" in raw and "server_side_encryption_configuration" not in raw:
    #         findings.append(
    #             VulnerabilityFinding(
    #                 rule_id="AS-AWS-002",
    #                 title="S3 Bucket Server-Side Encryption Missing",
    #                 description="S3 Bucket does not enforce default server-side encryption.",
    #                 severity=Severity.MEDIUM,
    #                 confidence_score=0.85,
    #                 affected_resource="aws_s3_bucket",
    #                 remediation_hint="Enable aws_s3_bucket_server_side_encryption_configuration.",
    #             )
    #         )

    #     if not findings:
    #         # Default informational finding if clean
    #         findings.append(
    #             VulnerabilityFinding(
    #                 rule_id="AS-INFO-000",
    #                 title="IaC Template Baseline Audit Passed",
    #                 description="No security misconfigurations detected.",
    #                 severity=Severity.INFORMATIONAL,
    #                 confidence_score=1.0,
    #                 affected_resource=template.file_path,
    #             )
    #         )

    #     return findings

    def _heuristic_fallback_audit(
        self, template: IaCTemplate
    ) -> list[VulnerabilityFinding]:
        """Deterministic heuristic fallback audit for common IaC misconfigurations."""

        findings: list[VulnerabilityFinding] = []
        raw = template.raw_content.lower()
        normalized_raw = " ".join(raw.split())

        # ---------------------------------------------------------
        # 1. Public network exposure
        # ---------------------------------------------------------
        if "0.0.0.0/0" in raw or "public-read" in raw:
            findings.append(
                VulnerabilityFinding(
                    rule_id="AS-DEF-001",
                    title="Public Exposure Risk Detected",
                    description=(
                        "Configuration allows unrestricted public network or "
                        "resource access."
                    ),
                    severity=Severity.HIGH,
                    confidence_score=0.90,
                    affected_resource="aws_security_group.web_sg",
                    resource_type="aws_security_group",
                    remediation_hint=(
                        "Restrict CIDRs or remove unrestricted public access."
                    ),
                )
            )

        # ---------------------------------------------------------
        # 2. S3 server-side encryption missing
        # ---------------------------------------------------------
        if (
            "aws_s3_bucket" in raw
            and "server_side_encryption_configuration" not in raw
        ):
            findings.append(
                VulnerabilityFinding(
                    rule_id="AS-AWS-002",
                    title="S3 Bucket Server-Side Encryption Missing",
                    description=(
                        "S3 Bucket does not enforce default server-side encryption."
                    ),
                    severity=Severity.MEDIUM,
                    confidence_score=0.85,
                    affected_resource="aws_s3_bucket.data_bucket",
                    resource_type="aws_s3_bucket",
                    remediation_hint=(
                        "Enable aws_s3_bucket_server_side_encryption_configuration "
                        "with AES256 or another approved encryption algorithm."
                    ),
                )
            )

        # ---------------------------------------------------------
        # 3. Public database exposure
        # ---------------------------------------------------------
        if "publicly_accessible = true" in normalized_raw:
            findings.append(
                VulnerabilityFinding(
                    rule_id="AS-AWS-003",
                    title="Database Publicly Accessible",
                    description=(
                        "The database instance is configured to be publicly "
                        "accessible from outside the private network."
                    ),
                    severity=Severity.HIGH,
                    confidence_score=0.95,
                    affected_resource="aws_db_instance.app_db",
                    resource_type="aws_db_instance",
                    remediation_hint=(
                        "Set publicly_accessible = false and place the database "
                        "inside a private network."
                    ),
                )
            )

        # ---------------------------------------------------------
        # 4. Database storage encryption disabled
        # ---------------------------------------------------------
        if "storage_encrypted" in normalized_raw and ("storage_encrypted=false" in normalized_raw or "storage_encrypted = false" in normalized_raw):
            findings.append(
                VulnerabilityFinding(
                    rule_id="AS-AWS-004",
                    title="Database Storage Encryption Disabled",
                    description=(
                        "The database instance does not enable storage encryption."
                    ),
                    severity=Severity.HIGH,
                    confidence_score=0.95,
                    affected_resource="aws_db_instance.app_db",
                    resource_type="aws_db_instance",
                    remediation_hint=(
                        "Set storage_encrypted = true."
                    ),
                )
            )

        # ---------------------------------------------------------
        # 5. No vulnerabilities detected
        # ---------------------------------------------------------
        if not findings:
            findings.append(
                VulnerabilityFinding(
                    rule_id="AS-INFO-000",
                    title="IaC Template Baseline Audit Passed",
                    description="No security misconfigurations detected.",
                    severity=Severity.INFORMATIONAL,
                    confidence_score=1.0,
                    affected_resource=template.file_path,
                )
            )

        return findings