#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-/opt/foxbrain-faos}"
cd "$APP_DIR"

fail() {
  echo "ERROR: $*"
  exit 1
}

command -v docker >/dev/null 2>&1 || fail "Docker is not installed. Run bash install.sh."
docker info >/dev/null 2>&1 || fail "Docker is not running. Try: sudo systemctl restart docker"

docker compose ps || fail "docker compose ps failed."

required_services="foxbrain-web foxbrain-api foxbrain-worker postgres redis minio qdrant nginx"
for service in $required_services; do
  container_id="$(docker compose ps -q "$service")"
  [ -n "$container_id" ] || fail "Service $service is not running."
  health_status="$(docker inspect --format='{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "$container_id")"
  echo "$service Docker status: $health_status"
  [ "$health_status" = "healthy" ] || fail "Service $service is not healthy."
done

ss -tlnp | awk '$4 ~ /(:80|:443)$/ {print}' || true
if ss -tlnp | awk '$4 ~ /(:80|:443)$/ {print}' | grep -q 'docker-proxy'; then
  fail "Docker is still binding public port 80 or 443. Keep only system nginx on public ports."
fi

curl -fsS http://127.0.0.1/api/health >/dev/null || curl -fsS http://127.0.0.1:3000/api/health >/dev/null || fail "VAFOX health API is not reachable. Check: docker compose logs foxbrain-web"
curl -fsS http://127.0.0.1/ >/dev/null || curl -fsS http://127.0.0.1:3000/ >/dev/null || fail "VAFOX homepage smoke test failed."

docker compose exec -T postgres pg_isready -U "${POSTGRES_USER:-foxbrain}" -d "${POSTGRES_DB:-foxbrain}" >/dev/null || fail "PostgreSQL is not ready."
docker compose exec -T redis redis-cli ping >/dev/null || fail "Redis is not ready."
curl -fsS http://127.0.0.1/minio/health/live >/dev/null || echo "WARN: MinIO public health path is not exposed through nginx. Check docker compose ps minio."

docker compose ps foxbrain-worker | grep -E "running|Up" >/dev/null || fail "VAFOX worker is not running."
if [ -f "$APP_DIR/logs/worker.log" ]; then
  echo "Recent worker logs:"
  tail -n 20 "$APP_DIR/logs/worker.log"
else
  echo "WARN: worker.log not found yet. It should appear after the worker starts."
fi

DISK_USE="$(df / | awk 'NR==2 {print $5}' | tr -d '%')"
if [ "$DISK_USE" -ge 85 ]; then
  fail "Disk usage is ${DISK_USE}%. Clean logs or expand disk."
fi

FREE_MEM_MB="$(free -m | awk '/Mem:/ {print $7}')"
if [ "$FREE_MEM_MB" -lt 300 ]; then
  fail "Available memory is below 300MB. Consider increasing server memory."
fi

echo "VAFOX healthcheck OK."
