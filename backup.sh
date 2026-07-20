#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-/opt/vafox-memory-factory}"
BACKUP_ROOT="$APP_DIR/backups"
STAMP="$(date '+%Y-%m-%d_%H-%M-%S')"
BACKUP_DIR="$BACKUP_ROOT/$STAMP"

mkdir -p "$BACKUP_DIR"
cd "$APP_DIR"

echo "Creating backup in $BACKUP_DIR"

if [ -f .env ]; then
  cp .env "$BACKUP_DIR/env.backup"
fi

docker compose exec -T postgres pg_dump -U "${POSTGRES_USER:-vafox}" "${POSTGRES_DB:-vafox_memory}" > "$BACKUP_DIR/postgres.sql" || echo "PostgreSQL backup skipped or failed."

PROJECT_NAME="${COMPOSE_PROJECT_NAME:-vafox-memory-factory}"
docker run --rm -v "${PROJECT_NAME}_minio_data:/data" -v "$BACKUP_DIR":/backup alpine tar czf /backup/minio.tar.gz -C /data . || echo "MinIO backup skipped or failed."

find "$BACKUP_ROOT" -mindepth 1 -maxdepth 1 -type d -mtime +14 -exec rm -rf {} \;

echo "Backup complete: $BACKUP_DIR"
