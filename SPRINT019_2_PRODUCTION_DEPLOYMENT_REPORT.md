# Sprint019.2 Production Deployment Report

## Deployment target

- Domain: `https://huyan.vafox.com`
- Server directory: `/opt/firefox-portal`
- Service: `firefox-portal.service`

## Deployment method

Server GitHub access can be unreliable, so the verified local file was uploaded directly:

1. Backed up production code, database, and uploads.
2. Uploaded `portal_v2.py` to `/tmp/portal_sprint0192.py`.
3. Copied it to `/opt/firefox-portal/portal.py`.
4. Ran server-side Python compile.
5. Restarted `firefox-portal.service`.
6. Verified service active.

## Backup artifacts

- `/opt/firefox-portal/portal.py.bak.sprint0192.20260711-101906`
- `/opt/firefox-portal/portal.db.bak.sprint0192.20260711-101906`
- `/opt/firefox-portal/uploads.bak.sprint0192.20260711-101906.tgz`
- `/opt/firefox-portal/uploads.inventory.sprint0192.20260711-101906`

## Service result

- `firefox-portal.service`: active after restart.
- Production compile: passed.

## Route verification

- `/drive`: 200
- `/drive/recent`: 200
- `/drive/starred`: 200
- `/drive/trash`: 200
- `/drive/search`: 200
- `/api/drive/files`: 200

## Database verification

- Drive tables present: 12 / 12.
- Existing documents: 12.
- Version records: 12.
- Root Drive folder: created.

## Rollback

Rollback can restore:

```bash
sudo cp /opt/firefox-portal/portal.py.bak.sprint0192.20260711-101906 /opt/firefox-portal/portal.py
sudo cp /opt/firefox-portal/portal.db.bak.sprint0192.20260711-101906 /opt/firefox-portal/portal.db
sudo systemctl restart firefox-portal.service
```

