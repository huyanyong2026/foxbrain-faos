# Production Secret Compatibility Report

## Purpose

The Genesis production deployment workflow now supports the production secrets already used by the legacy deployment while preserving the newer production governance checks.

## Compatibility Mapping

| Production deploy value | Preferred secret | Legacy fallback | Default |
| --- | --- | --- | --- |
| SSH host | `PRODUCTION_SSH_HOST` | `SERVER_HOST` | None; deployment fails if unresolved. |
| SSH user | `PRODUCTION_SSH_USER` | `SERVER_USER` | None; deployment fails if unresolved. |
| SSH private key | `PRODUCTION_SSH_KEY` | `SERVER_SSH_KEY` | None; deployment fails if unresolved. |
| SSH port | `PRODUCTION_SSH_PORT` | `SERVER_PORT` | `22` |
| Deploy path | `PRODUCTION_DEPLOY_PATH` | None | `/opt/foxbrain` |

## Deployment Path Protection

The workflow resolves one deployment path only: `PRODUCTION_DEPLOY_PATH`, which defaults to `/opt/foxbrain` when the new secret is absent. The remote deployment continues to `cd "$PRODUCTION_DEPLOY_PATH"` and does not create or target any duplicate production directory.

## Governance Preserved

The production workflow still runs the release commit verification, workflow script validation, release tests, release metadata generation, Docker Compose validation, production environment validation, and public runtime verification before or during deployment.

## Rollback Protection Preserved

The remote deployment still records the previously checked-out commit, installs an error trap, and restores that previous commit with `docker compose up -d --build --remove-orphans` if the deployment fails before completion.

## Runtime Verification Preserved

The workflow still waits for the required Docker Compose services to report healthy status, verifies the local runtime endpoint on the production host, and runs the public production runtime verifier after deployment.

## Validation Performed

The workflow YAML and embedded shell scripts were validated with the repository workflow script guard after applying the compatibility changes.
