# test all 3 functions of parsing, resource extraction and normalization
# and print their values in the terminal
import json

from agentshield.parsers.terraform import (
    parse_terraform_file,
    extract_terraform_resources,
)

from agentshield.parsers.normalizer import (
    normalize_terraform_resources,
)


FILE_PATH = "tests/fixtures/terraform/sample.tf"


# --------------------------------------------------
# ORIGINAL TERRAFORM
# --------------------------------------------------


print("ORIGINAL TERRAFORM")
print("\n")

with open(FILE_PATH, "r", encoding="utf-8") as file:
    print(file.read())


# --------------------------------------------------
# STEP 1: PARSING
# --------------------------------------------------

parsed_data = parse_terraform_file(FILE_PATH)

print("\n")
print("STEP 1: AFTER PARSING")
print("\n")

print(json.dumps(parsed_data, indent=2))


# --------------------------------------------------
# STEP 2: RESOURCE EXTRACTION
# --------------------------------------------------

resources = extract_terraform_resources(parsed_data)

print("\n")
print("STEP 2: AFTER RESOURCE EXTRACTION")
print("\n")

print(json.dumps(resources, indent=2))


# --------------------------------------------------
# STEP 3: NORMALIZATION
# --------------------------------------------------

normalized_resources = normalize_terraform_resources(resources)

print("\n")
print("STEP 3: AFTER NORMALIZATION")


print(json.dumps(normalized_resources, indent=2))