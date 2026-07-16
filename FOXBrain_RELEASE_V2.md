# VAFOX Foundation V2.0 Release Plan

## Branch

`feature/foundation-v2`

## Acceptance Matrix

| Area | Required PASS Items |
| --- | --- |
| Gateway | Authentication, Routing, Permission |
| Huyan | CEO Dashboard, Risk Radar, Daily Briefing |
| AI | Agent Registry, Workspace, Knowledge, Memory |
| Core | Master Data, Event Engine, Business API |
| Security | RBAC, ABAC, audit, SAP write protection |
| CI/CD | Automated test, build, deploy, health check |
| Rollback | Backup, previous artifact, health verification |

## Rollback Plan

1. Stop rollout if health verification fails.
2. Redeploy previous known-good artifact.
3. Restore backup only if a data migration changed state.
4. Re-run Gateway, Huyan, AI, Core, and SAP mirror checks.
5. Document incident, cause, and follow-up actions.

## Next Phase Readiness

This foundation prepares for AI Supply Chain Center, CEO Command Center, Enterprise WeCom AI, and Store Intelligence.
