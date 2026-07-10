# Sprint019.1 Production Deployment Report

## Status

Deployed to `huyan.vafox.com`.

## Runtime

- Runtime directory: `/opt/firefox-portal`
- Service: `firefox-portal.service`
- Status after restart: `active`
- Branch: `sprint019-1-usability-intelligence-polish`
- Commit: `bb5009f`

## Deployment Steps

1. Backed up `/opt/firefox-portal/portal.py`.
2. Backed up `/opt/firefox-portal/portal.db`.
3. Uploaded verified `portal_v2.py`.
4. Compiled on server.
5. Restarted `firefox-portal.service`.
6. Verified authenticated routes through HTTPS.

## Backups

- `/opt/firefox-portal/portal.py.bak.sprint0191.20260711-065922`
- `/opt/firefox-portal/portal.db.bak.sprint0191.20260711-065922`

## Route Verification

- `/`: 200, global Copilot present, compact homepage present
- `/ceo-workbench`: 200, global Copilot present
- `/copilot`: 200, global Copilot present
- `/daily-intelligence`: 200, global Copilot present
- `/decision`: 200, global Copilot present
- `/business-health`: 200, global Copilot present
- `/inventory-intelligence`: 200, global Copilot present
- `/brand-intelligence`: 200, global Copilot present
- `/store-intelligence`: 200, global Copilot present
- `/action-center`: 200, global Copilot present

## Safety

- No SAP write access.
- No SAP production modification.
- No `ai.vafox.com` deployment.
- No database deletion.
