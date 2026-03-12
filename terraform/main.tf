locals {
  bucket_name = "${var.project_name}-bucket"
  key_name    = "${var.project_name}-key"
}

resource "aws_key_pair" "project_key" {
  key_name   = local.key_name
  public_key = file("${path.module}/${var.public_key_path}")
}

resource "aws_security_group" "web_sg" {
  name        = "${var.project_name}-sg"
  description = "Security group for Flask web server"

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.allowed_ssh_cidr]
  }

  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = [var.allowed_http_cidr]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_s3_bucket" "static_files" {
  bucket = local.bucket_name
}

resource "aws_s3_bucket_public_access_block" "static_files_block" {
  bucket = aws_s3_bucket.static_files.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Rôle IAM pour que l'instance EC2 puisse accéder au bucket S3
resource "aws_iam_role" "flask_ec2_role" {
  name = "${var.project_name}-ec2-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "ec2.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy" "flask_s3_policy" {
  name = "${var.project_name}-s3-policy"
  role = aws_iam_role.flask_ec2_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "s3:GetObject",
        "s3:PutObject",
        "s3:ListBucket",
        "s3:DeleteObject"
      ]
      Resource = [
        aws_s3_bucket.static_files.arn,
        "${aws_s3_bucket.static_files.arn}/*"
      ]
    }]
  })
}

resource "aws_iam_instance_profile" "flask_profile" {
  name = "${var.project_name}-profile"
  role = aws_iam_role.flask_ec2_role.name
}

data "aws_ami" "ubuntu" {
  most_recent = true

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  owners = ["099720109477"] # Canonical
}

resource "aws_instance" "flask_server" {
  ami                         = data.aws_ami.ubuntu.id
  instance_type               = var.instance_type
  key_name                    = aws_key_pair.project_key.key_name
  vpc_security_group_ids      = [aws_security_group.web_sg.id]
  associate_public_ip_address = true
  iam_instance_profile        = aws_iam_instance_profile.flask_profile.name

  user_data = templatefile("${path.module}/../provisioning/user_data.sh", {
    project_name     = var.project_name
    bucket_name      = aws_s3_bucket.static_files.bucket
    aws_region       = var.aws_region
    app_py_b64       = base64encode(file("${path.module}/../app/app.py"))
    requirements_b64 = base64encode(file("${path.module}/../app/requirements.txt"))
  })

  user_data_replace_on_change = true

  tags = {
    Name = "${var.project_name}-flask-server"
  }
}

