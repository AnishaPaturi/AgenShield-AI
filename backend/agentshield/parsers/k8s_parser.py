"""
Kubernetes Manifest (YAML / multi-doc) IaC Parser.
Parses Workload specifications, securityContext, Pod Security Standards (PSS), and service linkages.
"""

import os
import yaml
from typing import List
from agentshield.parsers.schemas import IaCResource
from agentshield.parsers.line_loader import LineLoader


def parse_kubernetes(file_path: str) -> List[IaCResource]:
    """
    Parses a Kubernetes multi-document YAML file into IaCResource AST objects.
    """
    resources = []
    if not os.path.exists(file_path):
        return resources

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    try:
        docs = yaml.load_all(content, Loader=LineLoader)
        for doc in docs:
            if isinstance(doc, dict):
                kind = doc.get("kind", "KubernetesResource")
                metadata = doc.get("metadata", {})
                name = metadata.get("name", "unnamed") if isinstance(metadata, dict) else "unnamed"
                line_no = doc.get("__line__", 1)

                # Extract volume / secret dependencies
                deps = []
                spec = doc.get("spec", {})
                if isinstance(spec, dict):
                    volumes = spec.get("volumes", [])
                    if isinstance(volumes, list):
                        for vol in volumes:
                            if isinstance(vol, dict) and "secret" in vol:
                                secret_name = vol["secret"].get("secretName")
                                if secret_name:
                                    deps.append(f"Secret.{secret_name}")

                resources.append(
                    IaCResource(
                        file_path=file_path,
                        resource_type=f"k8s/{kind}",
                        resource_name=name,
                        provider="k8s",
                        line_start=line_no,
                        line_end=line_no + 15,
                        attributes=doc,
                        dependencies=deps
                    )
                )
    except Exception:
        pass

    return resources
