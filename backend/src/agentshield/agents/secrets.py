from typing import Any

from agentshield.core.schemas.contracts import AgentShieldWorkspace
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

    def execute_workspace(self, workspace: AgentShieldWorkspace) -> AgentShieldWorkspace:
        """
        Integrate with workspace state, enriching workspace report with flagged secrets findings.
        """
        file_path = workspace.template.file_path
        content = workspace.template.raw_content

        secrets_findings = self.scan(file_path, content)

        if workspace.report:
            workspace.report.findings.extend(secrets_findings)
            workspace.report.recalculate_summary()

        return workspace
