from typing import Any


def normalize_value(value: Any, key: str | None = None) -> Any:
    """
    Recursively normalize values produced by the Terraform parser.
    """

    if isinstance(value, dict):
        return {
            k: normalize_value(item, k)
            for k, item in value.items()
        }

    if isinstance(value, list):
        # Known list attributes should remain lists
        if key in {"cidr_blocks", "ipv6_cidr_blocks", "security_groups", "subnets", "availability_zones", "ingress", "egress"}:
            return [normalize_value(item) for item in value]

        # Parser wrapper around a single scalar value
        if len(value) == 1 and not isinstance(
            value[0], (list, dict)
        ):
            return normalize_value(value[0])

        # Nested list wrapper, for example:
        # [["0.0.0.0/0"]] -> ["0.0.0.0/0"]
        if (
            len(value) == 1
            and isinstance(value[0], list)
        ):
            return [
                normalize_value(item)
                for item in value[0]
            ]

        # Genuine list
        return [
            normalize_value(item)
            for item in value
        ]

    if isinstance(value, str):
        if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
            return value[1:-1]

    return value

def normalize_terraform_resource(resource: dict) -> dict:
    """
    Normalize an extracted Terraform resource.
    """

    normalized_resource = resource.copy()

    normalized_resource["properties"] = normalize_value(
        resource.get("properties", {})
    )

    return normalized_resource



def normalize_terraform_resources(resources: list[dict]) -> list[dict]:
    """
    Normalize a collection of extracted Terraform resources.
    """

    return [
        normalize_terraform_resource(resource)
        for resource in resources
    ]