# FoxBrain Enterprise OS V0.20.5 Platform Alignment Audit

## Scope

This audit aligns Core, AI, Huyan, Gateway, Docker, and GitHub Actions into one Enterprise OS release foundation before V0.21 Living Enterprise.

## Non-negotiable boundaries

- SAP B1 remains protected: this release does not modify SAP B1, finance flows, or any direct SAP write path.
- Core remains the only enterprise data understanding layer.
- AI consumes Core APIs and stores only prompts, approvals, evidence, and derived work products; it must not maintain a second business-facts database.
- Existing production data is preserved because the release changes declarative contracts, CI/release automation, and read-only health validation only.

## Unified data chain

`SAP B1 -> SAP Mirror -> Core -> Gateway/Huyan/AI`

| Platform | Responsibility | Source of truth | Health endpoint | Release unit |
| --- | --- | --- | --- | --- |
| Core | SAP Mirror + enterprise data service | Read-only SAP B1 mirror and approved enterprise datasets | `/api/v1/data-health` | `apps/core_api` + `infra/sap-mirror` |
| AI | AI capability center, workflow automation, replenishment worker | Core APIs only | `/ops-api/connections/check` | `apps/ai` |
| Huyan | CEO operating center | Core and approved AI outputs with evidence links | `/healthz` | `portal_v2.py` + Huyan nginx config |
| Gateway | Unified entry, authentication, and public status proxy | Core public APIs | `/healthz` | `apps/gateway` |

## Version alignment

- Current release: `0.20.5`
- Next release target: `0.21 Living Enterprise`
- Shared manifest source: `foxbrain_os.platform_alignment.platform_manifest()`

## Release gates

1. Unit tests pass.
2. Workflow script guard passes.
3. Security boundary tests pass.
4. Core read-only contract tests pass.
5. Production deployment health validation passes after merge.

## Auto-release model

- Pull requests run the Enterprise OS CI gate.
- Main branch merges trigger the existing production deployment workflow.
- Deployment completes only after Docker Compose services report healthy.
