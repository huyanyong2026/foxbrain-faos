# Database Notes

The portal SQLite database uses backward-compatible `create table if not exists` migrations.

Core tables:

- `users`
- `records`
- `knowledge_items`
- `uploaded_files`
- `activity_log`
- `timeline_events`
- `relations`

The existing SAP B1 PostgreSQL sync is not changed by Task001.
