# Sprint016 SAP Read-Only Security Checklist

## Current Sprint016 Status

- Production SAP connection: disabled.
- Production SAP write operations: not implemented.
- SAP server installation: not required.
- Scheduler: disabled by default.
- Credentials in Git: none.
- Manual approval before publish: required.

## Required Before Real SAP Rollout

- Create an independent SAP replica, restored backup database, or export host.
- Create a dedicated read-only database account.
- Confirm the account cannot execute:
  - `INSERT`
  - `UPDATE`
  - `DELETE`
  - `MERGE`
  - DDL
  - write stored procedures
- Store credentials only in server environment variables or a secret store.
- Do not place passwords in GitHub, `.env` committed files, logs, screenshots, or issue comments.
- Test connection against the replica/export host first.
- Run read-only verification.
- Run full dry-run.
- Review validation and reconciliation results.
- Manually approve the first publish.
- Enable scheduling only after business approval.

## Data Handling Boundaries

- Phase 1 allows sales, inventory, products, brands, and stores.
- Do not copy financial journal entries in Sprint016.
- Do not copy passwords, attachments, or sensitive personal data.
- Avoid logging customer phone numbers and personal identifiers in plain text.
- Sync failure must never affect SAP business operations.

## Approval Rules

- Dry-run can be executed by authorized roles.
- Publish requires authorized manual action.
- Schedules must remain off until explicit approval.
- High-risk changes remain outside Sprint016 automation.
