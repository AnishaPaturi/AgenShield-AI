"""
Unit tests for individual specialized agents.
"""

from agentshield.agents.manager import manager_agent_node
from agentshield.agents.secrets import secrets_agent_node
from agentshield.agents.analyst import analyst_agent_node
from agentshield.agents.remediation import remediation_agent_node


def test_secrets_agent(tmp_path):
    secret_file = tmp_path / "creds.tf"
    secret_file.write_text('aws_secret_access_key = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYKEY12345678"')

    state = {
        "target_files": [str(secret_file)],
        "execution_log": []
    }

    result = secrets_agent_node(state)
    secrets = result.get("secret_findings", [])
    assert len(secrets) == 1
    assert secrets[0]["secret_type"] == "AWS Credential Leak"


def test_analyst_and_remediation_agents():
    state = {
        "rag_context": [{
            "resource_id": "aws_s3_bucket.my_bucket",
            "file_path": "main.tf",
            "line_number": 1,
            "matched_rules": [{
                "rule_id": "CKV_AWS_19",
                "title": "Ensure S3 bucket is not publicly accessible",
                "severity": "CRITICAL",
                "compliance_standards": ["SOC2-CC6.1", "HIPAA-164.312"],
                "description": "S3 bucket public read access risk",
                "remediation_hcl": '  acl = "private"'
            }]
        }],
        "execution_log": []
    }

    analyst_result = analyst_agent_node(state)
    findings = analyst_result.get("security_findings", [])
    assert len(findings) == 1
    assert findings[0]["confidence_score"] >= 0.80

    remediation_result = remediation_agent_node(analyst_result)
    patches = remediation_result.get("remediation_patches", [])
    assert len(patches) == 1
    assert "remediation_hcl" in patches[0]["patched_code"] or "acl = \"private\"" in patches[0]["patched_code"]
