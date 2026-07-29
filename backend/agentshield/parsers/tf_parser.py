"""
Terraform (HCL / JSON) IaC Parser.
"""

import os
import re
import json
from typing import List
from agentshield.parsers.schemas import IaCResource


def parse_terraform(file_path: str) -> List[IaCResource]:
    """
    Parses a Terraform HCL / json file into a list of IaCResource objects.
    """
    resources = []
    if not os.path.exists(file_path):
        return resources

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    lines = content.splitlines()

    # Regex pattern matching HCL resource blocks: resource "type" "name" {
    pattern = re.compile(r'resource\s+"([^"]+)"\s+"([^"]+)"\s*\{')

    for i, line in enumerate(lines, start=1):
        match = pattern.search(line)
        if match:
            res_type = match.group(1)
            res_name = match.group(2)
            
            # Determine provider (aws, azure, gcp, etc.)
            provider = "aws"
            if res_type.startswith("azurerm_"):
                provider = "azure"
            elif res_type.startswith("google_"):
                provider = "gcp"

            # Capture block lines
            block_content = {}
            line_end = i
            depth = 0
            for j in range(i - 1, len(lines)):
                curr_line = lines[j]
                depth += curr_line.count("{") - curr_line.count("}")
                if depth == 0 and j >= i - 1:
                    line_end = j + 1
                    break

            resources.append(
                IaCResource(
                    file_path=file_path,
                    resource_type=res_type,
                    resource_name=res_name,
                    provider=provider,
                    line_start=i,
                    line_end=line_end,
                    attributes={"raw_code": "\n".join(lines[i-1:line_end])}
                )
            )

    return resources
