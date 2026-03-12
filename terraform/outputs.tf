output "instance_public_ip" {
  description = "Public IP of the Flask server"
  value       = aws_instance.flask_server.public_ip
}

output "app_url" {
  description = "URL to access the Flask app"
  value       = "http://${aws_instance.flask_server.public_ip}"
}

output "s3_bucket_name" {
  description = "Name of the S3 bucket used for static files"
  value       = aws_s3_bucket.static_files.bucket
}

