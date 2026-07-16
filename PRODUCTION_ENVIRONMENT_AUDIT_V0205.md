# VAFOX Enterprise OS V0.20.5 Production Environment Audit

## Scope

This audit covers the infrastructure road-repair items for VAFOX FAOS production hardening:

- Docker and Docker Compose
- Nginx exposure and reverse proxy health
- GitHub Actions deployment automation
- Environment-file safety
- Runtime permissions and operational boundaries
- Health checks and rollback readiness

## Non-negotiable platform boundary

SAP B1 remains the enterprise system of fact. VAFOX Huyan must not hold SAP credentials, write SAP data, or schedule direct SAP synchronization. Huyan reads operating facts through Core (`CORE_BASE_URL` and `CORE_API_TOKEN`) only. AI may analyze, reason, and recommend, but it must not persist a second set of operating facts.

## Findings and repairs

### 1. Docker Compose public ingress

**Finding:** Docker nginx was configured with `expose: 80`, which only exposes the port to the Docker network. A fresh production install could start containers successfully while leaving the app unreachable from the host.

**Repair:** `nginx` now publishes `${HTTP_PORT:-80}:80`, with `HTTP_PORT` documented in `.env.example`.

### 2. Docker Compose service health

**Finding:** Core services had health checks, but nginx and qdrant did not have production health gates. GitHub Actions deployment also only waited for the app and worker services.

**Repair:** Added nginx and qdrant health checks and included nginx in the production deployment health gate.

### 3. GitHub Actions production deploy hardening

**Finding:** The production workflow used a hardcoded host IP and did not fail early when required production secrets were missing.

**Repair:** Production deploy now requires `PRODUCTION_SSH_HOST`, `PRODUCTION_SSH_USER`, `PRODUCTION_SSH_KEY`, and `PRODUCTION_DEPLOY_PATH`, validates `docker compose config` remotely, and waits for nginx health in addition to the application services.

### 4. Environment-file safety

**Finding:** `deploy.sh` could deploy with placeholder production secrets or direct SAP-related environment variables.

**Repair:** Deployment now refuses to continue when `.env` is missing, placeholder secrets are still present, or SAP credential-style variables are present in Huyan.

### 5. SAP/Core/AI responsibility split

**Finding:** `install.sh` created a legacy `foxbrain-sap-sync` cron entry from the Huyan deployment path. That violated the platform boundary that Huyan must read business facts through Core only.

**Repair:** Installation now removes the legacy direct SAP cron if present and only installs the backup cron. SAP synchronization must be handled outside Huyan by the approved Core read-only path.

### 6. Backup and restore posture

**Finding:** Backup and restore scripts exist and cover `.env`, PostgreSQL, MinIO, portal data, and qdrant volumes. They are suitable as a first production baseline, but recovery drills should be scheduled.

**Recommended next action:** Run a restore drill on a staging host after this road-repair release.

## Required production secrets

GitHub Actions production deployment requires:

- `PRODUCTION_SSH_HOST`
- `PRODUCTION_SSH_USER`
- `PRODUCTION_SSH_KEY`
- `PRODUCTION_DEPLOY_PATH`

The server `.env` must define strong non-placeholder values for:

- `PORTAL_INITIAL_ADMIN_PASSWORD`
- `ADMIN_PASSWORD`
- `POSTGRES_PASSWORD`
- `MINIO_ROOT_PASSWORD`
- `JWT_SECRET`
- `ENCRYPTION_KEY`
- `CORE_API_TOKEN`

The server `.env` must not define direct SAP credential variables such as `SAP_*`, `B1_*`, or `SAPB1_*`.

## Release checklist

1. Confirm production server `.env` has no placeholder secrets and no SAP credentials.
2. Confirm GitHub production secrets listed above are configured.
3. Run `docker compose config` before deployment.
4. Deploy from GitHub Actions.
5. Confirm `docker compose ps` shows healthy app, worker, nginx, database, Redis, MinIO, and qdrant services.
6. Run `bash healthcheck.sh` on the server.
7. Confirm backups are being written under `$APP_DIR/backups`.

## Result

VAFOX remains functionally unchanged at the business layer. This release repairs production infrastructure so the platform is safer to deploy, easier to verify, and aligned with the SAP/Core/AI operating boundary.
