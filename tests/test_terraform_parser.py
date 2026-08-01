import json

from agentshield.parsers.terraform import parse_terraform_file
from agentshield.parsers.terraform import (
    extract_terraform_resources,
    parse_terraform_file,
)

def test_parse_terraform_file():
    result = parse_terraform_file(
        "tests/fixtures/terraform/sample.tf"
    )

    print("\nParsed Terraform:")
    print(json.dumps(result, indent=2))

    assert isinstance(result, dict)
    assert "resource" in result
    
def test_extract_terraform_resources():
    parsed_data = parse_terraform_file(
        "tests/fixtures/terraform/sample.tf"
    )

    resources = extract_terraform_resources(parsed_data)

    assert len(resources) == 3

    assert resources[0]["resource_id"] == "aws_s3_bucket.data_bucket"
    assert resources[0]["resource_type"] == "aws_s3_bucket"
    assert resources[0]["resource_name"] == "data_bucket"

    assert resources[1]["resource_id"] == "aws_security_group.web_sg"

    assert resources[2]["resource_id"] == "aws_db_instance.app_db"