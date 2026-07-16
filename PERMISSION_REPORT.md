# FoxBrain FAOS V0.20.5 Permission Governance Report

## Scope

Production application path: `/opt/foxbrain-faos`.

This report documents the permission model required for the deployment user to operate the application without changing SSL material or unrelated system files.

## Required ownership model

- `/opt/foxbrain-faos` should be owned by the deployment user and deployment group.
- The deployment user must be able to:
  - run `git pull --ff-only` in `/opt/foxbrain-faos`;
  - modify `docker-compose.yml`, `docker-compose.prod.yml`, and deployment scripts;
  - edit `.env` intentionally when production configuration changes are approved;
  - run `docker compose build`, `docker compose up -d`, `docker compose ps`, and `docker compose logs`.
- The deployment user should be in the `docker` group, or deployment automation should run Docker through the approved host privilege mechanism.

## Recommended commands

Run these on the production host after replacing `DEPLOY_USER` and `DEPLOY_GROUP` with the real deployment account values:

```bash
sudo chown -R DEPLOY_USER:DEPLOY_GROUP /opt/foxbrain-faos
sudo find /opt/foxbrain-faos -type d -exec chmod 775 {} \;
sudo find /opt/foxbrain-faos -type f -exec chmod 664 {} \;
sudo find /opt/foxbrain-faos -type f -name '*.sh' -exec chmod 775 {} \;
sudo usermod -aG docker DEPLOY_USER
```

## Explicit exclusions

Do not change permissions for:

- `/etc/letsencrypt`;
- `/etc/nginx`;
- `/var/www/certbot` unless ACME challenge ownership is separately approved;
- other system-managed files outside `/opt/foxbrain-faos`.

## Validation

After permission repair, validate with:

```bash
cd /opt/foxbrain-faos
git pull --ff-only
docker compose config >/dev/null
docker compose build foxbrain-web foxbrain-api foxbrain-worker
docker compose ps
```
