#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-/opt/vafox-memory-factory}"
BACKUP_DIR="${1:-}"

if [ -z "$BACKUP_DIR" ] || [ ! -d "$BACKUP_DIR" ]; then
  echo "Usage: bash rollback.sh /opt/vafox-memory-factory/backups/YYYY-MM-DD_HH-MM-SS" >&2
  exit 1
fi

cd "$APP_DIR"
"$APP_DIR/restore.sh" "$BACKUP_DIR"
"$APP_DIR/healthcheck.sh"
echo "Rollback complete: $BACKUP_DIR"
