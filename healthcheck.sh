#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-/opt/vafox-memory-factory}"
cd "$APP_DIR"

fail() { echo "ERROR: $*" >&2; exit 1; }

command -v docker >/dev/null 2>&1 || fail "Docker is not installed."
docker info >/dev/null 2>&1 || fail "Docker is not running."

for service in memory-api postgres redis minio; do
  container_id="$(docker compose ps -q "$service")"
  [ -n "$container_id" ] || fail "Service $service is not running."
  status="$(docker inspect --format='{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "$container_id")"
  echo "$service Docker status: $status"
  [ "$status" = healthy ] || fail "Service $service is not healthy."
done

curl -fsS "http://127.0.0.1:${MEMORY_API_PORT:-8080}/health" >/dev/null || fail "Memory API is not reachable."
docker compose exec -T postgres pg_isready -U "${POSTGRES_USER:-vafox}" -d "${POSTGRES_DB:-vafox_memory}" >/dev/null || fail "PostgreSQL is not ready."
docker compose exec -T redis redis-cli ping >/dev/null || fail "Redis is not ready."

echo "VAFOX Memory Factory Phase 1A healthcheck OK."
