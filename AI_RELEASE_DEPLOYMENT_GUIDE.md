# AI Release Deployment Guide

## Purpose

This guide documents the production release deployment model for `ai.vafox.com` and provides an operator-safe path for future migration to **VAFOX AI Workforce Genesis**.

> **Production safety rule:** this document is procedural documentation only. Creating or updating this file must not change production, restart services, switch symlinks, or modify data on `ai.vafox.com`.

## Production Target

- **Domain:** `ai.vafox.com`
- **Application root:** `/opt/ai-vafox`
- **Deployment model:** immutable release directories selected by a stable symlink.
- **Not used:** git checkout deployment. Production must not depend on `git checkout`, branch state, or working-tree mutation as the active deployment mechanism.

## 1. Current Release Architecture

Production is organized around a release root, one or more immutable release directories, and a stable runtime symlink:

```text
/opt/ai-vafox
├── releases/
│   └── fba3c17/
└── current-enterprise-ai -> releases/fba3c17
```

### Components

1. **`/opt/ai-vafox/releases/`**
   - Stores versioned release directories.
   - Each release directory represents a deployable application artifact set.
   - Release directories should be treated as immutable after validation.

2. **`/opt/ai-vafox/releases/<release_id>/`**
   - Contains one complete release payload.
   - Example current release ID: `fba3c17`.
   - The release ID should map to an auditable build identifier, such as a short commit SHA, CI build ID, or signed artifact manifest ID.

3. **`/opt/ai-vafox/current-enterprise-ai`**
   - Stable symlink used by runtime processes and Docker Compose commands.
   - Points to exactly one release directory at a time.
   - Switching this symlink is the deployment cutover action.

### Operational Principle

The production host should run from `current-enterprise-ai`, not from a mutable git working tree. New versions are introduced by creating a new directory under `releases/`, validating it, then atomically repointing `current-enterprise-ai`.

## 2. Release Creation Process

Create releases as standalone deployable artifacts before production cutover.

### Recommended Release Inputs

Each release directory should include:

- Application source or compiled build output required at runtime.
- Docker Compose file and service configuration templates.
- Runtime metadata, such as release ID, build timestamp, source commit, and artifact checksum.
- Migration scripts, if any, with explicit run instructions.
- Health-check or verification scripts.
- A release manifest, for example `deployment.json` or `RELEASE_MANIFEST.json`.

### Production Host Staging Pattern

From an approved operator session on the production host, stage the new release without changing the active symlink:

```bash
export APP_ROOT=/opt/ai-vafox
export RELEASE_ID=<new_release_id>

mkdir -p "$APP_ROOT/releases/$RELEASE_ID"
# Copy or extract the approved release artifact into:
# $APP_ROOT/releases/$RELEASE_ID
```

Validation should happen while the new release is staged but inactive:

```bash
cd "$APP_ROOT/releases/$RELEASE_ID"
# Review manifests, environment references, compose configuration, and checksums.
# Run only approved read-only validation commands before cutover.
```

### Release Creation Rules

- Do not create a production release by running `git checkout` in `/opt/ai-vafox/current-enterprise-ai`.
- Do not modify files inside the currently active release directory.
- Do not place secrets directly inside release artifacts.
- Do not run destructive migrations during staging.
- Record the release ID, artifact source, checksum, operator, and validation result before cutover.

## 3. New Release Deployment Process

Deploying a new release is a controlled sequence:

1. Confirm an approved release artifact exists.
2. Confirm current production health.
3. Run backup integration steps described in this guide.
4. Stage the new release under `/opt/ai-vafox/releases/<release_id>`.
5. Validate staged release files and Docker Compose configuration.
6. Switch `current-enterprise-ai` to the new release.
7. Restart Docker services from the symlink path.
8. Verify health checks, logs, and externally visible behavior.
9. Record deployment evidence.

### Pre-Deployment Checks

```bash
export APP_ROOT=/opt/ai-vafox
readlink -f "$APP_ROOT/current-enterprise-ai"
cd "$APP_ROOT/current-enterprise-ai"
docker compose ps
```

If production is unhealthy before deployment, stop and escalate. Do not combine incident recovery with a release cutover unless explicitly approved.

### Staged Release Validation

```bash
export APP_ROOT=/opt/ai-vafox
export RELEASE_ID=<new_release_id>

cd "$APP_ROOT/releases/$RELEASE_ID"
docker compose config
```

Review the resolved configuration for image tags, volume mounts, environment references, network names, and service commands before switching traffic.

## 4. `current-enterprise-ai` Symlink Switch

The symlink switch is the production cutover step. It should be short, explicit, and auditable.

### Current State Example

```text
/opt/ai-vafox/current-enterprise-ai -> releases/fba3c17
```

### Switch Procedure

Use a temporary symlink and atomic rename so operators do not leave a partially updated symlink:

```bash
export APP_ROOT=/opt/ai-vafox
export RELEASE_ID=<new_release_id>

cd "$APP_ROOT"
ln -sfn "releases/$RELEASE_ID" current-enterprise-ai.next
mv -Tf current-enterprise-ai.next current-enterprise-ai
readlink -f current-enterprise-ai
```

### Symlink Rules

- The symlink should point to a directory under `/opt/ai-vafox/releases/`.
- Do not point the symlink at a developer checkout, temporary upload directory, or incomplete artifact.
- Capture `readlink -f /opt/ai-vafox/current-enterprise-ai` before and after the switch.
- Keep at least the previous known-good release directory until rollback is no longer required.

## 5. Docker Restart Process

Docker should be controlled from the symlink path so the active release and runtime commands stay aligned.

### Restart After Symlink Switch

```bash
export APP_ROOT=/opt/ai-vafox
cd "$APP_ROOT/current-enterprise-ai"

docker compose config
docker compose up -d --remove-orphans
docker compose ps
```

### Post-Restart Verification

Run approved health checks after containers are recreated or restarted:

```bash
cd /opt/ai-vafox/current-enterprise-ai
docker compose ps
docker compose logs --tail=100
```

If the application exposes HTTP health endpoints, verify them from an approved network location:

```bash
curl -fsS https://ai.vafox.com/health
```

Use the production-specific health path if it differs from `/health`.

## 6. Rollback Procedure

Rollback uses the same symlink mechanism as deployment. The goal is to repoint `current-enterprise-ai` to the previous known-good release and restart Docker from that path.

### Rollback Triggers

Initiate rollback if any of these occur after deployment:

- Critical service fails to start.
- Health endpoint fails repeatedly.
- User-facing production behavior is materially broken.
- Logs show startup loops, migration failure, or unrecoverable configuration errors.
- External dependency integration fails in a way that blocks core production use.

### Rollback Steps

```bash
export APP_ROOT=/opt/ai-vafox
export PREVIOUS_RELEASE_ID=<previous_release_id>

cd "$APP_ROOT"
ln -sfn "releases/$PREVIOUS_RELEASE_ID" current-enterprise-ai.rollback
mv -Tf current-enterprise-ai.rollback current-enterprise-ai
readlink -f current-enterprise-ai

cd "$APP_ROOT/current-enterprise-ai"
docker compose up -d --remove-orphans
docker compose ps
docker compose logs --tail=100
```

### Rollback Evidence

Record:

- Failed release ID.
- Previous release ID restored.
- Start and end timestamps.
- Reason for rollback.
- Docker service state after rollback.
- Health-check results after rollback.
- Any data migrations that were run and whether they require separate remediation.

### Rollback Constraints

- Rollback is safest when database schema and persistent data remain backward compatible.
- If a release includes irreversible data migrations, the deployment plan must include a separate data rollback or remediation decision before cutover.
- Do not delete the failed release directory until investigation and evidence collection are complete.

## 7. Backup Integration

Backups are required before high-impact production cutovers and before migration work toward **VAFOX AI Workforce Genesis**.

### Backup Timing

Run backup collection before switching `current-enterprise-ai` when any release includes:

- Database schema changes.
- Persistent data format changes.
- Docker volume changes.
- Object storage changes.
- n8n workflow or credential changes.
- WeCom integration changes.
- Infrastructure configuration changes.

### Backup Location

The established backup parent is:

```text
/opt/ai-vafox/backups
```

Backups should be timestamped and tied to the deployment or migration event:

```text
/opt/ai-vafox/backups/pre-release-<release_id>-YYYYMMDDTHHMMSSZ/
```

### Backup Process Reference

Use the production backup workflow documented in `AI_BACKUP_EXECUTION_SCRIPT.md`. That workflow is designed for pre-Genesis evidence collection and defaults to `/opt/ai-vafox/backups`.

Recommended sequence:

```bash
export APP_ROOT=/opt/ai-vafox
export BACKUP_PARENT=/opt/ai-vafox/backups

# First validate behavior without collecting production backup data.
scripts/ai_production_backup.sh --dry-run

# Then run the approved backup during the approved window.
scripts/ai_production_backup.sh
```

### Backup Evidence Required Before Cutover

Confirm the backup run produced:

- Backup root path.
- `AI_BACKUP_REPORT.md`.
- SHA256 checksums.
- PostgreSQL dump evidence, if PostgreSQL is in scope.
- Docker Compose and container state evidence.
- Object storage inventory, if MinIO is in scope.
- n8n export evidence, if n8n is in scope.
- WeCom redacted configuration inventory, if WeCom is in scope.

### Genesis Migration Alignment

For the future migration to **VAFOX AI Workforce Genesis**, every release event should preserve enough evidence to reconstruct:

1. Which release was active before migration.
2. Which release was staged for Genesis migration.
3. Which containers, images, volumes, and environment references were active.
4. Which data backups correspond to the migration window.
5. Which rollback release was available at the time of cutover.

## Operator Checklist

Use this checklist for each production release:

- [ ] Release artifact created outside production git checkout deployment.
- [ ] Release staged under `/opt/ai-vafox/releases/<release_id>`.
- [ ] Existing symlink target recorded.
- [ ] Production health checked before deployment.
- [ ] Required backup completed and checksums generated.
- [ ] Staged Docker Compose configuration reviewed.
- [ ] `current-enterprise-ai` symlink switched atomically.
- [ ] Docker services restarted from `/opt/ai-vafox/current-enterprise-ai`.
- [ ] Health checks and logs verified.
- [ ] Rollback release retained.
- [ ] Deployment evidence recorded for Genesis migration traceability.
