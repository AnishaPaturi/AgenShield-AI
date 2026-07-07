"""IaC parsers package (HCL/Terraform, YAML/Kubernetes, JSON/CloudFormation)."""

from agentshield.parsers.schemas import ScanReport, CheckovFinding, ScanSummary, ParsedResource
from agentshield.parsers.cfn_parser import parse_cfn_file
from agentshield.parsers.k8s_parser import parse_k8s_file

__all__ = [
    "ScanReport", 
    "CheckovFinding", 
    "ScanSummary", 
    "ParsedResource",
    "parse_cfn_file",
    "parse_k8s_file"
]
