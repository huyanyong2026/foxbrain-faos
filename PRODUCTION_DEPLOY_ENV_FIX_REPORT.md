# Production Deploy Environment Validation Fix Report

## Before

The production deployment workflow ran `docker compose config` directly on the GitHub Actions runner. The Compose file declares `.env` as an `env_file` for production services, but the runner does not have the real production `.env` file.

## Root cause

The workflow used the same Compose validation path for CI and the production server. CI validation should never require real production secrets, while the production server must continue to use its server-managed `.env` file.

## Fix

- Added an explicit production secret gate for `PRODUCTION_SSH_HOST`, `PRODUCTION_SSH_USER`, `PRODUCTION_SSH_KEY`, and `PRODUCTION_DEPLOY_PATH` with clear GitHub Actions error messages.
- Changed CI Compose validation to copy `.env.example` to a temporary `.env`, run `docker compose config`, and remove the temporary file with a shell trap.
- Kept production deployment validation on the server using the real server-managed `.env` file.
- Added a clear remote failure message when the production server `.env` file is missing, without committing or exposing `.env`.

## Verification

- Validated workflow shell script structure with `.github/scripts/check_workflow_scripts.py`.
- Validated Docker Compose locally by copying `.env.example` to a temporary `.env`, running `docker compose config`, and removing the temporary file.
- Confirmed `.env` remains untracked and was not committed.
