# VAFOX Backup And Restore

Use:

```bash
bash backup.sh
bash restore.sh /opt/vafox-memory-factory/backups/BACKUP_DIR
bash rollback.sh /opt/vafox-memory-factory/backups/BACKUP_DIR
```

Phase 1A backups cover PostgreSQL, MinIO objects, and `.env`. `rollback.sh` restores a selected backup and then runs the Phase 1A health check.
Do not commit backup files to GitHub.
