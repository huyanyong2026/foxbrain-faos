# FoxBrain AI OS V4 Route Status Report

Production route verification is performed by `production_activation_check.py` and the CI/CD production deploy gate.

| Route | DNS | HTTPS | Nginx | Reverse Proxy | Backend Target |
|---|---|---|---|---|---|
| `gateway.vafox.com` | Verified by script | Verified by script | Verified by script | Verified by script | `/health/version` |
| `huyan.vafox.com` | Verified by script | Verified by script | Verified by script | Verified by script | `/health/version` |
| `ai.vafox.com` | Verified by script | Verified by script | Verified by script | Verified by script | `/health/version` |
| `core.vafox.com` | Verified by script | Verified by script | Verified by script | Verified by script | `/health/version` |

Expected result values are `PASS`, `FAIL`, or `UNVERIFIED`. `UNVERIFIED` means the route could not be independently confirmed from the running environment.
