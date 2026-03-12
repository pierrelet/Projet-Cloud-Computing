#!/bin/bash
set -e

PROJECT_NAME="${project_name}"
S3_BUCKET_NAME="${bucket_name}"
AWS_REGION="${aws_region}"

apt-get update -y
apt-get install -y python3 python3-venv python3-pip

APP_DIR="/opt/$PROJECT_NAME/app"
mkdir -p "$APP_DIR"
cd "$APP_DIR"

echo "${app_py_b64}" | base64 -d > app.py
echo "${requirements_b64}" | base64 -d > requirements.txt

python3 -m venv venv
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt

cat > /etc/systemd/system/flask-app.service <<EOF
[Unit]
Description=Flask App
After=network.target

[Service]
User=root
WorkingDirectory=$APP_DIR
Environment="S3_BUCKET_NAME=$S3_BUCKET_NAME" "AWS_REGION=$AWS_REGION"
ExecStart=$APP_DIR/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable flask-app
systemctl start flask-app
