"""
Agent 3: Secrets Scanner Agent
Scans IaC files and ASTs for embedded API keys, passwords, AWS secret keys, and private tokens using Gitleaks/TruffleHog rules.
"""

import re
from typing import List
from agentshield.state import AgentShieldState
from agentshield.parsers.schemas import SecretFinding


SECRET_PATTERNS = [
    (re.compile(r'(?i)(aws_secret_access_key|aws_access_key_id)\s*=\s*["\']([A-Za-z0-9/+=]{16,64})["\']'), "AWS Credential Leak"),
    (re.compile(r'(?i)(password|secret|api_key|token)\s*=\s*["\']([A-Za-z0-9!@#$%^&*()_+={}\[\]:;<>,.?/~`-]{8,})["\']'), "Hardcoded Password / API Key"),
    (re.compile(r'-----BEGIN (RSA|EC|OPENSSH|PRIVATE) KEY-----'), "Embedded Private Key Token"),
]


def secrets_agent_node(state: AgentShieldState) -> AgentShieldState:
    """
    Scans files for embedded secrets and hardcoded tokens.
    """
    target_files = state.get("target_files", [])
    secret_findings: List[SecretFinding] = []

    for file_path in target_files:
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()

            for line_no, line in enumerate(lines, start=1):
                # Ignore placeholder values
                if "YOUR_" in line or "EXAMPLE" in line or "DUMMY" in line:
                    continue

                for pattern, secret_type in SECRET_PATTERNS:
                    if pattern.search(line):
                        secret_findings.append(
                            SecretFinding(
                                secret_type=secret_type,
                                file_path=file_path,
                                line_number=line_no,
                                snippet=line.strip(),
                                severity="CRITICAL"
                            )
                        )
        except Exception:
            pass

    status_log = state.get("execution_log", [])
    status_log.append(f"[Secrets Scanner Agent] Intercepted {len(secret_findings)} hardcoded secret/credential leak(s).")

    return {
        **state,
        "secret_findings": [sf.model_dump() for sf in secret_findings],
        "execution_log": status_log,
        "current_agent": "RAG-Query Agent"
    }
