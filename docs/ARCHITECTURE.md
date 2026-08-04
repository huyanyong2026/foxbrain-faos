# FoxBrain Architecture and Delivery Controls

## Delivery workflow architecture

The architecture freeze separates GitHub Actions by responsibility:

| Workflow | Trigger | Responsibility |
| --- | --- | --- |
| `ci.yml` | Pull requests to `main`/`develop`; pushes to `develop` | Required code-quality, test, frontend-build, Compose, and workflow-script validation. |
| `release.yml` | Tags matching `v*.*.*` | Release metadata, changelog, deployment record, and GitHub release publication. |
| `production-deploy.yml` | Pushes to `main`; manual dispatch | Protected production deployment, health verification, and rollback. |

The retired `architecture-freeze.yml`, legacy `deploy.yml`, version-specific
`v0205-release.yml`, and PR auto-merge release gate were intentionally removed
to prevent overlapping validation, deployment, and release responsibilities.

## Production boundary

Production deploys execute only in the GitHub `production` Environment. The
workflow reads deployment values from GitHub Secrets, verifies that the commit
is reachable from `main`, and uses the server-managed `.env` file without
printing it. Runtime metadata uses `FOXBRAIN_VERSION`, with `v1.0.0` as the
production baseline. Deployment failures invoke the remote rollback handler to
restore the previously checked-out commit and Docker Compose stack.

Branch protection must require the CI workflow checks before merge. Environment
protection rules must require the production approvers defined in GitHub; they
cannot be represented safely as repository files.
