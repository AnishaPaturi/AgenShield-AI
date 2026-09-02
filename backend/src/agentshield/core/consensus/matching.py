"""Cross-model finding matching for ensemble consensus (Task 3.2).

Grouping ensemble output by exact ``rule_id`` equality does not work in
practice: GPT-4o may report ``CKV_AWS_20`` where Claude reports
``AS-AWS-001`` for the identical misconfiguration. Under exact matching both
are seen as single-model findings and *both* get escalated, which defeats the
purpose of the ensemble.

This module clusters findings that refer to the same underlying vulnerability
using canonical rule families, normalized resource identity, and semantic
similarity, subject to the invariant that a cluster holds at most one finding
per model (so ``N_agreed <= N_total`` always holds).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from agentshield.core.consensus.normalization import (
    normalize_resource,
    normalize_rule_id,
    severity_distance,
    text_similarity,
)
from agentshield.core.schemas.vulnerability import VulnerabilityFinding

# Minimum title+description token overlap for two findings on the same
# resource to be considered the same vulnerability.
DEFAULT_SEMANTIC_THRESHOLD: float = 0.45

# Models are allowed to disagree by at most one severity level and still be
# treated as describing the same issue.
DEFAULT_MAX_SEVERITY_GAP: int = 1


@dataclass
class ModelFindings:
    """Findings produced by one model (one ensemble slot).

    ``model_id`` is the *identity* used to enforce the one-finding-per-model
    invariant and must be unique across the ensemble; it defaults to
    ``model_name``. ``model_name`` is the human-facing label recorded in
    ``model_agreements``. The two differ when an ensemble runs several clients
    that share a configured model name, or when a model self-reports a more
    specific identifier than its client config carries.
    """

    model_name: str
    findings: list[VulnerabilityFinding] = field(default_factory=list)
    model_id: str | None = None

    @property
    def identity(self) -> str:
        """Unique slot identifier for this model within the ensemble."""
        return self.model_id or self.model_name


@dataclass
class FindingCluster:
    """A set of findings from distinct models describing one vulnerability."""

    findings: list[VulnerabilityFinding] = field(default_factory=list)
    model_names: list[str] = field(default_factory=list)
    model_ids: list[str] = field(default_factory=list)
    match_reasons: list[str] = field(default_factory=list)

    @property
    def size(self) -> int:
        """Number of distinct models that reported this vulnerability."""
        return len(self.findings)

    def signature(self) -> tuple[str, str]:
        """Canonical ``(rule family, resource)`` key of the first finding."""
        head = self.findings[0]
        return (
            normalize_rule_id(head.rule_id),
            normalize_resource(head.affected_resource),
        )


def _exact_signature(finding: VulnerabilityFinding) -> tuple[str, str]:
    return (
        normalize_rule_id(finding.rule_id),
        normalize_resource(finding.affected_resource),
    )


def _semantic_match_score(
    candidate: VulnerabilityFinding,
    cluster: FindingCluster,
    semantic_threshold: float,
    max_severity_gap: int,
) -> float | None:
    """Score a candidate against a cluster, or ``None`` if it cannot join.

    A candidate joins only when it agrees on the normalized resource, stays
    within ``max_severity_gap`` severity levels, and clears the semantic
    similarity threshold against *every* member of the cluster.
    """
    candidate_resource = normalize_resource(candidate.affected_resource)
    similarities: list[float] = []

    for member in cluster.findings:
        if normalize_resource(member.affected_resource) != candidate_resource:
            return None
        if severity_distance(candidate.severity, member.severity) > max_severity_gap:
            return None

        similarity = text_similarity(
            f"{candidate.title} {candidate.description}",
            f"{member.title} {member.description}",
        )
        if similarity < semantic_threshold:
            return None
        similarities.append(similarity)

    if not similarities:
        return None
    return sum(similarities) / len(similarities)


def cluster_findings(
    model_findings: list[ModelFindings],
    semantic_threshold: float = DEFAULT_SEMANTIC_THRESHOLD,
    max_severity_gap: int = DEFAULT_MAX_SEVERITY_GAP,
) -> list[FindingCluster]:
    """Group findings across models into per-vulnerability clusters.

    Two-pass greedy assignment, deterministic in model and finding order:

    1. **Exact pass** -- match on the canonical ``(rule family, resource)``
       signature. This is the fast path and covers models that happen to share
       a rule taxonomy.
    2. **Semantic pass** -- for anything still unmatched, join the
       best-scoring compatible cluster based on resource identity, severity
       proximity, and prose overlap.

    A model never contributes two findings to the same cluster, so the cluster
    size is exactly the number of models that independently agreed.
    """
    clusters: list[FindingCluster] = []
    signature_index: dict[tuple[str, str], list[int]] = {}

    for model in model_findings:
        for finding in model.findings:
            signature = _exact_signature(finding)
            placed = False

            # Pass 1: canonical signature match.
            for idx in signature_index.get(signature, []):
                if model.identity in clusters[idx].model_ids:
                    continue
                clusters[idx].findings.append(finding)
                clusters[idx].model_names.append(model.model_name)
                clusters[idx].model_ids.append(model.identity)
                clusters[idx].match_reasons.append("exact_signature")
                placed = True
                break

            # Pass 2: semantic match against existing clusters.
            if not placed:
                best_idx: int | None = None
                best_score = 0.0
                for idx, cluster in enumerate(clusters):
                    if model.identity in cluster.model_ids:
                        continue
                    score = _semantic_match_score(
                        finding, cluster, semantic_threshold, max_severity_gap
                    )
                    if score is not None and score > best_score:
                        best_idx, best_score = idx, score

                if best_idx is not None:
                    clusters[best_idx].findings.append(finding)
                    clusters[best_idx].model_names.append(model.model_name)
                    clusters[best_idx].model_ids.append(model.identity)
                    clusters[best_idx].match_reasons.append(
                        f"semantic:{best_score:.4f}"
                    )
                    placed = True

            # Otherwise this is a new, so-far unique vulnerability.
            if not placed:
                clusters.append(
                    FindingCluster(
                        findings=[finding],
                        model_names=[model.model_name],
                        model_ids=[model.identity],
                        match_reasons=["new"],
                    )
                )
                signature_index.setdefault(signature, []).append(len(clusters) - 1)

    return clusters
