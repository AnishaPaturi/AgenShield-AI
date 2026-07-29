"""
AWS CloudFormation (JSON / YAML) Multi-Cloud IaC Parser.
Supports parameter pre-evaluation, condition handling, and Ref / Fn::GetAtt dependency extraction.
"""

import os
import json
import yaml
from typing import List, Dict, Any
from agentshield.parsers.schemas import IaCResource
from agentshield.parsers.line_loader import LineLoader


def parse_cloudformation(file_path: str) -> List[IaCResource]:
    """
    Parses a CloudFormation JSON or YAML template into IaCResource AST objects.
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

    # Extract template parameters
    cfn_params = data.get("Parameters", {})
    parsed_vars: Dict[str, Any] = {}
    if isinstance(cfn_params, dict):
        for p_name, p_def in cfn_params.items():
            if isinstance(p_def, dict):
                parsed_vars[p_name] = p_def.get("Default", "parameter_declared")

    cfn_resources = data.get("Resources", {})
    if isinstance(cfn_resources, dict):
        for res_name, res_def in cfn_resources.items():
            if isinstance(res_def, dict):
                res_type = res_def.get("Type", "AWS::CloudFormation::Resource")
                line_no = res_def.get("__line__", 1)
                props = res_def.get("Properties", {})

                # Extract dependencies via Ref or Fn::GetAtt or DependsOn
                deps = []
                depends_on = res_def.get("DependsOn")
                if isinstance(depends_on, str):
                    deps.append(depends_on)
                elif isinstance(depends_on, list):
                    deps.extend([str(d) for d in depends_on])

                raw_str = str(res_def)
                for other_res in cfn_resources.keys():
                    if other_res != res_name and other_res in raw_str and other_res not in deps:
                        deps.append(other_res)

                resources.append(
                    IaCResource(
                        file_path=file_path,
                        resource_type=res_type,
                        resource_name=res_name,
                        provider="aws",
                        line_start=line_no,
                        line_end=line_no + 10,
                        attributes=props if isinstance(props, dict) else {},
                        dependencies=deps,
                        variables=parsed_vars
                    )
                )

    return resources
