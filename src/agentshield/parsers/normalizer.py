from typing import Any


def normalize_value(value: Any) -> Any:
    """
    Recursively normalize values produced by the Terraform parser.
    """

    if isinstance(value, dict):
        return {
            key: normalize_value(item)
            for key, item in value.items()
        }

    if isinstance(value, list):

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