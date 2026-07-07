import os
import yaml
from typing import List, Dict, Any
from agentshield.parsers.schemas import ParsedResource
from agentshield.parsers.line_loader import SafeLineLoader

def parse_k8s_file(file_path: str) -> List[ParsedResource]:
    """
    Parses a Kubernetes manifest file (supporting multi-document YAML)
    and returns a list of ParsedResources.
    
    Args:
        file_path: Path to the Kubernetes YAML manifest.
        
    Returns:
        List[ParsedResource]: List of normalized Kubernetes resources.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Kubernetes file not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        raw_content = f.read()

    lines = raw_content.splitlines()

    try:
        # Load all documents from the manifest (multi-document support)
        documents = yaml.load_all(raw_content, Loader=SafeLineLoader)
        doc_list = list(documents)
    except Exception as e:
        raise ValueError(f"Failed to parse Kubernetes manifest: {e}")

    parsed_resources = []

    for doc_idx, doc in enumerate(doc_list):
        if not doc or not isinstance(doc, dict):
            continue

        resource_type = doc.get("kind")
        if not resource_type:
            continue

        metadata = doc.get("metadata", {})
        resource_id = f"unnamed-doc-{doc_idx}"
        if isinstance(metadata, dict):
            resource_id = metadata.get("name", resource_id)
        elif isinstance(metadata, str):
            resource_id = metadata

        # Clone document to serve as properties
        properties = dict(doc)

        # Get line numbers
        start_line = doc.get("__start_line__")
        end_line = doc.get("__end_line__")
        line_range = None
        raw_snippet = ""

        if start_line is not None and end_line is not None:
            line_range = (start_line, end_line)
            snippet_lines = lines[start_line - 1 : end_line]
            raw_snippet = "\n".join(snippet_lines)

        # Recursively clean up __start_line__ and __end_line__ keys in properties
        def clean_metadata(d: Any) -> None:
            if isinstance(d, dict):
                d.pop("__start_line__", None)
                d.pop("__end_line__", None)
                for v in d.values():
                    clean_metadata(v)
            elif isinstance(d, list):
                for item in d:
                    clean_metadata(item)

        clean_metadata(properties)

        parsed_resources.append(ParsedResource(
            resource_id=resource_id,
            resource_type=resource_type,
            cloud_provider="k8s",
            iac_format="kubernetes",
            properties=properties,
            raw_snippet=raw_snippet,
            file_path=os.path.abspath(file_path),
            line_range=line_range
        ))

    return parsed_resources
