import json

from agentshield.parsers.terraform import parse_terraform_file


def test_parse_terraform_file():
    result = parse_terraform_file(
        "tests/fixtures/terraform/sample.tf"
    )

    print("\nParsed Terraform:")
    print(json.dumps(result, indent=2))

    assert isinstance(result, dict)
    assert "resource" in result