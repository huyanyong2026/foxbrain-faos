# Sprint016 Real Environment Rollout Guide

## Goal

Move from local Sprint016 fixtures to a production-safe SAP copy pipeline without touching the SAP production server.

## Recommended Architecture

```text
SAP Production
  -> read-only backup / replica / scheduled export
  -> FoxBrain Enterprise Sync Engine
  -> staging
  -> validation
  -> reconciliation
  -> manual approval
  -> Data Lake
  -> CEO Dashboard
```

## Rollout Steps

1. Prepare a replica database or safe export folder outside SAP production.
2. Create a read-only credential for the replica/export source.
3. Configure only environment-variable references on the FoxBrain server.
4. Keep `sap_b1_sql_readonly` disabled unless explicitly approved.
5. Open `/sync-center`.
6. Run connection test.
7. Run read-only verification.
8. Run full dry-run.
9. Review staging rows, validation, and reconciliation.
10. Manually publish the approved run.
11. Confirm Data Lake and CEO dashboard freshness.
12. Keep schedules disabled until the first several manual runs are stable.

## Deployment Notes

After the PR is merged:

```bash
git checkout main
git pull origin main
python3 -m py_compile portal.py
sudo systemctl restart firefox-portal.service
```

If the production deployment copies `portal_v2.py` to `/opt/firefox-portal/portal.py`, use the existing deployment process and restart the current service afterward.

## Rollback

If a sync run fails:

- Do not publish failed runs.
- Check `/api/sync/runs` and `/api/sync/reconciliation`.
- Use retry after the source/export problem is fixed.
- Discard bad runs when needed.
- Because publishing is manual, failed staging does not alter existing business data.

## Scheduler Policy

Sprint016 creates manual-only jobs. Do not enable automatic schedules until:

- Read-only verification is complete.
- Reconciliation has been reviewed.
- At least one manual publish has succeeded.
- Owner approval is recorded.
