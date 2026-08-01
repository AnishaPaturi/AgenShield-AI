from pathlib import Path

import hcl2


def parse_terraform_file(file_path: str) -> dict:
    """
    Parse a Terraform (.tf) file into a Python dictionary.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Terraform file not found: {file_path}"
        )

    if path.suffix.lower() != ".tf":
        raise ValueError(
            f"Expected a .tf file, got: {path.suffix}"
        )

    with path.open("r", encoding="utf-8") as file:
        parsed_data = hcl2.load(file)

    return parsed_data

def extract_terraform_resources(parsed_data: dict) -> list[dict]:
    """
    Extract individual Terraform resources from parsed HCL data.
    """

    resources = []

    resource_blocks = parsed_data.get("resource", [])

    for resource_block in resource_blocks:
        for raw_resource_type, resource_instances in resource_block.items():
            for raw_resource_name, resource_body in resource_instances.items():
                resource_type = str(raw_resource_type).strip('"').strip("'")
                resource_name = str(raw_resource_name).strip('"').strip("'")

                start_line = resource_body.get("__start_line__")
                end_line = resource_body.get("__end_line__")

                properties = {
                    key: value
                    for key, value in resource_body.items()
                    if key not in {"__start_line__", "__end_line__"}
                }

                resources.append({
                    "resource_id": f"{resource_type}.{resource_name}",
                    "resource_type": resource_type,
                    "resource_name": resource_name,
                    "properties": properties,
                    "start_line": start_line,
                    "end_line": end_line,
                })

    return resources