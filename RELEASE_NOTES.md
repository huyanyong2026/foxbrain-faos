# VAFOX FoxBrain V1.0.0 Release Notes

**Release date:** 2026-07-22
**Release owner:** Codex Cloud
**Promotion:** `develop` → `main`

## Highlights

- Delivers V1 frontend entrypoints for the Gateway, AI Workspace, and Huyan product surfaces.
- Uses shared UI and API client packages; frontend applications access backend capabilities through the API Gateway rather than direct data stores.
- Enables CI coverage for linting, repository structure tests, Python tests, frontend builds, Docker Compose validation, and frontend container builds.
- Provides production deployment metadata and runtime verification contracts for Gateway, Huyan, AI, and Core services.

## Release identity

| Field | Value |
| --- | --- |
| `FOXBRAIN_VERSION` | `v1.0.0` |
| Release channel | `production` |
| Deployment environment | `production` |
| Required services | `gateway`, `huyan`, `ai`, `core` |

## Upgrade and rollback

1. Merge the approved `develop` → `main` release PR after all required CI checks pass.
2. The `Production Deploy` workflow generates deployment metadata with the merge commit and `FOXBRAIN_VERSION=v1.0.0` before deployment.
3. If deployment verification fails, use the workflow's generated rollback script to restore the previous checked-out release and restart the Compose stack.

## Known release gate

Production deployment requires configured production SSH and deployment-path secrets. The workflow fails before deployment when those values are unavailable; no secret values are stored in this repository.
