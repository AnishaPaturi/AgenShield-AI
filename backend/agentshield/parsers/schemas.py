"""
Data schemas for AgentShield AI IaC resources, security findings, secrets, patches, and validation results.
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field


class IaCResource(BaseModel):
    file_path: str
    resource_type: str
    resource_name: str
    provider: str = "cloud"  # aws, azure, gcp, k8s, helm
    line_start: int = 1
    line_end: int = 1
    attributes: Dict[str, Any] = Field(default_factory=dict)


class SecretFinding(BaseModel):
    secret_type: str  # API Key, AWS Access Key, Password, Private Token
    file_path: str
    line_number: int
    snippet: str
    severity: str = "CRITICAL"


class Finding(BaseModel):
    finding_id: str
    rule_id: str
    title: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    resource_id: str
    file_path: str
    line_number: int = 1
    description: str
    compliance_standards: List[str] = Field(default_factory=list)  # SOC2, HIPAA, PCI-DSS, NIST 800-53
    confidence_score: float = 1.0  # 0.0 to 1.0
    reasoning: str = ""
    model_votes: Dict[str, str] = Field(default_factory=dict)  # {"Claude-3.5": "VULNERABLE", "GPT-4o": "VULNERABLE"}


class PatchDiff(BaseModel):
    finding_id: str
    file_path: str
    original_code: str
    patched_code: str
    diff_text: str
    compliance_tags: List[str] = Field(default_factory=list)


class ValidationResult(BaseModel):
    finding_id: str
    file_path: str
    syntax_valid: bool = True
    sandbox_passed: bool = True
    details: str = "Validation successful"
