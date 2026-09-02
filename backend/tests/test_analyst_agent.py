"""Tests for SecurityAnalystAgent vulnerability detection workflow."""

import json

from agentshield.agents import SecurityAnalystAgent
from agentshield.core.llm import LLMClient, MultiLLMEnsemble
from agentshield.core.schemas import IaCTemplate, Severity, VulnerabilityReport


def test_analyst_agent_mock_structured_parsing(sample_iac_template: IaCTemplate):
    client = LLMClient()
    mock_payload = {
        "findings": [
            {
                "rule_id": "AS-AWS-001",
                "title": "Public S3 Bucket Detected",
                "description": "Bucket has public-read ACL.",
                "severity": "HIGH",
                "confidence_score": 0.95,
                "affected_resource": "aws_s3_bucket.data_bucket",
            }
        ]
    }
    client.set_mock_responses([json.dumps(mock_payload)])

    agent = SecurityAnalystAgent(llm_client=client)
    report = agent.analyze(sample_iac_template)

    assert isinstance(report, VulnerabilityReport)
    assert report.summary.total_vulnerabilities == 1
    assert report.summary.high_count == 1
    assert report.findings[0].rule_id == "AS-AWS-001"
    assert len(report.findings[0].compliance_mappings) >= 1


def test_analyst_agent_fallback(sample_iac_template: IaCTemplate):
    client = LLMClient()
    # Force JSON parse error to test heuristic fallback audit
    client.set_mock_responses(["INVALID_NON_JSON_RESPONSE"])

    agent = SecurityAnalystAgent(llm_client=client)
    report = agent.analyze(sample_iac_template)

    assert isinstance(report, VulnerabilityReport)
    assert report.summary.total_vulnerabilities >= 1
    assert report.findings[0].rule_id == "AS-DEF-001"
    assert report.findings[0].severity == Severity.HIGH
    assert report.findings[0].auto_patchable is True
    assert report.summary.auto_patchable_count >= 1


def test_analyst_agent_ensemble_dual_model_consensus(sample_iac_template: IaCTemplate):
    client1 = LLMClient()
    client2 = LLMClient()

    # Model 1 (e.g. Claude 3.5 Sonnet) detects S3 public read with C=0.90
    client1.set_mock_responses([
        json.dumps({
            "findings": [
                {
                    "rule_id": "AS-AWS-001",
                    "title": "Public S3 Bucket",
                    "description": "Public read ACL",
                    "severity": "HIGH",
                    "confidence_score": 0.90,
                    "affected_resource": "aws_s3_bucket.data_bucket",
                    "raw_details": {"model": "claude-3-5-sonnet"},
                }
            ]
        })
    ])

    # Model 2 (e.g. GPT-4o) agrees on the same vulnerability with C=0.95
    client2.set_mock_responses([
        json.dumps({
            "findings": [
                {
                    "rule_id": "AS-AWS-001",
                    "title": "Public S3 Bucket",
                    "description": "Public read ACL",
                    "severity": "HIGH",
                    "confidence_score": 0.95,
                    "affected_resource": "aws_s3_bucket.data_bucket",
                    "raw_details": {"model": "gpt-4o"},
                }
            ]
        })
    ])

    ensemble = MultiLLMEnsemble([client1, client2])
    agent = SecurityAnalystAgent(ensemble=ensemble)
    report = agent.analyze(sample_iac_template)

    assert len(report.findings) == 1
    finding = report.findings[0]
    # Calibrated score: 0.45(0.90) + 0.45(0.95) + 0.10(1.0)(2/2) = 0.405 + 0.4275 + 0.10 = 0.9325 >= 0.85
    assert finding.confidence_score == 0.9325
    assert finding.consensus_score == 0.9325
    assert finding.auto_patchable is True
    assert finding.requires_human_review is False
    assert finding.escalation_reason is None
    assert "claude-3-5-sonnet" in finding.model_agreements
    assert "gpt-4o" in finding.model_agreements
    assert report.summary.auto_patchable_count == 1
    assert report.summary.human_review_count == 0


def test_analyst_agent_ensemble_single_model_hallucination_escalates(sample_iac_template: IaCTemplate):
    client1 = LLMClient()
    client2 = LLMClient()

    # Model 1 produces a finding with C=0.90
    client1.set_mock_responses([
        json.dumps({
            "findings": [
                {
                    "rule_id": "AS-AWS-999",
                    "title": "Hallucinated Rule Finding",
                    "description": "Single model trigger",
                    "severity": "MEDIUM",
                    "confidence_score": 0.90,
                    "affected_resource": "aws_s3_bucket.data_bucket",
                    "raw_details": {"model": "claude-3-5-sonnet"},
                }
            ]
        })
    ])

    # Model 2 does NOT find this issue (clean)
    client2.set_mock_responses([
        json.dumps({"findings": []})
    ])

    ensemble = MultiLLMEnsemble([client1, client2])
    agent = SecurityAnalystAgent(ensemble=ensemble)
    report = agent.analyze(sample_iac_template)

    assert len(report.findings) == 1
    finding = report.findings[0]
    # Calibrated score: 0.45(0.90) + 0.10(1.0)(1/2) = 0.405 + 0.05 = 0.4550 < 0.85
    assert finding.confidence_score == 0.455
    assert finding.auto_patchable is False
    assert finding.requires_human_review is True
    assert finding.escalation_reason is not None
    assert "below auto-patch threshold" in finding.escalation_reason
    assert report.summary.auto_patchable_count == 0
    assert report.summary.human_review_count == 1
