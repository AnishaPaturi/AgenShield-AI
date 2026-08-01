"""Tests for SecurityAnalystAgent vulnerability detection workflow."""

import json

from agentshield.agents import SecurityAnalystAgent
from agentshield.core.llm import LLMClient
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
