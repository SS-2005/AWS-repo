# Beginner-friendly AWS EC2 deployment guide for the Dog Identification app

This bundle is the version you should use for deployment on AWS EC2.

## What changed in this bundle
- Added `gunicorn` for production serving.
- Added `/health` and `/warmup` endpoints.
- Switched model loading to lazy loading so the server can start faster.
- Added systemd and nginx config files.
- Added a one-command setup script: `deploy/setup_ec2.sh`

## Recommended AWS choice
Use **EC2**, not Elastic Beanstalk and not S3 static hosting.

## Part 1: Create your EC2 server
1. Open AWS Console.
2. Search for **EC2**.
3. Click **Launch instance**.
4. Set these values:
   - Name: `dog-identification-app`
   - AMI: **Ubuntu** (22.04 or newer is fine)
   - Instance type: **t3.medium**
5. Security group inbound rules:
   - SSH, port 22, Source: **My IP**
   - HTTP, port 80, Source: **Anywhere**
   - HTTPS, port 443, Source: **Anywhere**
6. Launch the instance.

## Part 2: Connect to the instance
1. Wait until the instance state is **Running**.
2. Select the instance.
3. Click **Connect**.
4. Open the **EC2 Instance Connect** tab.
5. Click **Connect**.

## Part 3: Upload this project bundle to the server
You have 2 easy options.

### Option A: Use GitHub
1. Upload this bundle's contents to a GitHub repo.
2. In the EC2 terminal, run:
   ```bash
   git clone YOUR_GITHUB_REPO_URL dog-app
   cd dog-app
   ```

### Option B: Upload the zip manually
1. In the EC2 terminal, run:
   ```bash
   sudo apt update
   sudo apt install -y unzip
   mkdir -p ~/dog-app
   ```
2. Upload the zip to the server using the EC2 console file upload if available, or use WinSCP / SCP from your computer.
3. Extract it:
   ```bash
   cd ~/dog-app
   unzip YOUR_ZIP_NAME.zip
   ```

## Part 4: Run the setup script
From inside the project folder, run:
```bash
bash deploy/setup_ec2.sh
```

This installs Python packages, sets up Gunicorn, configures Nginx, and starts the app.

## Part 5: Test the app
Open these in your browser:
- `http://YOUR_PUBLIC_IP/health`
- `http://YOUR_PUBLIC_IP/warmup`
- `http://YOUR_PUBLIC_IP/`

### What each URL does
- `/health` checks that the app is alive.
- `/warmup` loads the TensorFlow model once.
- `/` opens the website.

## Useful commands if something breaks
Run these in the EC2 terminal:
```bash
sudo systemctl status dogapp
sudo journalctl -u dogapp -n 100 --no-pager
sudo systemctl status nginx
```

## Important note
The first `/warmup` call can take some time because TensorFlow loads the `.h5` model into memory.
