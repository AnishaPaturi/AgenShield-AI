"""
Helm Chart IaC Parser.
"""

import os
from typing import List
from agentshield.parsers.schemas import IaCResource
from agentshield.parsers.k8s_parser import parse_kubernetes


def parse_helm(file_path: str) -> List[IaCResource]:
    """
    Parses Helm chart templates into IaCResource objects.
    """
    # Helm template files are YAML with Go template expressions.
    resources = parse_kubernetes(file_path)
    for res in resources:
        res.provider = "helm"
    return resources
