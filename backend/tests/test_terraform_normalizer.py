from agentshield.parsers.normalizer import (
    normalize_terraform_resources,
)
from agentshield.parsers.terraform import (
    extract_terraform_resources,
    parse_terraform_file,
)


def test_normalize_terraform_resources():
    # Parse Terraform
    parsed_data = parse_terraform_file(
        "tests/fixtures/terraform/sample.tf"
    )

    # Extract resources
    resources = extract_terraform_resources(parsed_data)

    # Normalize resources
    normalized = normalize_terraform_resources(resources)

    # We expect 3 resources
    assert len(normalized) == 3

    # Test S3 bucket
    s3 = normalized[0]

    assert (
        s3["properties"]["bucket"]
        == "my-app-data-bucket"
    )

    # Test security group
    security_group = normalized[1]

    ingress = security_group["properties"]["ingress"]

    assert len(ingress) == 1
    assert ingress[0]["from_port"] == 22
    assert ingress[0]["to_port"] == 22
    assert ingress[0]["protocol"] == "tcp"

    assert ingress[0]["cidr_blocks"] == [
        "0.0.0.0/0"
    ]

    # Test database
    database = normalized[2]

    assert (
        database["properties"]["storage_encrypted"]
        is False
    )

    assert (
        database["properties"]["publicly_accessible"]
        is True
    )