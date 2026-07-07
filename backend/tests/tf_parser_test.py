from pathlib import Path
from agentshield.parsers.tf_parser import parse_terraform_file

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "terraform"


def test_parses_all_resources():
    resources = parse_terraform_file(FIXTURE_DIR / "sample.tf")
    assert len(resources) == 3


def test_s3_bucket_parsed_correctly():
    resources = parse_terraform_file(FIXTURE_DIR / "sample.tf")
    bucket = next(r for r in resources if r["resource_type"] == "aws_s3_bucket")

    assert bucket["resource_name"] == "data_bucket"
    assert bucket["provider"] == "aws"
    assert bucket["attributes"]["bucket"] == "my-app-data-bucket"


def test_security_group_ingress_is_parsed_as_list():
    resources = parse_terraform_file(FIXTURE_DIR / "sample.tf")
    sg = next(r for r in resources if r["resource_type"] == "aws_security_group")

    assert isinstance(sg["attributes"]["ingress"], list)
    assert sg["attributes"]["ingress"][0]["cidr_blocks"] == ["0.0.0.0/0"]


def test_no_quotes_leak_into_string_values():
    resources = parse_terraform_file(FIXTURE_DIR / "sample.tf")
    db = next(r for r in resources if r["resource_type"] == "aws_db_instance")

    assert db["attributes"]["engine"] == "postgres"
    assert not db["attributes"]["engine"].startswith('"')