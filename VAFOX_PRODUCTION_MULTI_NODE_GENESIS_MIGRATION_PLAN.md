# VAFOX Production Multi-Node Genesis Migration Plan

## Scope

Upgrade the remaining production nodes to VAFOX Genesis after the successful `Huyan.vafox.com` production cutover:

- `gateway.vafox.com`
- `ai.vafox.com`
- `core.vafox.com`

Target runtime:

- System: `VAFOX`
- Version: `AI-OS-V6-CLEAN-REBUILD-V1`
- Image: `vafox-genesis:AI-OS-V6-CLEAN-REBUILD-V1`
- Production directory baseline: `/opt/foxbrain-faos`
- Orchestration: Docker Compose behind nginx

## Non-Negotiable Safety Rules

1. Do not delete databases.
2. Do not delete Docker volumes.
3. Do not delete old backups.
4. Do not directly remove old systemd services or legacy files during discovery.
5. Do not modify core data structures as part of this migration.
6. Do not cut over before discovery, backup, compose validation, image build validation, and health checks are complete.
7. Every production change must produce a report under `migration-reports/`.

## Operator Variables

Set these on each node before running commands:

```bash
export APP_DIR=/opt/foxbrain-faos
export COMPOSE_FILE=docker-compose.yml
export FOXBRAIN_SYSTEM=VAFOX
export FOXBRAIN_VERSION=AI-OS-V6-CLEAN-REBUILD-V1
export DOMAINS="gateway.vafox.com ai.vafox.com core.vafox.com"
```

If a node owns only one domain, set `DOMAINS` to that single hostname.

## A. Production Discovery

Run:

```bash
cd "$APP_DIR"
bash deploy/vafox_multi_node_genesis_migration.sh discover
```

Required output:

- `migration-reports/NODE_DISCOVERY_REPORT.md`

The report records:

- IP addresses
- SSH/current user
- current directory
- Docker Compose file candidates
- Docker containers
- Docker images
- nginx configuration
- systemd services
- port usage
- current domain health entry points

## B. Legacy Detection

Run:

```bash
cd "$APP_DIR"
bash deploy/vafox_multi_node_genesis_migration.sh legacy
```

Required output:

- `migration-reports/LEGACY_DETECTION_REPORT.md`

This step records only and does not delete:

- old `portal.py` files
- old systemd services
- old `foxbrain-v4` or Dify images
- old nginx routes
- old Dify/legacy AI page markers

## C. Genesis Migration Preparation

Run:

```bash
cd "$APP_DIR"
git fetch origin main
git checkout main
git pull --ff-only origin main
bash deploy/vafox_multi_node_genesis_migration.sh prepare
```

This validates:

- latest `main` code is present
- `docker-compose.yml` renders successfully
- `vafox-genesis:AI-OS-V6-CLEAN-REBUILD-V1` can build
- Compose service definitions are available before cutover

## D. Production Cutover

Run only after reviewing discovery and legacy reports.

```bash
cd "$APP_DIR"
bash deploy/vafox_multi_node_genesis_migration.sh backup
bash deploy/vafox_multi_node_genesis_migration.sh cutover
```

The cutover helper:

1. creates a timestamped backup directory
2. records current compose, env, nginx, systemd, and container state where available
3. stops known legacy systemd units only to prevent port conflicts
4. deploys the Genesis Docker Compose stack
5. verifies `nginx -t`
6. reloads nginx

## E. Final Verification

Run:

```bash
cd "$APP_DIR"
bash deploy/vafox_multi_node_genesis_migration.sh verify
```

Required output:

- `migration-reports/PRODUCTION_NODE_MIGRATION_REPORT.md`

Required endpoint checks:

- `/health`
- `/health/runtime`
- `/api/health`

Each endpoint response must confirm:

- `version`: `AI-OS-V6-CLEAN-REBUILD-V1`
- `system`: `VAFOX`

## Rollback Capability

If verification fails:

1. Do not delete the new containers, old services, data volumes, databases, or backups.
2. Capture `docker compose ps`, `docker compose logs --tail=200`, `nginx -t`, and endpoint failures into the migration report.
3. Restore the previous nginx/compose/env files from the timestamped backup directory if needed.
4. Restart the previously active service manager path, either Docker Compose or the legacy systemd unit, based on `NODE_DISCOVERY_REPORT.md`.
5. Re-run `/health`, `/health/runtime`, and `/api/health` against the restored route.

## Node Completion Checklist

For each node, attach these artifacts to the production change record:

- `NODE_DISCOVERY_REPORT.md`
- `LEGACY_DETECTION_REPORT.md`
- backup directory path
- Docker Compose validation output
- Docker build result
- `PRODUCTION_NODE_MIGRATION_REPORT.md`
- final domain endpoint responses for `/health`, `/health/runtime`, and `/api/health`
