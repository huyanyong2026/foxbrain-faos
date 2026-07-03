# Architecture

Current implementation is intentionally conservative:

- `portal_v2.py` remains the main portal application.
- `sync_sap_b1.py` remains the SAP B1 sync script.
- SQLite stores portal users, archive records, knowledge items, uploaded file metadata, logs, timeline events, and relations.
- SAP B1 sync continues to write to PostgreSQL and generate a summary JSON consumed by the portal.

New V4 skeletons:

- Minimal dashboard
- Unified archive framework
- Document center
- Knowledge center
- AI agent center
- Workflow center
- SAP analysis API placeholders
