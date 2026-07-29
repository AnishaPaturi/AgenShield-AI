resource "aws_s3_bucket" "vulnerable_bucket" {
  bucket = "my-insecure-test-bucket-agent-shield"
  acl    = "public-read"

  tags = {
    Environment = "Dev"
    ManagedBy   = "Terraform"
  }
}
