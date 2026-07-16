# Link Health Report

Version: AI-OS-V5.1-AUTOMATION-AUDIT

PASS — Gateway → Huyan → AI → Core links are governed by canonical production domains.

| Link | Purpose | Status |
| --- | --- | --- |
| `gateway.vafox.com` → `huyan.vafox.com` | CEO command routing | PASS |
| `gateway.vafox.com` → `ai.vafox.com` | Employee AI workspace | PASS |
| `gateway.vafox.com` → `ai.vafox.com/store` | Store AI | PASS |
| `gateway.vafox.com` → `ai.vafox.com/supply` | Supply AI | PASS |
| `ai.vafox.com` → `core.vafox.com` | AI Core data access | PASS |
| `huyan.vafox.com` → `core.vafox.com` | CEO enterprise digital twin context | PASS |

Deprecated links and old routes are blocked by version governance and release guard checks.
