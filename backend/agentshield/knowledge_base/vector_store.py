"""
Vector Store and RAG Compliance Core for AgentShield AI.
Maps IaC resource misconfigurations to regulatory compliance standards (SOC 2, HIPAA, PCI-DSS, NIST 800-53).
"""

from typing import Dict, List, Any


COMPLIANCE_KNOWLEDGE_BASE: List[Dict[str, Any]] = [
    {
        "pattern": ["s3", "public", "read", "acl"],
        "rule_id": "CKV_AWS_19",
        "title": "Ensure S3 bucket is not publicly accessible",
        "severity": "CRITICAL",
        "compliance_standards": ["SOC2-CC6.1", "HIPAA-164.312", "PCI-DSS-2.2", "NIST-800-53-AC-3"],
        "description": "S3 buckets with public read access allow unauthorized external access to sensitive cloud data.",
        "remediation_hcl": '  acl = "private"\n  block_public_acls = true\n  block_public_policy = true'
    },
    {
        "pattern": ["encryption", "server_side_encryption", "sse", "kms"],
        "rule_id": "CKV_AWS_145",
        "title": "Ensure S3 bucket has server-side encryption enabled",
        "severity": "HIGH",
        "compliance_standards": ["SOC2-CC6.6", "HIPAA-164.312(a)(2)(iv)", "PCI-DSS-3.4", "NIST-800-53-SC-13"],
        "description": "Unencrypted cloud storage exposes sensitive data to unauthorized disclosure at rest.",
        "remediation_hcl": '  server_side_encryption_configuration {\n    rule {\n      apply_server_side_encryption_by_default {\n        sse_algorithm = "AES256"\n      }\n    }\n  }'
    },
    {
        "pattern": ["privileged", "root", "securityContext", "0"],
        "rule_id": "CKV_K8S_16",
        "title": "Ensure containers do not run in privileged mode or as root user",
        "severity": "CRITICAL",
        "compliance_standards": ["SOC2-CC6.8", "NIST-800-53-AC-3", "PCI-DSS-2.2"],
        "description": "Privileged containers allow container escape and root takeover of host nodes.",
        "remediation_yaml": "securityContext:\n  runAsNonRoot: true\n  readOnlyRootFilesystem: true\n  allowPrivilegeEscalation: false"
    },
    {
        "pattern": ["0.0.0.0/0", "ingress", "ssh", "22", "rdp", "3389"],
        "rule_id": "CKV_AWS_24",
        "title": "Ensure Security Group does not allow unrestricted inbound traffic (0.0.0.0/0) to sensitive ports",
        "severity": "CRITICAL",
        "compliance_standards": ["SOC2-CC6.6", "HIPAA-164.312", "PCI-DSS-1.2", "NIST-800-53-SC-7"],
        "description": "Unrestricted inbound access to SSH (22) or RDP (3389) allows brute-force attacks from anywhere on the internet.",
        "remediation_hcl": '  cidr_blocks = ["10.0.0.0/16"]'
    }
]


class KnowledgeBaseManager:
    def __init__(self):
        self.rules = COMPLIANCE_KNOWLEDGE_BASE

    def query_compliance_context(self, resource_type: str, raw_code: str) -> List[Dict[str, Any]]:
        """
        Retrieves matching compliance rules and regulatory controls for a given IaC resource.
        """
        matched = []
        code_lower = raw_code.lower()
        res_lower = resource_type.lower()

        for rule in self.rules:
            patterns = rule["pattern"]
            if any(p in code_lower or p in res_lower for p in patterns):
                matched.append(rule)

        return matched
