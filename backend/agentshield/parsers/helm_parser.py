"""
Helm Chart IaC Parser.
Parses Helm chart templates, values.yaml overrides, and Helm release parameters.
"""

import os
from typing import List
from agentshield.parsers.schemas import IaCResource
from agentshield.parsers.k8s_parser import parse_kubernetes


def parse_helm(file_path: str) -> List[IaCResource]:
    """
    Parses Helm chart template files into IaCResource AST objects with Helm provider classification.
    """
    resources = parse_kubernetes(file_path)
    for res in resources:
        res.provider = "helm"
        res.environment_context = "helm_chart"
    return resources
