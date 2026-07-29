"""
Unit tests for the 8-agent LangGraph orchestration state machine.
"""

import os
import pytest
from agentshield.graph import AgentShieldOrchestrator


def test_langgraph_orchestration_state_machine(tmp_path):
    # Create sample vulnerable terraform template in tmp_path
    tf_file = tmp_path / "main.tf"
    tf_file.write_text("""
resource "aws_s3_bucket" "test_bucket" {
  bucket = "test-agent-shield-bucket"
  acl    = "public-read"
}
""")

    orchestrator = AgentShieldOrchestrator()
    result = orchestrator.run(str(tmp_path))

    # Verify all 8 agents executed in sequence
    log = result.get("execution_log", [])
    assert any("[Manager Agent]" in item for item in log)
    assert any("[Hybrid AST Parser Agent]" in item for item in log)
    assert any("[Secrets Scanner Agent]" in item for item in log)
    assert any("[RAG-Query Agent]" in item for item in log)
    assert any("[Security Analyst Agent]" in item for item in log)
    assert any("[Remediation Agent]" in item for item in log)
    assert any("[Code & Sandbox Validator Agent]" in item for item in log)
    assert any("[Report Agent]" in item for item in log)

    # Verify output reports and findings
    findings = result.get("security_findings", [])
    assert len(findings) > 0

    report = result.get("final_report", "")
    assert "AgentShield AI - Unified Multi-Cloud Security & Compliance Audit Report" in report
    assert "SOC 2" in report
    assert "HIPAA" in report
