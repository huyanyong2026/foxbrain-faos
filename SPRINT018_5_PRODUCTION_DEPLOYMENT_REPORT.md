# Sprint018.5 Production Deployment Report

## Deployment Target

```text
huyan.vafox.com
```

## Safety

- SAP write access: not used
- SAP production modification: not performed
- ai.vafox.com development: not performed
- credentials committed to GitHub: no

## Local Pre-Deployment Result

```text
PASS: portal_v2.py syntax check
PASS: local Copilot evidence calibration
PASS: feedback and memory draft validation
PASS: selective test cleanup validation
```

## Production Deployment

Status:

```text
DEPLOYED
```

Deployment method:

```text
GitHub fetch on server was unavailable due network/permission timeout.
Deployed by securely copying locally verified portal_v2.py to /opt/firefox-portal/portal.py.
```

Repository commit:

```text
56d9f51 Implement Sprint018.5 copilot real data calibration
```

Runtime directory:

```text
/opt/firefox-portal
```

Service:

```text
firefox-portal.service
status: active
restart time: 2026-07-11 00:26:32 CST
main pid observed: 3469580
```

Backups created:

```text
/opt/firefox-portal/portal.py.bak.sprint0185.20260711-002631
/opt/firefox-portal/portal.db.bak.sprint0185.20260711-002631
```

Compile check on server:

```text
python3 -m py_compile /opt/firefox-portal/portal.py
PASS
```

Production route status:

```text
/                              accessible, login page returned when unauthenticated
/copilot                       accessible, login page returned when unauthenticated
/api/copilot/sessions          401 login required when unauthenticated
/api/dashboard/ceo             protected endpoint, requires login
```

Production calibration:

```text
PASS
```

Notes:

```text
Production Enterprise Sync freshness currently reports no_published_sync.
This is surfaced to Copilot answers as data freshness context.
```

## Routes To Verify

- `/`
- `/copilot`
- `/api/copilot/sessions`
- `/api/dashboard/ceo`

All listed routes were checked after restart. Protected routes correctly require login.
