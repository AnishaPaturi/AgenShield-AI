import math
from pathlib import Path
import re
from typing import Any

from agentshield.core.schemas.vulnerability import SeverityLevel, VulnerabilityFinding


def calculate_shannon_entropy(data: str) -> float:
    """
    Calculate Shannon entropy of a string to identify high-entropy random secrets.
    """
    if not data:
        return 0.0
    entropy = 0.0
    for char in set(data):
        p_x = float(data.count(char)) / len(data)
        entropy -= p_x * math.log2(p_x)
    return entropy


# Gitleaks & TruffleHog high-confidence secret patterns
SECRET_PATTERNS = [
    {
        "id": "SEC-AWS-KEY-001",
        "name": "AWS Access Key ID",
        "pattern": r"(?:A3T[A-Z0-9]|AKIA|AGPA|AIDA|AROA|AIPA|ANPA|ANVA|ASIA)[A-Z0-9]{16}",
        "severity": SeverityLevel.CRITICAL,
        "description": "Hardcoded AWS Access Key ID exposed in infrastructure template.",
        "cwe_id": "CWE-798",
    },
    {
        "id": "SEC-AWS-SECRET-002",
        "name": "AWS Secret Access Key",
        "pattern": r"(?i)aws_?(?:secret)?_?(?:access)?_?key\s*[:=]\s*['\"]?([A-Za-z0-9/+=]{40})['\"]?",
        "severity": SeverityLevel.CRITICAL,
        "description": "Hardcoded AWS Secret Access Key detected in template source.",
        "cwe_id": "CWE-798",
    },
    {
        "id": "SEC-RSA-KEY-003",
        "name": "Private RSA/SSH Key",
        "pattern": r"-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----",
        "severity": SeverityLevel.CRITICAL,
        "description": "Embedded private key certificate detected in source code.",
        "cwe_id": "CWE-321",
    },
    {
        "id": "SEC-JWT-TOKEN-004",
        "name": "JSON Web Token (JWT)",
        "pattern": r"eyJ[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*",
        "severity": SeverityLevel.HIGH,
        "description": "Embedded JWT Authentication Token detected.",
        "cwe_id": "CWE-798",
    },
    {
        "id": "SEC-GH-TOKEN-005",
        "name": "GitHub Personal Access Token",
        "pattern": r"ghp_[a-zA-Z0-9]{36}|github_pat_[a-zA-Z0-9]{22}_[a-zA-Z0-9]{59}",
        "severity": SeverityLevel.CRITICAL,
        "description": "Hardcoded GitHub Personal Access Token exposed.",
        "cwe_id": "CWE-798",
    },
    {
        "id": "SEC-DB-URI-006",
        "name": "Database Connection Password",
        "pattern": r"(?:postgres|mysql|mongodb|redis)://[a-zA-Z0-9_]+:([^@\s\"']+)@[a-zA-Z0-9_.-]+",
        "severity": SeverityLevel.HIGH,
        "description": "Hardcoded password embedded inside database connection URL.",
        "cwe_id": "CWE-259",
    },
]


def scan_content_for_secrets(content: str, file_path: str = "template.tf") -> list[VulnerabilityFinding]:
    """
    Scan string content for hardcoded secrets, API keys, and high-entropy credentials.
    """
    findings = []
    lines = content.splitlines()

    # Pattern matching
    for rule in SECRET_PATTERNS:
        compiled_regex = re.compile(rule["pattern"])
        for idx, line in enumerate(lines, start=1):
            match = compiled_regex.search(line)
            if match:
                findings.append(
                    VulnerabilityFinding(
                        finding_id=f"{rule['id']}-L{idx}",
                        title=f"Embedded Secret: {rule['name']}",
                        severity=rule["severity"],
                        category="Secrets Leakage",
                        description=rule["description"],
                        resource_id=f"file.{Path(file_path).name}",
                        resource_type="File/Credential",
                        affected_line_start=idx,
                        affected_line_end=idx,
                        cwe_id=rule["cwe_id"],
                        remediation_recommendation=(
                            "Remove hardcoded credentials. Store secrets in AWS Secrets Manager, "
                            "HashiCorp Vault, or reference them dynamically via environment variables."
                        ),
                        confidence_score=0.98,
                    )
                )

    # High-entropy string search for assignments
    assignment_pattern = re.compile(r"(?:password|passwd|secret|api_key|token)\s*[:=]\s*['\"]([^'\"]{16,})['\"]", re.IGNORECASE)
    for idx, line in enumerate(lines, start=1):
        for match in assignment_pattern.finditer(line):
            secret_val = match.group(1)
            entropy = calculate_shannon_entropy(secret_val)
            if entropy > 4.2:
                findings.append(
                    VulnerabilityFinding(
                        finding_id=f"SEC-ENTROPY-L{idx}",
                        title="High-Entropy Secret Assignment",
                        severity=SeverityLevel.HIGH,
                        category="High-Entropy Secrets",
                        description=f"High entropy secret string (entropy: {entropy:.2f}) detected in variable assignment.",
                        resource_id=f"file.{Path(file_path).name}",
                        resource_type="File/Secret",
                        affected_line_start=idx,
                        affected_line_end=idx,
                        cwe_id="CWE-798",
                        remediation_recommendation="Replace hardcoded high-entropy secret string with dynamic secret manager reference.",
                        confidence_score=0.92,
                    )
                )

    return findings


def scan_file_for_secrets(file_path: str) -> list[VulnerabilityFinding]:
    """
    Scan a file on disk for hardcoded secrets and credentials.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found for secrets scan: {file_path}")

    content = path.read_text(encoding="utf-8", errors="ignore")
    return scan_content_for_secrets(content, str(path))
