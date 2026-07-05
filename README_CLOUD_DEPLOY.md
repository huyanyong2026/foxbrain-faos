# FoxBrain Cloud Edition Deploy

This guide deploys FoxBrain V4 Cloud Edition to an Ubuntu Tencent Cloud server.

## Server Requirements

- Ubuntu 22.04 or newer
- 2 CPU / 4 GB RAM minimum
- 20 GB disk minimum
- Security group open for the port you publish, normally `80/443` through a reverse proxy or `8088` for direct testing

## One-command Install

```bash
curl -fsSL https://raw.githubusercontent.com/huyanyong2026/foxbrain-v4/main/install.sh -o install.sh
chmod +x install.sh
sudo APP_DIR=/opt/foxbrain-v4 REPO_URL=https://github.com/huyanyong2026/foxbrain-v4.git ./install.sh
```

Then edit:

```bash
sudo nano /opt/foxbrain-v4/.env
```

Never put real passwords in GitHub.

## Start / Stop

```bash
cd /opt/foxbrain-v4
sudo docker compose up -d --build
sudo docker compose logs -f
sudo docker compose down
```

## Health Check

```bash
curl http://127.0.0.1:8088/api/health
```

Browser test:

```text
http://SERVER_IP:8088
```

## Nginx Reverse Proxy

Install Nginx:

```bash
sudo apt-get update
sudo apt-get install -y nginx
```

Copy the example config:

```bash
sudo cp /opt/foxbrain-v4/deploy/nginx/foxbrain.conf.example /etc/nginx/sites-available/foxbrain
sudo ln -sf /etc/nginx/sites-available/foxbrain /etc/nginx/sites-enabled/foxbrain
sudo nginx -t
sudo systemctl reload nginx
```

Then visit:

```text
http://huyan.vafox.com
```

For HTTPS after DNS points to the server:

```bash
sudo apt-get install -y certbot python3-certbot-nginx
sudo certbot --nginx -d huyan.vafox.com
```

Nginx forwards traffic to the Docker container on `127.0.0.1:8088`.

## Persistent Data

Docker volumes keep runtime data:

- `foxbrain_portal`: SQLite database, secret key, uploads
- `foxbrain_sap_sync`: SAP summary files
- `./logs`: deployment and SAP sync logs

## Long-running Cloud Behavior

The service runs on the Tencent Cloud server, not on your personal computer.

`docker-compose.yml` uses:

```yaml
restart: always
```

So FoxBrain restarts automatically after:

- container crash
- Docker restart
- Ubuntu server reboot

Your computer can be turned off after deployment. The cloud server keeps running independently.

## SAP Nightly Sync

`install.sh` installs a cron job:

```cron
0 22 * * * cd /opt/foxbrain-v4 && docker compose exec -T foxbrain python sync_sap_b1.py --trigger scheduled_22_00 >> /opt/foxbrain-v4/logs/sap_sync.log 2>&1
```

Required safe environment variables are in `.env.example`.

## GitHub Actions Deployment

Create repository secrets:

- `CLOUD_HOST`: server IP or domain
- `CLOUD_USER`: usually `ubuntu`
- `CLOUD_SSH_KEY`: private SSH key with access to the server
- `CLOUD_APP_DIR`: optional, defaults to `/opt/foxbrain-v4`

Push to `main`, then GitHub Actions deploys automatically.

## Rollback

```bash
cd /opt/foxbrain-v4
sudo git log --oneline -5
sudo git checkout <commit>
sudo docker compose up -d --build
```

To disable SAP scheduled sync:

```bash
sudo rm -f /etc/cron.d/foxbrain-sap-sync
```
