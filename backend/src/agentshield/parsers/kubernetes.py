from pathlib import Path
from typing import Any
import yaml


def parse_kubernetes_file(file_path: str) -> list[dict[str, Any]]:
    """
    Parse a Kubernetes manifest file (.yaml, .yml) into a list of document dictionaries.
    Supports multi-document YAML files separated by '---'.
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Kubernetes manifest file not found: {file_path}")

    content = path.read_text(encoding="utf-8")

    documents = []
    try:
        raw_docs = list(yaml.safe_load_all(content))
        for doc in raw_docs:
            if isinstance(doc, dict) and doc:
                documents.append(doc)
    except Exception as e:
        raise ValueError(f"Failed to parse Kubernetes YAML manifest: {e}") from e

    return documents


def extract_kubernetes_resources(documents: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Extract individual Kubernetes resources from parsed multi-document YAML data.
    """
    resources = []

    for doc in documents:
        api_version = str(doc.get("apiVersion", "v1")).strip('"\'')
        kind = str(doc.get("kind", "UnknownKind")).strip('"\'')
        metadata = doc.get("metadata", {})
        spec = doc.get("spec", {})

        resource_name = "unnamed"
        namespace = "default"

        if isinstance(metadata, dict):
            resource_name = str(metadata.get("name", "unnamed")).strip('"\'')
            namespace = str(metadata.get("namespace", "default")).strip('"\'')

        resource_id = f"k8s.{kind}.{resource_name}"

        # Extract container definitions if present (Pod, Deployment, DaemonSet, StatefulSet, Job)
        containers = []
        pod_spec = spec.get("template", {}).get("spec", spec) if isinstance(spec, dict) else {}
        if isinstance(pod_spec, dict):
            containers = pod_spec.get("containers", [])

        resources.append({
            "resource_id": resource_id,
            "resource_type": f"k8s/{kind}",
            "resource_name": resource_name,
            "api_version": api_version,
            "kind": kind,
            "namespace": namespace,
            "metadata": metadata if isinstance(metadata, dict) else {},
            "properties": spec if isinstance(spec, dict) else {},
            "containers": containers if isinstance(containers, list) else [],
            "start_line": None,
            "end_line": None,
        })

    return resources
