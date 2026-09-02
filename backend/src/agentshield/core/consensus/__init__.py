"""Calibrated Confidence Scoring & Consensus Algorithm (Task 3.2).

Public surface of the consensus layer that turns raw Multi-LLM ensemble
output into calibrated, routable security findings.
"""

from agentshield.core.consensus.agreement import (
    DEFAULT_SIGNAL_WEIGHTS,
    AgreementBreakdown,
    compute_agreement,
    location_agreement,
    resource_agreement,
    semantic_agreement,
    severity_agreement,
)
from agentshield.core.consensus.calibration import (
    CalibrationReport,
    ConfidenceCalibrator,
    ReliabilityBin,
    brier_score,
    expected_calibration_error,
    reliability_bins,
)
from agentshield.core.consensus.engine import (
    DEFAULT_GAMMA,
    NON_CONSENSUS_THRESHOLD,
    ConsensusConfig,
    ConsensusEngine,
    ConsensusOutcome,
    calculate_calibrated_confidence,
    evaluate_routing,
)
from agentshield.core.consensus.matching import (
    DEFAULT_MAX_SEVERITY_GAP,
    DEFAULT_SEMANTIC_THRESHOLD,
    FindingCluster,
    ModelFindings,
    cluster_findings,
)
from agentshield.core.consensus.normalization import (
    MAX_SEVERITY_DISTANCE,
    SEVERITY_RANK,
    interval_jaccard,
    jaccard,
    normalize_resource,
    normalize_rule_id,
    severity_distance,
    text_similarity,
    tokenize,
)

__all__ = [
    # engine
    "ConsensusEngine",
    "ConsensusConfig",
    "ConsensusOutcome",
    "calculate_calibrated_confidence",
    "evaluate_routing",
    "DEFAULT_GAMMA",
    "NON_CONSENSUS_THRESHOLD",
    # matching
    "ModelFindings",
    "FindingCluster",
    "cluster_findings",
    "DEFAULT_SEMANTIC_THRESHOLD",
    "DEFAULT_MAX_SEVERITY_GAP",
    # agreement
    "AgreementBreakdown",
    "compute_agreement",
    "severity_agreement",
    "resource_agreement",
    "semantic_agreement",
    "location_agreement",
    "DEFAULT_SIGNAL_WEIGHTS",
    # calibration
    "ConfidenceCalibrator",
    "CalibrationReport",
    "ReliabilityBin",
    "expected_calibration_error",
    "brier_score",
    "reliability_bins",
    # normalization
    "normalize_resource",
    "normalize_rule_id",
    "tokenize",
    "jaccard",
    "text_similarity",
    "severity_distance",
    "interval_jaccard",
    "SEVERITY_RANK",
    "MAX_SEVERITY_DISTANCE",
]
