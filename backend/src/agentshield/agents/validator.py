"""Code & Sandbox Validator Agent for AgentShield AI.

Executes static syntax and configuration verification across multi-cloud IaC templates
using static verification tools:
- terraform validate
- tflint
- cfn-lint
- kube-linter
- helm lint

Enforces automated rollback and re-remediation loops with the Remediation Agent
whenever static lint errors are detected in generated patches.
"""

from __future__ import annotations

import logging
from typing import Any

from agentshield.agents.remediator import RemediationAgent
from agentshield.core.schemas import (
    IaCTemplate,
    IaCType,
    PatchDiff,
    RemediationStatus,
    Severity,
    ValidationCheckResult,
    VulnerabilityFinding,
    VulnerabilityReport,
)
from agentshield.validation import (
    BaseLinter,
    apply_patch_to_content,
    get_linters_for_iac_type,
)

logger = logging.getLogger("agentshield.agents.validator")


class ValidatorAgent:
    """Specialized Code & Sandbox Validator Agent executing static lint verification and rollback."""

    def __init__(
        self,
        custom_linters: dict[IaCType | str, list[BaseLinter]] | None = None,
    ) -> None:
        self.custom_linters = custom_linters or {}

    def get_linters(self, iac_type: IaCType | str) -> list[BaseLinter]:
        """Retrieve registered static linters for the given IaC type."""
        iac_key = iac_type if isinstance(iac_type, IaCType) else IaCType(str(iac_type).lower())
        if iac_key in self.custom_linters:
            return self.custom_linters[iac_key]
        if str(iac_type).lower() in self.custom_linters:
            return self.custom_linters[str(iac_type).lower()]
        return get_linters_for_iac_type(iac_type)

    def validate_patch(
        self,
        template: IaCTemplate,
        patch: PatchDiff,
        finding: VulnerabilityFinding | None = None,
        remediator: RemediationAgent | None = None,
        max_retries: int = 2,
    ) -> PatchDiff:
        """Validate a single PatchDiff against static linters with automated rollback and retry.

        Args:
            template: The target IaCTemplate.
            patch: The proposed candidate PatchDiff.
            finding: The corresponding VulnerabilityFinding.
            remediator: Optional RemediationAgent instance for error-correction rollback.
            max_retries: Maximum number of re-remediation attempts before failing.

        Returns:
            PatchDiff: Validated (or marked as failed) patch diff.
        """
        # 1. Apply candidate patch to produce candidate file content
        candidate_content, applied = apply_patch_to_content(template.raw_content, patch)
        if not applied:
            logger.warning(
                "Failed to apply patch %s to template %s: snippet not found.",
                patch.patch_id,
                template.file_path,
            )
            patch.validation_results = [
                ValidationCheckResult(
                    check_name="patch_apply",
                    passed=False,
                    output="",
                    error="Failed to match patch original_code block in template raw content.",
                )
            ]
            patch.remediation_status = RemediationStatus.FAILED
            patch.requires_human_review = True
            return patch

        # 2. Run static linters for this template's IaC type
        linters = self.get_linters(template.iac_type)
        results: list[ValidationCheckResult] = []

        for linter in linters:
            res = linter.validate(candidate_content, file_path=template.file_path)
            results.append(res)

        patch.validation_results = results
        all_passed = all(r.passed for r in results)

        if all_passed:
            patch.remediation_status = RemediationStatus.SYNTAX_VALIDATED
            logger.info(
                "Patch %s PASSED static lint checks: %s",
                patch.patch_id,
                [r.check_name for r in results],
            )
            return patch

        # 3. Handle Lint Failure: Enforce Automated Rollback & Re-Remediation Loop
        failed_checks = [r for r in results if not r.passed]
        lint_errors = [f"{r.check_name}: {r.error or r.output}" for r in failed_checks]
        logger.warning(
            "Patch %s FAILED static lint checks: %s. Executing automated rollback.",
            patch.patch_id,
            lint_errors,
        )

        # Candidate content is rolled back (discarded)
        if remediator is not None and max_retries > 0:
            logger.info(
                "Initiating automated rollback to RemediationAgent for patch %s (retries left: %d)",
                patch.patch_id,
                max_retries,
            )
            target_finding = finding
            if target_finding is None:
                target_finding = VulnerabilityFinding(
                    finding_id=patch.finding_id,
                    rule_id="LINT_ERROR_REPAIR",
                    title="Automated Linter Repair",
                    description="; ".join(lint_errors),
                    severity=Severity.HIGH,
                    affected_resource=patch.target_resource,
                )

            # Re-remediate patch with linter error feedback
            repaired_patch = remediator.re_remediate(
                template=template,
                finding=target_finding,
                failed_patch=patch,
                lint_errors=lint_errors,
            )

            # Recursively validate repaired patch
            return self.validate_patch(
                template=template,
                patch=repaired_patch,
                finding=target_finding,
                remediator=remediator,
                max_retries=max_retries - 1,
            )

        # Retries exhausted or no remediator available
        logger.warning(
            "Patch %s failed lint checks and all retries exhausted. Marking as FAILED and escalating to human review.",
            patch.patch_id,
        )
        patch.remediation_status = RemediationStatus.FAILED
        patch.requires_human_review = True
        return patch

    def validate_patches(
        self,
        template: IaCTemplate,
        patches: list[PatchDiff],
        report: VulnerabilityReport | None = None,
        remediator: RemediationAgent | None = None,
        max_retries: int = 2,
    ) -> list[PatchDiff]:
        """Validate all generated patches for an IaCTemplate."""
        finding_map: dict[str, VulnerabilityFinding] = {}
        if report and report.findings:
            finding_map = {f.finding_id: f for f in report.findings}

        validated_list: list[PatchDiff] = []
        for patch in patches:
            finding = finding_map.get(patch.finding_id)
            val_patch = self.validate_patch(
                template=template,
                patch=patch,
                finding=finding,
                remediator=remediator,
                max_retries=max_retries,
            )
            validated_list.append(val_patch)

        return validated_list


# Alias for compatibility with architecture papers and docs
CodeSandboxValidatorAgent = ValidatorAgent
