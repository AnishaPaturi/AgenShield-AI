"""Calibrated consensus engine for Multi-LLM ensembles (Task 3.2).

Single source of truth for the consensus pipeline:

    per-model findings
        -> cross-model clustering            (consensus.matching)
        -> mathematical agreement scoring    (consensus.agreement)
        -> weighted ensemble confidence      (this module)
        -> calibration mapping               (consensus.calibration)
        -> auto-patch / human-review routing (this module)

Confidence formulation:

    w_i         = (1 - gamma) / N_total
    C_ensemble  = sum_{i in agreed} (w_i * C_i)
                  + gamma * S_agreement * (N_agreed / N_total)
    C_final     = calibrator(C_ensemble)

The first term rewards models that are individually confident; the second
rewards models that agree *with each other*. The ``N_agreed / N_total`` factor
is what eliminates single-model hallucinations: a finding only one of two
models raised cannot exceed ``0.45 * C + 0.05``, which is structurally below
the 0.85 auto-patch threshold no matter how confident that one model was.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from agentshield.core.consensus.agreement import (
    AgreementBreakdown,
    compute_agreement,
)
from agentshield.core.consensus.calibration import ConfidenceCalibrator
from agentshield.core.consensus.matching import (
    DEFAULT_MAX_SEVERITY_GAP,
    DEFAULT_SEMANTIC_THRESHOLD,
    FindingCluster,
    ModelFindings,
    cluster_findings,
)
from agentshield.core.schemas.vulnerability import (
    AUTO_PATCH_THRESHOLD,
    ComplianceMapping,
    Severity,
    VulnerabilityFinding,
)

# Weight given to the inter-model agreement bonus in the confidence formula.
DEFAULT_GAMMA: float = 0.10

# Consensus score below which the audit queue flags outright model
# disagreement (distinct from merely low confidence).
NON_CONSENSUS_THRESHOLD: float = 0.80

_SEVERITY_ORDER: tuple[Severity, ...] = (
    Severity.CRITICAL,
    Severity.HIGH,
    Severity.MEDIUM,
    Severity.LOW,
    Severity.INFORMATIONAL,
)


@dataclass
class ConsensusConfig:
    """Tunable parameters of the consensus algorithm."""

    gamma: float = DEFAULT_GAMMA
    auto_patch_threshold: float = AUTO_PATCH_THRESHOLD
    semantic_threshold: float = DEFAULT_SEMANTIC_THRESHOLD
    max_severity_gap: int = DEFAULT_MAX_SEVERITY_GAP
    model_weights: dict[str, float] | None = None
    signal_weights: dict[str, float] | None = None


@dataclass
class ConsensusOutcome:
    """Result of reconciling one cluster into a single consensus finding."""

    finding: VulnerabilityFinding
    raw_confidence: float
    calibrated_confidence: float
    agreement: AgreementBreakdown
    agreed_models: list[str] = field(default_factory=list)
    total_models: int = 0
    auto_patchable: bool = False
    requires_human_review: bool = True
    escalation_reason: str | None = None

    @property
    def agreement_ratio(self) -> float:
        """Fraction of ensemble models that independently raised this finding."""
        if self.total_models <= 0:
            return 0.0
        return len(self.agreed_models) / self.total_models


def evaluate_routing(
    confidence_score: float, threshold: float = AUTO_PATCH_THRESHOLD
) -> tuple[bool, bool, str | None]:
    """Route a finding by confidence threshold.

    Returns ``(auto_patchable, requires_human_review, escalation_reason)``.
    C >= 0.85 is auto-patchable; anything below escalates to the human
    security audit queue built in Task 3.4.
    """
    if confidence_score >= threshold:
        return True, False, None
    escalation_reason = (
        f"Confidence score {confidence_score:.4f} is below auto-patch threshold "
        f"{threshold:.2f}; escalated to human review queue to prevent potential "
        "hallucination."
    )
    return False, True, escalation_reason


def calculate_calibrated_confidence(
    model_confidences: list[float],
    total_models: int,
    agreement_score: float = 1.0,
    gamma: float = DEFAULT_GAMMA,
    weights: list[float] | None = None,
) -> float:
    """Compute C_ensemble for one cluster.

    Worked examples with gamma = 0.10 and two models:

    * Both models agree at C = 0.90:
      ``0.45(0.90) + 0.45(0.90) + 0.10(1.0)(2/2) = 0.9100`` -> auto-patch.
    * Only one of two models flags it at C = 0.90:
      ``0.45(0.90) + 0.10(1.0)(1/2) = 0.4550`` -> human review.
    """
    if not model_confidences or total_models <= 0:
        return 0.0

    # A single-model deployment has no cross-model evidence to combine; the
    # model's own confidence is the best estimate available.
    if total_models == 1:
        return round(min(1.0, max(0.0, model_confidences[0])), 4)

    num_agreed = len(model_confidences)
    if weights and len(weights) == num_agreed:
        weighted_sum = sum(w * c for w, c in zip(weights, model_confidences, strict=True))
    else:
        uniform_weight = (1.0 - gamma) / total_models
        weighted_sum = sum(uniform_weight * c for c in model_confidences)

    agreement_bonus = gamma * agreement_score * (num_agreed / total_models)
    return round(min(1.0, max(0.0, weighted_sum + agreement_bonus)), 4)


class ConsensusEngine:
    """Reconciles Multi-LLM ensemble output into calibrated consensus findings."""

    def __init__(
        self,
        config: ConsensusConfig | None = None,
        calibrator: ConfidenceCalibrator | None = None,
    ) -> None:
        self.config = config or ConsensusConfig()
        # Identity by default: an unfitted pipeline reproduces the raw formula.
        self.calibrator = calibrator or ConfidenceCalibrator()

    def reconcile(
        self,
        model_findings: list[ModelFindings],
        total_models: int | None = None,
    ) -> list[ConsensusOutcome]:
        """Cluster, score, calibrate, and route every finding in the ensemble."""
        n_total = total_models if total_models is not None else len(model_findings)
        clusters = cluster_findings(
            model_findings,
            semantic_threshold=self.config.semantic_threshold,
            max_severity_gap=self.config.max_severity_gap,
        )
        return [self._reconcile_cluster(c, n_total) for c in clusters]

    def _reconcile_cluster(
        self, cluster: FindingCluster, total_models: int
    ) -> ConsensusOutcome:
        agreement = compute_agreement(
            cluster.findings, weights=self.config.signal_weights
        )
        confidences = [f.confidence_score for f in cluster.findings]
        weights = self._resolve_weights(cluster.model_names)

        raw_confidence = calculate_calibrated_confidence(
            confidences,
            total_models=total_models,
            agreement_score=agreement.score,
            gamma=self.config.gamma,
            weights=weights,
        )
        calibrated = self.calibrator.apply(raw_confidence)

        finding = self._merge_findings(cluster)
        finding.confidence_score = calibrated
        finding.consensus_score = calibrated
        finding.model_agreements = list(cluster.model_names)

        auto_patchable, requires_review, escalation_reason = evaluate_routing(
            calibrated, self.config.auto_patch_threshold
        )
        finding.auto_patchable = auto_patchable
        finding.requires_human_review = requires_review
        finding.escalation_reason = escalation_reason

        finding.raw_details["consensus"] = {
            "raw_confidence": raw_confidence,
            "calibrated_confidence": calibrated,
            "calibrator_fitted": self.calibrator.fitted,
            "gamma": self.config.gamma,
            "agreed_models": list(cluster.model_names),
            "total_models": total_models,
            "agreement_ratio": round(len(cluster.model_names) / total_models, 4)
            if total_models
            else 0.0,
            "match_reasons": list(cluster.match_reasons),
            "agreement": agreement.as_dict(),
            "per_model_confidence": dict(zip(cluster.model_names, confidences, strict=True)),
        }

        return ConsensusOutcome(
            finding=finding,
            raw_confidence=raw_confidence,
            calibrated_confidence=calibrated,
            agreement=agreement,
            agreed_models=list(cluster.model_names),
            total_models=total_models,
            auto_patchable=auto_patchable,
            requires_human_review=requires_review,
            escalation_reason=escalation_reason,
        )

    def _resolve_weights(self, model_names: list[str]) -> list[float] | None:
        """Per-model weights, when the deployment configures them."""
        if not self.config.model_weights:
            return None
        configured = self.config.model_weights
        if not any(name in configured for name in model_names):
            return None
        # Fall back to the uniform weight for any model without an override.
        uniform = (1.0 - self.config.gamma) / max(1, len(model_names))
        return [configured.get(name, uniform) for name in model_names]

    def _merge_findings(self, cluster: FindingCluster) -> VulnerabilityFinding:
        """Fold a cluster into one finding, keeping the union of evidence.

        The highest-confidence model supplies the narrative fields; severity is
        resolved by majority vote with ties broken toward the more severe
        level, so one model downplaying a critical issue cannot silently
        lower it.
        """
        ordered = sorted(
            cluster.findings, key=lambda f: f.confidence_score, reverse=True
        )
        base = ordered[0].model_copy(deep=True)
        base.severity = self._resolve_severity(cluster.findings)

        # Union compliance mappings across models, de-duplicated.
        seen: set[tuple[str, str]] = set()
        merged: list[ComplianceMapping] = []
        for finding in ordered:
            for mapping in finding.compliance_mappings:
                key = (str(mapping.framework), mapping.control_id)
                if key not in seen:
                    seen.add(key)
                    merged.append(mapping)
        base.compliance_mappings = merged

        # Prefer any line range a model did supply.
        if base.line_range is None:
            for finding in ordered:
                if finding.line_range is not None:
                    base.line_range = finding.line_range
                    break

        if not base.remediation_hint:
            for finding in ordered:
                if finding.remediation_hint:
                    base.remediation_hint = finding.remediation_hint
                    break

        return base

    @staticmethod
    def _resolve_severity(findings: list[VulnerabilityFinding]) -> Severity:
        """Majority-vote severity, ties broken toward the more severe level."""
        counts: dict[Severity, int] = {}
        for finding in findings:
            counts[finding.severity] = counts.get(finding.severity, 0) + 1
        top = max(counts.values())
        tied = [sev for sev, count in counts.items() if count == top]
        for severity in _SEVERITY_ORDER:
            if severity in tied:
                return severity
        return findings[0].severity
