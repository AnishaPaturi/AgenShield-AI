"""
Enhanced data schemas for AgentShield AI multi-cloud IaC resources, dependency graphs, findings, secrets, patches, and validation results.
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field


class IaCResource(BaseModel):
    file_path: str
    resource_type: str
    resource_name: str
    provider: str = "aws"  # aws, azure, gcp, k8s, helm
    line_start: int = 1
    line_end: int = 1
    attributes: Dict[str, Any] = Field(default_factory=dict)
    dependencies: List[str] = Field(default_factory=list)  # Referenced resource IDs
    variables: Dict[str, Any] = Field(default_factory=dict)  # Dynamic parameters/variables
    environment_context: str = "default"  # production, staging, dev


class ASTDependencyGraph(BaseModel):
    nodes: Dict[str, IaCResource] = Field(default_factory=dict)
    edges: List[Dict[str, str]] = Field(default_factory=list)  # [{"source": "resA", "target": "resB"}]


class ParsedIaCFile(BaseModel):
    file_path: str
    file_type: str  # terraform, cloudformation, kubernetes, helm
    resources: List[IaCResource] = Field(default_factory=list)
    variables: Dict[str, Any] = Field(default_factory=dict)
    modules: List[Dict[str, Any]] = Field(default_factory=list)


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
