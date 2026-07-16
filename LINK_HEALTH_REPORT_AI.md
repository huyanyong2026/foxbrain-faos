# AI Link Health Report

## Scope

Audit path: `gateway.vafox.com → ai.vafox.com → core.vafox.com`.

## Link Health

| Link | Status | Verification |
| --- | --- | --- |
| Gateway to AI | PASS | Gateway keeps ai.vafox.com as the employee AI workspace destination. |
| AI Router | PASS | Workspace form posts natural-language questions to AI Router V5. |
| AI to Core | PASS | Runs use automatic `core.vafox.com` evidence links with read-only Core access. |
| Authentication | PASS | Existing login, CSRF, role, RBAC and ABAC decorators remain in force. |
| Permission | PASS | `authorize_ai_context` runs before each V5 workspace run is stored. |

## Generated Report

`LINK_HEALTH_REPORT_AI.md` mirrors this audit for deployment handoff.
