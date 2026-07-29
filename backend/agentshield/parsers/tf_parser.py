"""
Terraform (HCL / JSON) Multi-Cloud IaC Parser.
Supports AWS, Azure, GCP resource types, dynamic variables, and dependency extraction.
"""

import os
import re
from typing import List, Dict, Any
from agentshield.parsers.schemas import IaCResource, ParsedIaCFile


def parse_terraform(file_path: str) -> List[IaCResource]:
    """
    Parses a Terraform HCL / JSON file into IaCResource AST objects with multi-cloud provider detection.
    """
    resources = []
    if not os.path.exists(file_path):
        return resources

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    lines = content.splitlines()

    # Regex patterns
    resource_pattern = re.compile(r'resource\s+"([^"]+)"\s+"([^"]+)"\s*\{')
    var_pattern = re.compile(r'variable\s+"([^"]+)"\s*\{')
    ref_pattern = re.compile(r'\b(aws_[a-z0-9_]+|azurerm_[a-z0-9_]+|google_[a-z0-9_]+)\.([a-z0-9_]+)\b')

    # Extract dynamic variables declared in file
    declared_vars: Dict[str, Any] = {}
    for i, line in enumerate(lines, start=1):
        v_match = var_pattern.search(line)
        if v_match:
            declared_vars[v_match.group(1)] = "variable_declared"

    for i, line in enumerate(lines, start=1):
        match = resource_pattern.search(line)
        if match:
            res_type = match.group(1)
            res_name = match.group(2)

            # Cloud provider classification
            provider = "aws"
            if res_type.startswith("azurerm_"):
                provider = "azure"
            elif res_type.startswith("google_"):
                provider = "gcp"

            # Determine line bounds
            line_end = i
            depth = 0
            block_lines = []
            for j in range(i - 1, len(lines)):
                curr_line = lines[j]
                block_lines.append(curr_line)
                depth += curr_line.count("{") - curr_line.count("}")
                if depth == 0 and j >= i - 1:
                    line_end = j + 1
                    break

            raw_code = "\n".join(block_lines)

            # Dependency extraction from raw code
            deps = []
            for ref in ref_pattern.finditer(raw_code):
                ref_type, ref_name = ref.group(1), ref.group(2)
                target_id = f"{ref_type}.{ref_name}"
                if target_id != f"{res_type}.{res_name}" and target_id not in deps:
                    deps.append(target_id)

            resources.append(
                IaCResource(
                    file_path=file_path,
                    resource_type=res_type,
                    resource_name=res_name,
                    provider=provider,
                    line_start=i,
                    line_end=line_end,
                    attributes={"raw_code": raw_code},
                    dependencies=deps,
                    variables=declared_vars
                )
            )

    return resources
