resource "aws_s3_bucket" "data_bucket" {
  bucket = "my-app-data-bucket"
}


resource "aws_security_group" "web_sg" {
  name        = "web-sg"
  description = "Allow web and SSH traffic"

  ingress {
    description = "SSH from anywhere"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_db_instance" "app_db" {
  identifier          = "app-database"
  engine              = "postgres"
  storage_encrypted   = false
  publicly_accessible = true
}