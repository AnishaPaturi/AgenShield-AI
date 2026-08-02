from pathlib import Path
import tempfile
import pytest

from agentshield.agents.secrets import SecretsScannerAgent
from agentshield.core.schemas.contracts import AgentShieldWorkspace
from agentshield.core.schemas.iac import IaCTemplate
from agentshield.core.schemas.vulnerability import VulnerabilityReport
from agentshield.scanners.secrets_scanner import (
    calculate_shannon_entropy,
    scan_content_for_secrets,
    scan_file_for_secrets,
)


def test_shannon_entropy_calculation():
    low_entropy = "aaaaaaaaaaaaaaaa"
    high_entropy = "8f9a2b1c4e7d0f3a5b6c"

    assert calculate_shannon_entropy(low_entropy) < 1.0
    assert calculate_shannon_entropy(high_entropy) > 3.5


def test_scan_content_for_aws_keys():
    content = """
    provider "aws" {
      region     = "us-east-1"
      access_key = "AKIAIOSFODNN7EXAMPLE"
      secret_key = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
    }
    """
    findings = scan_content_for_secrets(content, "main.tf")

    assert len(findings) >= 1
    aws_key_finding = next((f for f in findings if "AWS Access Key" in f.title), None)
    assert aws_key_finding is not None
    assert aws_key_finding.confidence_score >= 0.95


def test_scan_content_for_rsa_and_jwt():
    content = """
    variable "private_key" {
      default = "-----BEGIN RSA PRIVATE KEY-----\\nMIIEowIBAAKCAQEA..."
    }
    variable "jwt_token" {
      default = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
    }
    """
    findings = scan_content_for_secrets(content, "secrets.tf")

    assert len(findings) >= 2
    titles = [f.title for f in findings]
    assert any("RSA" in t for t in titles)
    assert any("JWT" in t for t in titles)


def test_secrets_scanner_agent_execution():
    content = 'api_token = "ghp_1234567890abcdefghijklmnopqrstuvwxyz"'
    with tempfile.NamedTemporaryFile("w", suffix=".tf", delete=False) as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        agent = SecretsScannerAgent()
        findings = agent.scan(tmp_path)
        assert len(findings) >= 1
        assert "GitHub" in findings[0].title

        # Test AgentShieldWorkspace Integration
        template = IaCTemplate(file_path=tmp_path, raw_content=content, template_type="terraform")
        report = VulnerabilityReport(template_id="t1", target_file=tmp_path)
        workspace = AgentShieldWorkspace(template=template, report=report)

        updated_workspace = agent.execute_workspace(workspace)
        assert len(updated_workspace.report.findings) >= 1
    finally:
        Path(tmp_path).unlink(missing_ok=True)
