import os
import yaml
from typing import List, Dict, Any
from agentshield.parsers.schemas import ParsedResource
from agentshield.parsers.line_loader import SafeLineLoader

def parse_cfn_file(file_path: str) -> List[ParsedResource]:
    """
    Parses a CloudFormation template (JSON or YAML) and returns a list of ParsedResources.
    
    Args:
        file_path: Path to the CloudFormation template file.
        
    Returns:
        List[ParsedResource]: List of normalized resources.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"CloudFormation file not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        raw_content = f.read()

    # Split lines for raw snippet extraction
    lines = raw_content.splitlines()

    try:
        # SafeLineLoader handles both YAML and JSON templates since JSON is valid YAML
        template = yaml.load(raw_content, Loader=SafeLineLoader)
    except Exception as e:
        raise ValueError(f"Failed to parse CloudFormation template: {e}")

    if not template or not isinstance(template, dict):
        return []

    resources_dict = template.get("Resources")
    if not resources_dict or not isinstance(resources_dict, dict):
        return []

    parsed_resources = []

    for logical_id, resource_def in resources_dict.items():
        if not isinstance(resource_def, dict):
            continue

        resource_type = resource_def.get("Type")
        if not resource_type:
            continue

        # Extract properties
        properties = resource_def.get("Properties", {})
        if isinstance(properties, dict):
            properties = dict(properties)
        else:
            properties = {"value": properties}

        # Determine line numbers
        start_line = resource_def.get("__start_line__")
        end_line = resource_def.get("__end_line__")
        line_range = None
        raw_snippet = ""

        if start_line is not None and end_line is not None:
            line_range = (start_line, end_line)
            # Reconstruct raw snippet from lines (adjust to 0-indexed bounds)
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
            resource_id=logical_id,
            resource_type=resource_type,
            cloud_provider="aws",  # CloudFormation is AWS-specific
            iac_format="cloudformation",
            properties=properties,
            raw_snippet=raw_snippet,
            file_path=os.path.abspath(file_path),
            line_range=line_range
        ))

    return parsed_resources
