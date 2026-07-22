# Release Notes

## FoxBrain V1 Sprint 4 — Architecture Freeze

- Established the `apps`, `services`, `packages`, `infrastructure`, `docs`, `tests`, and `scripts` monorepo boundaries.
- Added Next.js foundations for AI Workspace and Huyan, backed exclusively by the API Gateway.
- Added architecture validation, frontend build, Docker build, and protected deployment workflow stages.

## Release process

1. Create a `release/<version>` branch from `develop` after CI is green.
2. Update `CHANGELOG.md`, this file, and `MIGRATION.md` as applicable.
3. Obtain release approval, tag `v<version>`, and merge into `main`.
4. The protected production environment performs deployment and records validation evidence.
