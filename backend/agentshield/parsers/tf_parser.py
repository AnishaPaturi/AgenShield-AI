"""
Terraform (HCL) parser for AgentShield AI.

Takes a raw .tf file and returns a normalized list of resource objects:

    {
        "resource_type": "aws_s3_bucket",
        "resource_name": "data_bucket",
        "provider": "aws",
        "attributes": { ... cleaned key-value pairs ... },
        "source_file": "sample.tf"
    }

This normalized shape is what downstream agents (retrieval, detection,
remediation) will consume — regardless of whether the original file was
Terraform, CloudFormation, etc. Keeping this schema stable is what makes
the "multi-cloud" claim real rather than cosmetic.
"""

import hcl2
from pathlib import Path


def _strip_quotes(value):
    """
    python-hcl2 sometimes returns plain string values with literal
    surrounding quotes still attached (e.g. '"us-east-1"' instead of
    'us-east-1'). Clean that up recursively across nested structures.
    """
    if isinstance(value, str):
        if len(value) >= 2 and value.startswith('"') and value.endswith('"'):
            return value[1:-1]
        return value
    elif isinstance(value, list):
        return [_strip_quotes(v) for v in value]
    elif isinstance(value, dict):
        return {
            (k[1:-1] if isinstance(k, str) and k.startswith('"') and k.endswith('"') else k):
            _strip_quotes(v)
            for k, v in value.items()
            if k != "__is_block__"
        }
    else:
        return value


def parse_terraform_file(filepath: str) -> list[dict]:
    """
    Parse a single .tf file and return a list of normalized resource dicts.
    """
    filepath = Path(filepath)
    with open(filepath, "r") as f:
        raw = hcl2.load(f)

    normalized_resources = []

    for resource_block in raw.get("resource", []):
        for raw_type, named_resources in resource_block.items():
            resource_type = raw_type.strip('"')
            provider = resource_type.split("_")[0]

            for raw_name, attrs in named_resources.items():
                resource_name = raw_name.strip('"')
                clean_attrs = _strip_quotes(attrs)

                normalized_resources.append({
                    "resource_type": resource_type,
                    "resource_name": resource_name,
                    "provider": provider,
                    "attributes": clean_attrs,
                    "source_file": filepath.name,
                })

    return normalized_resources


def parse_terraform_directory(dirpath: str) -> list[dict]:
    """
    Parse every .tf file in a directory and return one combined list of
    normalized resources. Real Terraform projects are almost always split
    across multiple files, so this is the entry point you'll actually use
    once you're scanning a whole project instead of a single file.
    """
    dirpath = Path(dirpath)
    all_resources = []
    for tf_file in sorted(dirpath.glob("*.tf")):
        all_resources.extend(parse_terraform_file(tf_file))
    return all_resources