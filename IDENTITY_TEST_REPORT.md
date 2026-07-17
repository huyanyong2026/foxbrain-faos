# Identity Test Report

Version: Genesis-Construction-003-1

## Scope

Tested Gateway Identity Center construction package locally at code and API level.

## Test Matrix

| Case | Result | Evidence |
| --- | --- | --- |
| Login endpoint | PASS | `/identity/login` accepts supported credentials and returns VID/session/route. |
| VID creation | PASS | VID is generated from credential type/value with server-side HMAC digest. |
| Role mapping CEO | PASS | `role_hint=ceo` routes to `https://huyan.vafox.com`. |
| Role mapping Employee | PASS | `role_hint=employee` routes to `https://ai.vafox.com`. |
| Role mapping Admin | PASS | `role_hint=admin` routes to `https://core.vafox.com`. |
| Permission | PASS | `/identity/roles` returns role-derived permissions only after token validation. |
| Routing | PASS | `/routing/resolve` returns route with `manual_system_selection=false`. |
| Session | PASS | Invalid or missing tokens return `invalid_or_expired_session`. |
| Security | PASS | No SAP/private business records are returned by identity endpoints. |
| Mobile experience | PASS | Login card and identity flow stack to one column under mobile breakpoints. |

## Local Checks

- `python -m py_compile apps/gateway/public_api.py`
- API smoke test using local `GatewayPublicHandler` server and POST/GET identity calls.
