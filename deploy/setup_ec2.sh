#!/usr/bin/env bash
set -e

APP_DIR="/home/ubuntu/dog-app"

sudo apt update
sudo apt install -y python3-pip python3-venv git nginx

mkdir -p "$APP_DIR"
cp -r . "$APP_DIR"
cd "$APP_DIR"

python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

sudo cp deploy/dogapp.service /etc/systemd/system/dogapp.service
sudo cp deploy/nginx-dogapp.conf /etc/nginx/sites-available/dogapp
sudo ln -sf /etc/nginx/sites-available/dogapp /etc/nginx/sites-enabled/dogapp
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl daemon-reload
sudo systemctl enable dogapp
sudo systemctl restart dogapp
sudo systemctl restart nginx

echo "Setup complete. Test these URLs:"
echo "1) http://YOUR_PUBLIC_IP/health"
echo "2) http://YOUR_PUBLIC_IP/warmup"
echo "3) http://YOUR_PUBLIC_IP/"
