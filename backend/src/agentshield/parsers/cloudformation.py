import json
from pathlib import Path
from typing import Any
import yaml


def parse_cloudformation_file(file_path: str) -> dict[str, Any]:
    """
    Parse an AWS CloudFormation template (.json, .yaml, .template) into a Python dictionary.
    Handles standard YAML/JSON structures and AWS custom tag constructors.
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"CloudFormation file not found: {file_path}")

    content = path.read_text(encoding="utf-8")

    # Custom Loader for AWS CloudFormation intrinsic functions (e.g., !Ref, !Sub, !GetAtt)
    class CFNLoader(yaml.SafeLoader):
        pass

    def cfn_constructor(loader, node):
        if isinstance(node, yaml.ScalarNode):
            return loader.construct_scalar(node)
        elif isinstance(node, yaml.SequenceNode):
            return loader.construct_sequence(node)
        elif isinstance(node, yaml.MappingNode):
            return loader.construct_mapping(node)
        return None

    cfn_tags = [
        "!Ref", "!Sub", "!GetAtt", "!Join", "!Select", "!Split",
        "!FindInMap", "!ImportValue", "!GetAZs", "!If", "!Not",
        "!Equals", "!And", "!Or", "!Condition"
    ]

    for tag in cfn_tags:
        CFNLoader.add_constructor(tag, cfn_constructor)

    if path.suffix.lower() == ".json":
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in CloudFormation file: {e}") from e

    try:
        data = yaml.load(content, Loader=CFNLoader)
        if isinstance(data, dict):
            return data
        raise ValueError("CloudFormation template must parse to a dictionary object.")
    except Exception as e:
        # Fallback to standard json decode if yaml fails
        try:
            return json.loads(content)
        except Exception:
            raise ValueError(f"Failed to parse CloudFormation template: {e}") from e


def extract_cloudformation_resources(parsed_data: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Extract resources, parameters, and metadata from parsed CloudFormation data.
    """
    resources = []
    cfn_resources = parsed_data.get("Resources", {})

    if not isinstance(cfn_resources, dict):
        return resources

    for resource_name, resource_body in cfn_resources.items():
        if not isinstance(resource_body, dict):
            continue

        resource_type = str(resource_body.get("Type", "AWS::Unknown::Resource")).strip('"\'')
        properties = resource_body.get("Properties", {})
        metadata = resource_body.get("Metadata", {})
        condition = resource_body.get("Condition")
        depends_on = resource_body.get("DependsOn")

        resources.append({
            "resource_id": f"{resource_type}.{resource_name}",
            "resource_type": resource_type,
            "resource_name": str(resource_name).strip('"\''),
            "properties": properties if isinstance(properties, dict) else {},
            "metadata": metadata if isinstance(metadata, dict) else {},
            "condition": condition,
            "depends_on": depends_on,
            "start_line": None,
            "end_line": None,
        })

    return resources
