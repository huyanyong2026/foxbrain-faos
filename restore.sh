#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-/opt/vafox-memory-factory}"
BACKUP_DIR="${1:-}"

if [ -z "$BACKUP_DIR" ] || [ ! -d "$BACKUP_DIR" ]; then
  echo "Usage: bash restore.sh /opt/vafox-memory-factory/backups/YYYY-MM-DD_HH-mm-ss"
  exit 1
fi

cd "$APP_DIR"

echo "Restoring from $BACKUP_DIR"
docker compose down

if [ -f "$BACKUP_DIR/env.backup" ]; then
  cp "$BACKUP_DIR/env.backup" "$APP_DIR/.env"
fi

docker compose up -d postgres
sleep 10
if [ -f "$BACKUP_DIR/postgres.sql" ]; then
  cat "$BACKUP_DIR/postgres.sql" | docker compose exec -T postgres psql -U "${POSTGRES_USER:-vafox}" "${POSTGRES_DB:-vafox_memory}" || echo "PostgreSQL restore failed."
fi

if [ -f "$BACKUP_DIR/minio.tar.gz" ]; then
  PROJECT_NAME="${COMPOSE_PROJECT_NAME:-vafox-memory-factory}"
  docker run --rm -v "${PROJECT_NAME}_minio_data:/data" -v "$BACKUP_DIR":/backup alpine sh -c "rm -rf /data/* && tar xzf /backup/minio.tar.gz -C /data"
fi

docker compose up -d
docker compose ps
echo "Restore complete."
