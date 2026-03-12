#!/bin/bash
set -e

PROJECT_NAME="${project_name}"
S3_BUCKET_NAME="${bucket_name}"
AWS_REGION="${aws_region}"

apt-get update -y
apt-get install -y python3 python3-venv python3-pip git

mkdir -p /opt/${PROJECT_NAME}
cd /opt/${PROJECT_NAME}

git clone https://github.com/example/projet-cloud-flask.git app || true

if [ -d "app/app" ]; then
  cd app/app
else
  cd app || true
fi

python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

cat > .env <<EOF
S3_BUCKET_NAME=${S3_BUCKET_NAME}
AWS_REGION=${AWS_REGION}
EOF

cat >/etc/systemd/system/flask-app.service <<EOF
[Unit]
Description=Flask App
After=network.target

[Service]
User=root
WorkingDirectory=/opt/${PROJECT_NAME}/app
Environment="S3_BUCKET_NAME=${S3_BUCKET_NAME}" "AWS_REGION=${AWS_REGION}"
ExecStart=/opt/${PROJECT_NAME}/app/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable flask-app
systemctl start flask-app

