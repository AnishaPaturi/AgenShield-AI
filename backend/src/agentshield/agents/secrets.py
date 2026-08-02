from typing import Any

from agentshield.core.schemas.contracts import AgentShieldState
from agentshield.core.schemas.vulnerability import VulnerabilityFinding
from agentshield.scanners.secrets_scanner import scan_content_for_secrets, scan_file_for_secrets


class SecretsScannerAgent:
    """
    Dedicated Secrets & Credential Scanner Agent.
    Intercepts embedded AWS credentials, JWT tokens, RSA private keys, and high-entropy secrets.
    """

    def __init__(self, name: str = "SecretsScannerAgent"):
        self.name = name

    def scan(self, file_path: str, content: str | None = None) -> list[VulnerabilityFinding]:
        """
        Scan a file or raw string content for secrets leakage.
        """
        if content:
            return scan_content_for_secrets(content, file_path)
        return scan_file_for_secrets(file_path)

    def execute_state(self, state: AgentShieldState) -> AgentShieldState:
        """
        Integrate with LangGraph execution state, enriching state with flagged secrets findings.
        """
        file_path = state.template.file_path
        content = state.template.raw_content

        secrets_findings = self.scan(file_path, content)

        # Append flagged findings to state
        existing_findings = state.vulnerability_report.findings if state.vulnerability_report else []
        combined_findings = existing_findings + secrets_findings

        state.vulnerability_report.findings = combined_findings
        return state
