"""Tests for cross-model matching and the calibrated consensus engine (Task 3.2)."""

import pytest

from agentshield.core.consensus import (
    NON_CONSENSUS_THRESHOLD,
    ConfidenceCalibrator,
    ConsensusConfig,
    ConsensusEngine,
    ModelFindings,
    calculate_calibrated_confidence,
    cluster_findings,
    evaluate_routing,
)
from agentshield.core.schemas import (
    AUTO_PATCH_THRESHOLD,
    ComplianceFramework,
    ComplianceMapping,
    LineRange,
    Severity,
    VulnerabilityFinding,
)

PUBLIC_BUCKET_TITLE = "S3 bucket allows public read access"
PUBLIC_BUCKET_DESC = "The S3 bucket ACL is set to public-read exposing objects publicly."


def _finding(**overrides) -> VulnerabilityFinding:
    payload = {
        "rule_id": "AS-AWS-001",
        "title": PUBLIC_BUCKET_TITLE,
        "description": PUBLIC_BUCKET_DESC,
        "severity": Severity.HIGH,
        "confidence_score": 0.90,
        "affected_resource": "aws_s3_bucket.data_bucket",
    }
    payload.update(overrides)
    return VulnerabilityFinding(**payload)


# --------------------------------------------------------------------------
# Cross-model matching
# --------------------------------------------------------------------------


def test_exact_signature_match_groups_identical_rule_ids():
    clusters = cluster_findings(
        [
            ModelFindings("gpt-4o", [_finding()]),
            ModelFindings("claude-3-5-sonnet", [_finding()]),
        ]
    )
    assert len(clusters) == 1
    assert clusters[0].size == 2
    assert clusters[0].match_reasons == ["new", "exact_signature"]


def test_semantic_match_groups_divergent_rule_ids():
    """The defect this engine exists to fix: two models describing the same
    vulnerability with different rule taxonomies must reach consensus."""
    clusters = cluster_findings(
        [
            ModelFindings("gpt-4o", [_finding(rule_id="CKV_AWS_20")]),
            ModelFindings(
                "claude-3-5-sonnet",
                [
                    _finding(
                        rule_id="AS-AWS-001",
                        title="Public S3 bucket read ACL",
                        description="Bucket grants public read access to all objects via ACL.",
                        affected_resource="resource.aws_s3_bucket.data_bucket",
                    )
                ],
            ),
        ]
    )
    assert len(clusters) == 1
    assert clusters[0].size == 2
    assert clusters[0].match_reasons[1].startswith("semantic:")


def test_different_resources_never_merge():
    clusters = cluster_findings(
        [
            ModelFindings("gpt-4o", [_finding(affected_resource="aws_s3_bucket.a")]),
            ModelFindings("claude", [_finding(affected_resource="aws_s3_bucket.b")]),
        ]
    )
    assert len(clusters) == 2


def test_unrelated_findings_on_same_resource_never_merge():
    clusters = cluster_findings(
        [
            ModelFindings("gpt-4o", [_finding(rule_id="CKV_AWS_20")]),
            ModelFindings(
                "claude",
                [
                    _finding(
                        rule_id="CKV_AWS_19",
                        title="Bucket versioning disabled",
                        description="Versioning is not enabled so deletions are unrecoverable.",
                    )
                ],
            ),
        ]
    )
    assert len(clusters) == 2


def test_wide_severity_disagreement_blocks_merge():
    clusters = cluster_findings(
        [
            ModelFindings("gpt-4o", [_finding(rule_id="CKV_AWS_20", severity=Severity.CRITICAL)]),
            ModelFindings(
                "claude",
                [_finding(rule_id="AS-AWS-001", severity=Severity.INFORMATIONAL)],
            ),
        ]
    )
    # Same prose, but a 4-level severity gap means these are not the same call.
    assert len(clusters) == 2


def test_one_model_never_contributes_twice_to_a_cluster():
    """Guarantees N_agreed <= N_total, so the agreement ratio stays a ratio."""
    clusters = cluster_findings(
        [ModelFindings("gpt-4o", [_finding(), _finding()])]
    )
    assert len(clusters) == 2
    assert all(c.size == 1 for c in clusters)


def test_model_identity_is_the_slot_not_the_label():
    """Two clients sharing a configured model name are still distinct voters."""
    clusters = cluster_findings(
        [
            ModelFindings("gpt-4o", [_finding()], model_id="slot0"),
            ModelFindings("gpt-4o", [_finding()], model_id="slot1"),
        ]
    )
    assert len(clusters) == 1
    assert clusters[0].size == 2


def test_clustering_is_deterministic():
    def build():
        return [
            ModelFindings("gpt-4o", [_finding(rule_id="CKV_AWS_20")]),
            ModelFindings("claude", [_finding(rule_id="AS-AWS-001")]),
            ModelFindings("llama", [_finding(rule_id="OTHER-1", affected_resource="aws_db.x")]),
        ]

    first = [c.signature() for c in cluster_findings(build())]
    second = [c.signature() for c in cluster_findings(build())]
    assert first == second


def test_empty_ensemble_produces_no_clusters():
    assert cluster_findings([]) == []
    assert cluster_findings([ModelFindings("gpt-4o", [])]) == []


# --------------------------------------------------------------------------
# Confidence formula
# --------------------------------------------------------------------------


def test_full_agreement_clears_auto_patch_threshold():
    # 0.45(0.90) + 0.45(0.95) + 0.10(1.0)(2/2) = 0.9325
    score = calculate_calibrated_confidence([0.90, 0.95], total_models=2)
    assert score == 0.9325
    assert score >= AUTO_PATCH_THRESHOLD


def test_single_model_finding_cannot_reach_threshold():
    """Structural guarantee: with two models, a lone vote is capped at
    0.45(1.0) + 0.05 = 0.50, far below the 0.85 auto-patch threshold."""
    for confidence in (0.5, 0.9, 0.99, 1.0):
        score = calculate_calibrated_confidence([confidence], total_models=2)
        assert score < AUTO_PATCH_THRESHOLD
    assert calculate_calibrated_confidence([1.0], total_models=2) == 0.50


def test_low_agreement_reduces_confidence():
    high = calculate_calibrated_confidence([0.9, 0.9], total_models=2, agreement_score=1.0)
    low = calculate_calibrated_confidence([0.9, 0.9], total_models=2, agreement_score=0.2)
    assert low < high


def test_single_model_deployment_passes_confidence_through():
    assert calculate_calibrated_confidence([0.72], total_models=1) == 0.72


def test_degenerate_inputs_score_zero():
    assert calculate_calibrated_confidence([], total_models=2) == 0.0
    assert calculate_calibrated_confidence([0.9], total_models=0) == 0.0


def test_explicit_model_weights_are_honoured():
    weighted = calculate_calibrated_confidence(
        [0.9, 0.9], total_models=2, weights=[0.7, 0.2]
    )
    # 0.7(0.9) + 0.2(0.9) + 0.10 = 0.91
    assert weighted == pytest.approx(0.91)


def test_confidence_is_clamped_to_unit_interval():
    score = calculate_calibrated_confidence(
        [1.0, 1.0], total_models=2, weights=[5.0, 5.0]
    )
    assert score == 1.0


# --------------------------------------------------------------------------
# Threshold routing
# --------------------------------------------------------------------------


def test_routing_at_and_below_threshold():
    assert evaluate_routing(0.85) == (True, False, None)

    auto, review, reason = evaluate_routing(0.8499)
    assert auto is False
    assert review is True
    assert "below auto-patch threshold 0.85" in reason


def test_routing_honours_custom_threshold():
    assert evaluate_routing(0.70, threshold=0.60)[0] is True
    assert evaluate_routing(0.70, threshold=0.90)[0] is False


# --------------------------------------------------------------------------
# End-to-end engine
# --------------------------------------------------------------------------


def test_engine_reaches_consensus_across_rule_taxonomies():
    engine = ConsensusEngine()
    outcomes = engine.reconcile(
        [
            ModelFindings("gpt-4o", [_finding(rule_id="CKV_AWS_20", confidence_score=0.93)]),
            ModelFindings(
                "claude-3-5-sonnet",
                [
                    _finding(
                        rule_id="AS-AWS-001",
                        confidence_score=0.91,
                        title="Public S3 bucket read ACL",
                        description="Bucket grants public read access to all objects via ACL.",
                    )
                ],
            ),
        ]
    )

    assert len(outcomes) == 1
    outcome = outcomes[0]
    assert outcome.auto_patchable is True
    assert outcome.requires_human_review is False
    assert outcome.escalation_reason is None
    assert outcome.agreement_ratio == 1.0
    assert set(outcome.agreed_models) == {"gpt-4o", "claude-3-5-sonnet"}
    assert outcome.calibrated_confidence >= AUTO_PATCH_THRESHOLD


def test_engine_escalates_single_model_hallucination():
    engine = ConsensusEngine()
    outcomes = engine.reconcile(
        [
            ModelFindings("gpt-4o", [_finding(rule_id="AS-AWS-999", confidence_score=0.99)]),
            ModelFindings("claude-3-5-sonnet", []),
        ]
    )

    assert len(outcomes) == 1
    outcome = outcomes[0]
    assert outcome.auto_patchable is False
    assert outcome.requires_human_review is True
    assert "below auto-patch threshold" in outcome.escalation_reason
    assert outcome.agreement_ratio == 0.5
    # Also below the non-consensus threshold used by the Task 3.4 audit queue.
    assert outcome.calibrated_confidence < NON_CONSENSUS_THRESHOLD


def test_engine_counts_failed_models_in_the_denominator():
    """A model that returned nothing is not a model that agreed."""
    engine = ConsensusEngine()
    outcomes = engine.reconcile(
        [ModelFindings("gpt-4o", [_finding(confidence_score=0.95)])],
        total_models=2,
    )
    assert outcomes[0].total_models == 2
    assert outcomes[0].agreement_ratio == 0.5
    assert outcomes[0].requires_human_review is True


def test_engine_writes_consensus_diagnostics_onto_the_finding():
    engine = ConsensusEngine()
    outcome = engine.reconcile(
        [
            ModelFindings("gpt-4o", [_finding(confidence_score=0.93)]),
            ModelFindings("claude-3-5-sonnet", [_finding(confidence_score=0.91)]),
        ]
    )[0]

    diagnostics = outcome.finding.raw_details["consensus"]
    assert diagnostics["total_models"] == 2
    assert diagnostics["agreement_ratio"] == 1.0
    assert diagnostics["calibrator_fitted"] is False
    assert diagnostics["gamma"] == 0.10
    assert diagnostics["per_model_confidence"] == {
        "gpt-4o": 0.93,
        "claude-3-5-sonnet": 0.91,
    }
    assert diagnostics["agreement"]["signals"]["severity"] == 1.0


def test_engine_resolves_severity_by_majority_vote():
    engine = ConsensusEngine()
    outcome = engine.reconcile(
        [
            ModelFindings("a", [_finding(severity=Severity.HIGH)], model_id="s0"),
            ModelFindings("b", [_finding(severity=Severity.HIGH)], model_id="s1"),
            ModelFindings("c", [_finding(severity=Severity.MEDIUM)], model_id="s2"),
        ]
    )[0]
    assert outcome.finding.severity == Severity.HIGH


def test_engine_breaks_severity_ties_toward_the_more_severe_level():
    """One model downplaying an issue must not silently lower its severity."""
    engine = ConsensusEngine()
    outcome = engine.reconcile(
        [
            ModelFindings("a", [_finding(severity=Severity.MEDIUM)], model_id="s0"),
            ModelFindings("b", [_finding(severity=Severity.HIGH)], model_id="s1"),
        ]
    )[0]
    assert outcome.finding.severity == Severity.HIGH


def test_engine_merges_evidence_across_models():
    engine = ConsensusEngine()
    outcome = engine.reconcile(
        [
            ModelFindings(
                "gpt-4o",
                [
                    _finding(
                        confidence_score=0.95,
                        compliance_mappings=[
                            ComplianceMapping(
                                framework=ComplianceFramework.SOC2,
                                control_id="CC6.1",
                                title="Logical Access Controls",
                            )
                        ],
                    )
                ],
            ),
            ModelFindings(
                "claude-3-5-sonnet",
                [
                    _finding(
                        confidence_score=0.90,
                        line_range=LineRange(start_line=12, end_line=18),
                        remediation_hint="Set acl to private.",
                        compliance_mappings=[
                            ComplianceMapping(
                                framework=ComplianceFramework.PCI_DSS,
                                control_id="Requirement-1.3",
                                title="Restrict Public Access",
                            )
                        ],
                    )
                ],
            ),
        ]
    )[0]

    finding = outcome.finding
    # Union of compliance evidence, not just the top model's.
    assert len(finding.compliance_mappings) == 2
    # Evidence only one model supplied is still carried forward.
    assert finding.line_range is not None
    assert finding.line_range.start_line == 12
    assert finding.remediation_hint == "Set acl to private."


def test_engine_deduplicates_identical_compliance_mappings():
    mapping = ComplianceMapping(
        framework=ComplianceFramework.SOC2,
        control_id="CC6.1",
        title="Logical Access Controls",
    )
    engine = ConsensusEngine()
    outcome = engine.reconcile(
        [
            ModelFindings("a", [_finding(compliance_mappings=[mapping])], model_id="s0"),
            ModelFindings("b", [_finding(compliance_mappings=[mapping])], model_id="s1"),
        ]
    )[0]
    assert len(outcome.finding.compliance_mappings) == 1


def test_engine_does_not_mutate_the_input_findings():
    original = _finding(confidence_score=0.90)
    ConsensusEngine().reconcile(
        [
            ModelFindings("gpt-4o", [original], model_id="s0"),
            ModelFindings("claude", [_finding(confidence_score=0.95)], model_id="s1"),
        ]
    )
    assert original.confidence_score == 0.90
    assert original.consensus_score is None


def test_engine_applies_a_fitted_calibrator():
    calibrator = ConfidenceCalibrator().fit([0.95] * 20, [1] * 10 + [0] * 10)
    engine = ConsensusEngine(calibrator=calibrator)

    outcome = engine.reconcile(
        [
            ModelFindings("gpt-4o", [_finding(confidence_score=0.99)], model_id="s0"),
            ModelFindings("claude", [_finding(confidence_score=0.99)], model_id="s1"),
        ]
    )[0]

    # The calibrator was fitted on systematically over-confident data, so the
    # calibrated score must sit below the raw ensemble score.
    assert outcome.calibrated_confidence < outcome.raw_confidence
    assert outcome.finding.raw_details["consensus"]["calibrator_fitted"] is True


def test_engine_respects_a_custom_threshold():
    engine = ConsensusEngine(ConsensusConfig(auto_patch_threshold=0.95))
    outcome = engine.reconcile(
        [
            ModelFindings("a", [_finding(confidence_score=0.90)], model_id="s0"),
            ModelFindings("b", [_finding(confidence_score=0.90)], model_id="s1"),
        ]
    )[0]
    # C = 0.91, which clears 0.85 but not the stricter 0.95 gate.
    assert outcome.calibrated_confidence == 0.91
    assert outcome.auto_patchable is False


def test_engine_handles_an_empty_ensemble():
    assert ConsensusEngine().reconcile([]) == []
