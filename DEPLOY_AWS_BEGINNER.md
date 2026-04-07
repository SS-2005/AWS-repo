# AWS Deployment Guide for Beginners

This project is ready to deploy on AWS using **AWS App Runner**. That is the simplest beginner-friendly option because AWS manages the public URL, scaling, and service runtime for you.

## What was added in this deployment-ready package
- `Procfile` for a production start command
- `gunicorn` in `requirements.txt`
- `Dockerfile` for container-based deployment if needed later
- `apprunner.yaml` for AWS App Runner source deployment
- `/health` route in `app.py`
- better image URL validation and request timeouts

## Best path: Deploy with AWS App Runner

### 1. Create a GitHub repository or update your existing one
Push this updated project to GitHub.

### 2. Open AWS Console
Search for **App Runner**.

### 3. Create service
- Click **Create service**
- Source: **Source code repository**
- Provider: **GitHub**
- Connect your GitHub account if AWS asks
- Select this repository and branch

### 4. Configure deployment
Choose **Automatic** or **Manual** deployment. For a first deployment, Manual is safer.

### 5. Build configuration
Since `apprunner.yaml` is included, App Runner can use it.
If AWS asks for commands manually, use:
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app --bind 0.0.0.0:5000 --timeout 120`
- Port: `5000`

### 6. Instance size
Start with a small instance. If TensorFlow fails because of memory, redeploy with a larger instance size.

### 7. Deploy
Click **Create & deploy**.
Wait for the build and startup to finish.

### 8. Test the app
Open the public App Runner URL and test:
- `/`
- `/health`
- upload a dog image and run prediction

## Backup option: Deploy on EC2
Use EC2 only if App Runner gives build/runtime issues.

### Launch EC2
- AMI: Ubuntu
- Instance type: t3.small or t3.medium
- Allow inbound ports: 22, 80, 443

### Connect and install dependencies
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-pip python3-venv git nginx

git clone <your-repo-url>
cd DIP-Dog_Identification_Project-main
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Test app
```bash
gunicorn app:app --bind 0.0.0.0:5000
```
Open `http://EC2_PUBLIC_IP:5000`

### Make it persistent with systemd
Create `/etc/systemd/system/dogapp.service`:
```ini
[Unit]
Description=Dog Identification Flask App
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/DIP-Dog_Identification_Project-main
Environment="PATH=/home/ubuntu/DIP-Dog_Identification_Project-main/.venv/bin"
ExecStart=/home/ubuntu/DIP-Dog_Identification_Project-main/.venv/bin/gunicorn app:app --bind 0.0.0.0:5000 --timeout 120
Restart=always

[Install]
WantedBy=multi-user.target
```

Then run:
```bash
sudo systemctl daemon-reload
sudo systemctl enable dogapp
sudo systemctl start dogapp
sudo systemctl status dogapp
```

### Configure nginx
Create `/etc/nginx/sites-available/dogapp`:
```nginx
server {
    listen 80;
    server_name _;

    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

Enable it:
```bash
sudo ln -s /etc/nginx/sites-available/dogapp /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

Now open `http://EC2_PUBLIC_IP`

## Important notes
- The model file is large and TensorFlow uses a lot of memory.
- If App Runner build fails, the quickest fix is usually increasing memory or using the included Dockerfile.
- Keep `full-image-set-mobilenetv2-adam.h5` and `labels.csv` in the project root.
