# VAFOX Foundation V2.0 Deployment

## CI/CD Flow

```text
Codex Cloud -> GitHub -> Automated Test -> Build -> Deploy -> Health Check -> Release
```

## Pre-Deployment Gates

1. Backup current production data and deployment artifacts.
2. Verify in a test environment.
3. Run automated tests.
4. Run service health checks.
5. Confirm rollback plan and previous artifact availability.

## Deployment Order

1. Core read-only API and governance contracts.
2. Gateway routing, token, permission, and health checks.
3. AI Digital Workforce foundation.
4. Huyan CEO OS foundation.
5. End-to-end health verification.

## Production Safety

Do not deploy if any required health check fails. Do not modify SAP business logic as part of this foundation release.
