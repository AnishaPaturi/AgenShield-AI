"""
AWS CloudFormation (JSON / YAML) IaC Parser.
"""

import os
import json
import yaml
from typing import List
from agentshield.parsers.schemas import IaCResource
from agentshield.parsers.line_loader import LineLoader


def parse_cloudformation(file_path: str) -> List[IaCResource]:
    """
    Parses a CloudFormation JSON or YAML template into IaCResource objects.
    """
    resources = []
    if not os.path.exists(file_path):
        return resources

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    data = None
    try:
        if file_path.endswith(".json"):
            data = json.loads(content)
        else:
            data = yaml.load(content, Loader=LineLoader)
    except Exception:
        return resources

    if not isinstance(data, dict):
        return resources

    cfn_resources = data.get("Resources", {})
    if isinstance(cfn_resources, dict):
        for res_name, res_def in cfn_resources.items():
            if isinstance(res_def, dict):
                res_type = res_def.get("Type", "AWS::CloudFormation::Resource")
                line_no = res_def.get("__line__", 1)
                props = res_def.get("Properties", {})
                
                resources.append(
                    IaCResource(
                        file_path=file_path,
                        resource_type=res_type,
                        resource_name=res_name,
                        provider="aws",
                        line_start=line_no,
                        line_end=line_no + 10,
                        attributes=props if isinstance(props, dict) else {}
                    )
                )

    return resources
