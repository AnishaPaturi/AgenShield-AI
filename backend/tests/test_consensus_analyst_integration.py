"""End-to-end tests for Task 3.2 wired through the Security Analyst Agent.

Covers the full path an ensemble scan takes: parallel model calls, cross-model
consensus, calibrated confidence, threshold routing, and hand-off to the Task
3.4 human audit queue.
"""

import json

from agentshield.agents import SecurityAnalystAgent
from agentshield.core.audit import AuditQueueManager, EscalationReason
from agentshield.core.consensus import ConfidenceCalibrator, ConsensusEngine
from agentshield.core.llm import LLMClient, LLMConfig, MultiLLMEnsemble
from agentshield.core.schemas import AUTO_PATCH_THRESHOLD, IaCTemplate
from agentshield.core.schemas.contracts import AgentShieldWorkspace

PUBLIC_BUCKET_GPT = {
    "rule_id": "CKV_AWS_20",
    "title": "S3 bucket allows public read access",
    "description": "The S3 bucket ACL is set to public-read exposing objects publicly.",
    "severity": "HIGH",
    "confidence_score": 0.93,
    "affected_resource": "aws_s3_bucket.data_bucket",
}

# Same vulnerability, different rule taxonomy and phrasing.
PUBLIC_BUCKET_CLAUDE = {
    "rule_id": "AS-AWS-001",
    "title": "Public S3 bucket read ACL",
    "description": "Bucket grants public read access to all objects via ACL.",
    "severity": "HIGH",
    "confidence_score": 0.91,
    "affected_resource": "resource.aws_s3_bucket.data_bucket",
}


def _ensemble(*payloads: dict) -> MultiLLMEnsemble:
    """Build a two-model ensemble with distinct configured model names."""
    names = ["gpt-4o", "claude-3-5-sonnet-20241022"]
    clients = []
    for name, payload in zip(names, payloads, strict=True):
        client = LLMClient(LLMConfig(model_name=name))
        client.set_mock_responses([json.dumps(payload)])
        clients.append(client)
    return MultiLLMEnsemble(clients)


def test_models_reach_consensus_despite_different_rule_ids(
    sample_iac_template: IaCTemplate,
):
    """Regression: exact rule_id matching split one agreed vulnerability into
    two single-model findings and escalated both, defeating the ensemble."""
    ensemble = _ensemble(
        {"findings": [PUBLIC_BUCKET_GPT]},
        {"findings": [PUBLIC_BUCKET_CLAUDE]},
    )
    report = SecurityAnalystAgent(ensemble=ensemble).analyze(sample_iac_template)

    assert len(report.findings) == 1
    finding = report.findings[0]
    assert finding.confidence_score >= AUTO_PATCH_THRESHOLD
    assert finding.auto_patchable is True
    assert finding.requires_human_review is False
    assert set(finding.model_agreements) == {"gpt-4o", "claude-3-5-sonnet-20241022"}
    assert report.summary.auto_patchable_count == 1
    assert report.summary.human_review_count == 0


def test_disagreeing_models_produce_two_escalated_findings(
    sample_iac_template: IaCTemplate,
):
    """Genuinely different findings must stay separate and both escalate."""
    ensemble = _ensemble(
        {"findings": [PUBLIC_BUCKET_GPT]},
        {
            "findings": [
                {
                    "rule_id": "CKV_AWS_19",
                    "title": "Bucket versioning disabled",
                    "description": "Versioning is not enabled so deletions are unrecoverable.",
                    "severity": "MEDIUM",
                    "confidence_score": 0.88,
                    "affected_resource": "aws_s3_bucket.data_bucket",
                }
            ]
        },
    )
    report = SecurityAnalystAgent(ensemble=ensemble).analyze(sample_iac_template)

    assert len(report.findings) == 2
    assert all(f.requires_human_review for f in report.findings)
    assert report.summary.human_review_count == 2


def test_consensus_diagnostics_are_attached_to_findings(
    sample_iac_template: IaCTemplate,
):
    ensemble = _ensemble(
        {"findings": [PUBLIC_BUCKET_GPT]},
        {"findings": [PUBLIC_BUCKET_CLAUDE]},
    )
    report = SecurityAnalystAgent(ensemble=ensemble).analyze(sample_iac_template)

    diagnostics = report.findings[0].raw_details["consensus"]
    assert diagnostics["total_models"] == 2
    assert diagnostics["agreement_ratio"] == 1.0
    assert diagnostics["match_reasons"][1].startswith("semantic:")
    assert set(diagnostics["per_model_confidence"]) == {
        "gpt-4o",
        "claude-3-5-sonnet-20241022",
    }
    assert 0.0 <= diagnostics["agreement"]["score"] <= 1.0


def test_unparseable_model_output_still_counts_toward_the_denominator(
    sample_iac_template: IaCTemplate,
):
    """One model returning junk must not let the other auto-patch alone."""
    good = LLMClient(LLMConfig(model_name="gpt-4o"))
    good.set_mock_responses([json.dumps({"findings": [PUBLIC_BUCKET_GPT]})])
    broken = LLMClient(LLMConfig(model_name="claude-3-5-sonnet-20241022"))
    broken.set_mock_responses(["NOT VALID JSON AT ALL"])

    report = SecurityAnalystAgent(
        ensemble=MultiLLMEnsemble([good, broken])
    ).analyze(sample_iac_template)

    assert len(report.findings) == 1
    finding = report.findings[0]
    assert finding.model_agreements == ["gpt-4o"]
    assert finding.auto_patchable is False
    assert finding.requires_human_review is True


def test_total_model_failure_falls_back_to_heuristic_audit(
    sample_iac_template: IaCTemplate,
):
    broken_a = LLMClient(LLMConfig(model_name="gpt-4o"))
    broken_a.set_mock_responses(["NOT JSON"])
    broken_b = LLMClient(LLMConfig(model_name="claude-3-5-sonnet-20241022"))
    broken_b.set_mock_responses(["ALSO NOT JSON"])

    report = SecurityAnalystAgent(
        ensemble=MultiLLMEnsemble([broken_a, broken_b])
    ).analyze(sample_iac_template)

    assert len(report.findings) >= 1
    assert report.findings[0].rule_id == "AS-DEF-001"


def test_fitted_calibrator_can_gate_an_otherwise_auto_patchable_finding(
    sample_iac_template: IaCTemplate,
):
    """Calibration is load-bearing: models that historically over-report at
    high confidence get pulled back below the auto-patch threshold."""
    ensemble = _ensemble(
        {"findings": [PUBLIC_BUCKET_GPT]},
        {"findings": [PUBLIC_BUCKET_CLAUDE]},
    )
    calibrator = ConfidenceCalibrator().fit([0.95] * 20, [1] * 4 + [0] * 16)
    agent = SecurityAnalystAgent(
        ensemble=ensemble,
        consensus_engine=ConsensusEngine(calibrator=calibrator),
    )
    report = agent.analyze(sample_iac_template)

    finding = report.findings[0]
    assert finding.confidence_score < AUTO_PATCH_THRESHOLD
    assert finding.requires_human_review is True
    assert finding.raw_details["consensus"]["calibrator_fitted"] is True
    assert (
        finding.raw_details["consensus"]["calibrated_confidence"]
        < finding.raw_details["consensus"]["raw_confidence"]
    )


def test_escalated_consensus_finding_reaches_the_audit_queue(
    sample_iac_template: IaCTemplate, tmp_path
):
    """Task 3.2 routing hands off correctly to the Task 3.4 audit queue."""
    good = LLMClient(LLMConfig(model_name="gpt-4o"))
    good.set_mock_responses([json.dumps({"findings": [PUBLIC_BUCKET_GPT]})])
    silent = LLMClient(LLMConfig(model_name="claude-3-5-sonnet-20241022"))
    silent.set_mock_responses([json.dumps({"findings": []})])

    report = SecurityAnalystAgent(
        ensemble=MultiLLMEnsemble([good, silent])
    ).analyze(sample_iac_template)

    workspace = AgentShieldWorkspace(
        template=sample_iac_template, report=report, patches=[], status="ANALYZED"
    )
    manager = AuditQueueManager(persist_file=tmp_path / "audit_queue.json")
    enqueued = manager.evaluate_and_enqueue(workspace)

    assert len(enqueued) == 1
    item = enqueued[0]
    # Consensus score below 0.80 is reported as model disagreement, not merely
    # low confidence.
    assert item.escalation_trigger == EscalationReason.MODEL_DISAGREEMENT
    assert "gpt-4o" in item.escalation_reason


def test_consensus_findings_that_agree_are_not_escalated(
    sample_iac_template: IaCTemplate, tmp_path
):
    ensemble = _ensemble(
        {"findings": [PUBLIC_BUCKET_GPT]},
        {"findings": [PUBLIC_BUCKET_CLAUDE]},
    )
    report = SecurityAnalystAgent(ensemble=ensemble).analyze(sample_iac_template)

    workspace = AgentShieldWorkspace(
        template=sample_iac_template, report=report, patches=[], status="ANALYZED"
    )
    manager = AuditQueueManager(persist_file=tmp_path / "audit_queue.json")

    assert manager.evaluate_and_enqueue(workspace) == []
