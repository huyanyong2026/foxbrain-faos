# FoxBrain Architecture Freeze

## Monorepo boundaries

| Boundary | Responsibility |
| --- | --- |
| `apps/` | Web experiences; only call the API Gateway. |
| `services/` | Identity, runtime, knowledge, product intelligence, customer/retail brain, and core data bounded contexts. |
| `packages/` | Shared design system, API client, and types. |
| `infrastructure/` | Docker, edge proxy, Kubernetes, and monitoring configuration. |
| `docs/` | Architecture, API, deployment, and governance records. |

## Frontend data boundary

`ai-web` and `huyan-web` use `NEXT_PUBLIC_API_BASE_URL` through `@foxbrain/api-client`. It is intentionally the only client data transport. Direct database access is prohibited in frontend code.

## Branch strategy

- `main`: production, protected, and release-tagged only.
- `develop`: integration branch.
- `feature/<work-item>`: short-lived feature branches merged by pull request.
- `release/<version>`: stabilization and release-note preparation.
- `hotfix/<work-item>`: production fixes branched from `main`, then back-merged to `develop`.
