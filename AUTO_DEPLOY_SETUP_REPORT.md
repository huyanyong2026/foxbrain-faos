# FoxBrain FAOS Automatic Production Deployment Setup Report

## Summary

GitHub Actions automatic production deployment has been configured for the `huyanyong2026/foxbrain-faos` repository.

The workflow deploys FoxBrain FAOS to production after every push to the `main` branch, which covers the normal post-merge deployment flow for pull requests merged into `main`.

## Workflow File

- `.github/workflows/production-deploy.yml`

## Trigger

The production deployment workflow runs on:

- `push` events to the `main` branch

## Production Server

- Host: `140.143.207.194`
- Application: FoxBrain FAOS

## Deployment Process

The workflow performs the following steps:

1. Checks out the repository in GitHub Actions.
2. Creates an SSH configuration on the GitHub Actions runner.
3. Connects to the production server over SSH.
4. Changes into the configured production deployment directory.
5. Fetches and checks out `main`.
6. Runs `git pull --ff-only origin main`.
7. Runs `docker compose up -d --build`.
8. Runs `docker compose ps` after deployment.
9. Verifies that these required services are healthy:
   - `foxbrain-web`
   - `foxbrain-api`
   - `foxbrain-worker`

## Required GitHub Actions Secrets

Configure these secrets in the GitHub repository before enabling production deployment:

| Secret | Purpose |
| --- | --- |
| `PRODUCTION_SSH_USER` | SSH username used to connect to `140.143.207.194`. |
| `PRODUCTION_SSH_KEY` | Private SSH key with access to the production server. |
| `PRODUCTION_DEPLOY_PATH` | Absolute path to the checked-out `huyanyong2026/foxbrain-faos` repository on the production server. |

## Server Requirements

The production server must already have:

- The repository cloned at `PRODUCTION_DEPLOY_PATH`.
- The configured SSH user authorized to access the repository directory.
- Git installed.
- Docker and Docker Compose v2 installed.
- Required production environment files, such as `.env`, already present on the server.
- The deployment SSH key authorized in the server user's `~/.ssh/authorized_keys`.

## Health Check Behavior

After `docker compose up -d --build`, the workflow runs `docker compose ps` and then checks Docker health status for:

- `foxbrain-web`
- `foxbrain-api`
- `foxbrain-worker`

The workflow waits up to 20 attempts with 15 seconds between attempts. If any required service does not reach `healthy`, the deployment job fails and prints final `docker compose ps` output.

## Application Code Impact

No application code was changed. The update only adds GitHub Actions deployment automation and this setup report.
