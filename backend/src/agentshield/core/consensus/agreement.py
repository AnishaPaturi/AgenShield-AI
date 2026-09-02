"""Mathematical agreement scoring between LLM outputs (Task 3.2).

Agreement is decomposed into four independent signals, each normalized to
[0.0, 1.0]. Signals that cannot be computed for a given cluster (for example
line ranges the models did not emit) are *excluded* rather than defaulted, and
the remaining weights are renormalized. This keeps the score meaningful under
partial information instead of silently collapsing to a constant.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from itertools import combinations

from agentshield.core.consensus.normalization import (
    MAX_SEVERITY_DISTANCE,
    interval_jaccard,
    normalize_resource,
    severity_distance,
    text_similarity,
)
from agentshield.core.schemas.vulnerability import VulnerabilityFinding

# Relative importance of each agreement signal. Renormalized over whichever
# signals are actually computable for a cluster.
DEFAULT_SIGNAL_WEIGHTS: dict[str, float] = {
    "severity": 0.30,
    "resource": 0.25,
    "semantic": 0.25,
    "location": 0.20,
}


@dataclass(frozen=True)
class AgreementBreakdown:
    """Per-signal decomposition of a cluster's agreement score."""

    score: float
    signals: dict[str, float] = field(default_factory=dict)
    weights: dict[str, float] = field(default_factory=dict)
    model_count: int = 0

    def as_dict(self) -> dict[str, object]:
        """Serializable view for embedding in finding diagnostics."""
        return {
            "score": self.score,
            "signals": {k: round(v, 4) for k, v in self.signals.items()},
            "weights": {k: round(v, 4) for k, v in self.weights.items()},
            "model_count": self.model_count,
        }


def _pairwise_mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 1.0


def severity_agreement(findings: list[VulnerabilityFinding]) -> float:
    """1.0 when every model assigned the same severity, decaying with distance."""
    scores = [
        1.0 - (severity_distance(a.severity, b.severity) / MAX_SEVERITY_DISTANCE)
        for a, b in combinations(findings, 2)
    ]
    return _pairwise_mean(scores)


def resource_agreement(findings: list[VulnerabilityFinding]) -> float:
    """Exact-match rate on the canonicalized affected resource identifier."""
    scores = [
        1.0
        if normalize_resource(a.affected_resource)
        == normalize_resource(b.affected_resource)
        else 0.0
        for a, b in combinations(findings, 2)
    ]
    return _pairwise_mean(scores)


def semantic_agreement(findings: list[VulnerabilityFinding]) -> float:
    """Token-set overlap of the title + description prose across models."""
    scores = [
        text_similarity(
            f"{a.title} {a.description}",
            f"{b.title} {b.description}",
        )
        for a, b in combinations(findings, 2)
    ]
    return _pairwise_mean(scores)


def location_agreement(findings: list[VulnerabilityFinding]) -> float | None:
    """Mean pairwise Jaccard overlap of source line ranges.

    Returns ``None`` when any model omitted a line range, signalling that this
    dimension is not measurable and must be excluded from the weighted mean.
    """
    ranges = [f.line_range for f in findings if f.line_range is not None]
    if len(ranges) < len(findings):
        return None

    scores = [
        interval_jaccard(
            (a.start_line, a.end_line),
            (b.start_line, b.end_line),
        )
        for a, b in combinations(ranges, 2)
    ]
    return _pairwise_mean(scores)


def compute_agreement(
    findings: list[VulnerabilityFinding],
    weights: dict[str, float] | None = None,
) -> AgreementBreakdown:
    """Compute the composite agreement score S_agreement for one cluster.

    Formulation:
        S_agreement = sum_k(w_k * s_k) / sum_k(w_k)   over computable signals k

    A cluster containing a single model's finding has no cross-model evidence
    to weigh, so its agreement is vacuously 1.0. The hallucination penalty for
    such findings is applied separately by the ``N_agreed / N_total`` term of
    the calibrated confidence formula, not here -- keeping "how much do the
    models that flagged this agree?" distinct from "how many models flagged
    it at all?".
    """
    if len(findings) <= 1:
        return AgreementBreakdown(
            score=1.0,
            signals={},
            weights={},
            model_count=len(findings),
        )

    base_weights = weights or DEFAULT_SIGNAL_WEIGHTS
    signals: dict[str, float] = {
        "severity": severity_agreement(findings),
        "resource": resource_agreement(findings),
        "semantic": semantic_agreement(findings),
    }

    location = location_agreement(findings)
    if location is not None:
        signals["location"] = location

    active_weights = {
        k: base_weights.get(k, 0.0) for k in signals if base_weights.get(k, 0.0) > 0.0
    }
    total_weight = sum(active_weights.values())
    if total_weight <= 0.0:
        return AgreementBreakdown(
            score=1.0, signals=signals, weights={}, model_count=len(findings)
        )

    score = sum(active_weights[k] * signals[k] for k in active_weights) / total_weight

    return AgreementBreakdown(
        score=round(min(1.0, max(0.0, score)), 4),
        signals=signals,
        weights={k: v / total_weight for k, v in active_weights.items()},
        model_count=len(findings),
    )
