# VAFOX Production Cutover Repair Report

## Before

- GitHub `main` contained the Genesis runtime, but production could still serve legacy UI because more than one deployment workflow could run on `main` and production metadata was not consistently injected into the running Compose containers.
- The runtime path was Docker Compose on the production host, with host Nginx routing public domains to loopback services and the in-repo Compose stack owning the application containers.
- Release verification checked some health endpoints, but it did not enforce the required `/health/runtime` metadata contract for `gateway.vafox.com`, `ai.vafox.com`, and `huyan.vafox.com` in one post-deploy gate.

## Root Cause

- Duplicate legacy deployment workflows (`deploy.yml` and `deploy-cloud.yml`) were still eligible to run from `main`, creating a race with the production deployment bridge.
- The production deployment workflow generated metadata in CI and again on the server, but Docker Compose did not pass the release commit, version, build time, and deploy time into the runtime containers.
- The production workflow used `git pull --ff-only`, which did not pin the production working tree to the exact GitHub Actions commit.
- Rollback behavior was documented but not wired into the automated production deploy step.

## Changes

- Production deployment is now the only automatic `main` deployment bridge for the Genesis runtime.
- Legacy cloud deploy workflows are manual-only and no longer auto-deploy from `main`.
- The production workflow now maps the release chain explicitly: GitHub commit -> server checkout pinned to that commit -> Docker Compose build -> image tag -> containers -> loopback Nginx service -> host Nginx public domains.
- Docker Compose injects `FOXBRAIN_VERSION`, `GIT_COMMIT`, `BUILD_TIME`, `DEPLOY_TIME`, `FOXBRAIN_ENV`, and `FOXBRAIN_SYSTEM` into web, API, and worker containers.
- A release verifier now checks `/health/runtime` for `gateway.vafox.com`, `ai.vafox.com`, and `huyan.vafox.com` and requires version, commit, build time, and running status.
- Production deployment now has rollback protection: failures after the previous commit is captured restore the previous commit and restart Compose.
- Deployment metadata now defaults to the Genesis runtime version instead of the older V4 value.

## After Verification

The automated deploy performs these checks after every `main` deployment:

1. Validate workflow shell blocks.
2. Generate deployment metadata.
3. Validate Docker Compose configuration.
4. SSH to production and pin the working tree to the GitHub Actions commit.
5. Build and start the Compose runtime with `--remove-orphans` to remove old Compose routes/containers.
6. Wait for required containers to become healthy.
7. Prune orphan containers and dangling images.
8. Verify local runtime on `127.0.0.1:8088/health/runtime`.
9. Verify public release runtime metadata on:
   - `https://gateway.vafox.com/health/runtime`
   - `https://ai.vafox.com/health/runtime`
   - `https://huyan.vafox.com/health/runtime`

## Rollback Plan

Automated rollback runs if deployment fails after the previous commit is captured:

1. Checkout the previous production commit.
2. Restart Docker Compose with `docker compose up -d --build --remove-orphans`.
3. Leave the deployment failed so GitHub Actions reports the incident.

Manual rollback remains available on the production host:

```bash
cd "$PRODUCTION_DEPLOY_PATH"
git checkout <known-good-commit>
docker compose up -d --build --remove-orphans
python scripts/verify_release_runtime.py --expected-commit <known-good-commit> --expected-version AI-OS-V6-CLEAN-REBUILD-V1
```
