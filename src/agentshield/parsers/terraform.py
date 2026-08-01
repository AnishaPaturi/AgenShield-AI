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