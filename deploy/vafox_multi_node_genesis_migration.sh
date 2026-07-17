#!/usr/bin/env bash
set -euo pipefail

# VAFOX Production Multi-Node Genesis Migration helper.
# Safe by default: discovery and legacy detection only record state; no database,
# volume, or backup deletion is performed by any action in this script.

TARGET_VERSION="${FOXBRAIN_VERSION:-AI-OS-V6-CLEAN-REBUILD-V1}"
TARGET_SYSTEM="${FOXBRAIN_SYSTEM:-VAFOX}"
APP_DIR="${APP_DIR:-/opt/foxbrain-faos}"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.yml}"
REPORT_DIR="${REPORT_DIR:-$APP_DIR/migration-reports}"
BACKUP_DIR="${BACKUP_DIR:-$APP_DIR/backups/$(date -u +%Y%m%dT%H%M%SZ)}"
DOMAINS="${DOMAINS:-gateway.vafox.com ai.vafox.com core.vafox.com}"

mkdir -p "$REPORT_DIR"

section() {
  printf '\n## %s\n\n' "$1"
}

run_capture() {
  local title="$1"
  shift
  printf '### %s\n\n```\n' "$title"
  if "$@"; then
    true
  else
    printf '\n[command exited non-zero: %s]\n' "$*"
  fi
  printf '```\n\n'
}


assert_health_identity() {
  local url="$1"
  local body
  body="$(curl -kfsS --max-time 8 "$url" 2>/dev/null || true)"
  printf '### Identity assertion: %s\n\n' "$url"
  if printf '%s' "$body" | grep -q "$TARGET_VERSION" && printf '%s' "$body" | grep -q "$TARGET_SYSTEM"; then
    printf '- Result: PASS\n'
  else
    printf '- Result: REVIEW_REQUIRED\n'
  fi
  printf '- Required version: `%s`\n' "$TARGET_VERSION"
  printf '- Required system: `%s`\n' "$TARGET_SYSTEM"
  printf '- Response excerpt:\n\n```\n%s\n```\n\n' "$(printf '%s' "$body" | head -c 2000)"
}

write_discovery_report() {
  local report="$REPORT_DIR/NODE_DISCOVERY_REPORT.md"
  {
    printf '# VAFOX Node Discovery Report\n\n'
    printf '- Generated UTC: `%s`\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    printf '- Hostname: `%s`\n' "$(hostname -f 2>/dev/null || hostname)"
    printf '- Current user: `%s`\n' "$(id -un)"
    printf '- Current directory: `%s`\n' "$(pwd)"
    printf '- Target app directory: `%s`\n' "$APP_DIR"
    printf '- Compose file: `%s`\n' "$APP_DIR/$COMPOSE_FILE"
    printf '- Target image tag: `vafox-genesis:%s`\n' "$TARGET_VERSION"

    section 'IP Addresses'
    run_capture 'hostname -I' hostname -I
    run_capture 'ip addr' ip addr

    section 'Docker Compose Files'
    run_capture 'compose file candidates' bash -c "find /opt /srv /var/www \$HOME -maxdepth 4 \( -name docker-compose.yml -o -name docker-compose.yaml -o -name 'compose*.yml' \) 2>/dev/null | sort"

    section 'Docker Containers'
    run_capture 'docker ps -a' docker ps -a --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}'

    section 'Docker Images'
    run_capture 'docker images' docker images --format 'table {{.Repository}}\t{{.Tag}}\t{{.ID}}\t{{.CreatedSince}}\t{{.Size}}'

    section 'nginx Configuration'
    run_capture 'nginx -T' bash -c 'nginx -T 2>&1 | sed -n "1,260p"'

    section 'systemd Services'
    run_capture 'foxbrain/vafox systemd units' bash -c "systemctl list-units --type=service --all | egrep -i 'foxbrain|vafox|portal|dify|nginx|docker' || true"

    section 'Port Usage'
    run_capture 'ss -tulpen' ss -tulpen

    section 'Current Access Entry Points'
    for domain in $DOMAINS; do
      run_capture "curl https://$domain/health" curl -kfsS --max-time 8 "https://$domain/health"
      run_capture "curl https://$domain/api/health" curl -kfsS --max-time 8 "https://$domain/api/health"
    done
  } > "$report"
  echo "$report"
}

write_legacy_report() {
  local report="$REPORT_DIR/LEGACY_DETECTION_REPORT.md"
  {
    printf '# VAFOX Legacy Detection Report\n\n'
    printf '- Generated UTC: `%s`\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    printf '- Policy: record only; do not delete legacy services, images, routes, databases, volumes, or backups.\n'

    section 'Legacy portal.py Files'
    run_capture 'portal.py candidates' bash -c "find /opt /srv /var/www \$HOME -maxdepth 5 -name portal.py 2>/dev/null | sort"

    section 'Legacy systemd Services'
    run_capture 'legacy service candidates' bash -c "systemctl list-unit-files | egrep -i 'foxbrain|vafox|portal|dify|v4' || true"

    section 'Legacy foxbrain-v4 Images'
    run_capture 'legacy docker images' bash -c "docker images --format '{{.Repository}}:{{.Tag}} {{.ID}} {{.CreatedSince}}' | egrep -i 'foxbrain.*v4|v4|dify' || true"

    section 'Legacy nginx Routes'
    run_capture 'legacy nginx route candidates' bash -c "nginx -T 2>&1 | egrep -in 'portal.py|foxbrain-v4|dify|old|legacy|proxy_pass' || true"

    section 'Legacy AI/Dify Pages'
    for domain in $DOMAINS; do
      run_capture "probe $domain for Dify/legacy markers" bash -c "curl -kfsSL --max-time 8 https://$domain/ 2>/dev/null | egrep -i 'dify|foxbrain v4|legacy|old ai' || true"
    done
  } > "$report"
  echo "$report"
}

prepare_genesis() {
  cd "$APP_DIR"
  git fetch origin main
  git status --short
  git rev-parse HEAD
  docker compose -f "$COMPOSE_FILE" config >/tmp/vafox-compose-config.yml
  docker build -t "vafox-genesis:$TARGET_VERSION" .
  docker compose -f "$COMPOSE_FILE" config --services
}

backup_current_config() {
  mkdir -p "$BACKUP_DIR"
  cd "$APP_DIR"
  cp -a "$COMPOSE_FILE" "$BACKUP_DIR/" 2>/dev/null || true
  cp -a .env "$BACKUP_DIR/" 2>/dev/null || true
  nginx -T > "$BACKUP_DIR/nginx.full.conf" 2>&1 || true
  systemctl list-units --type=service --all > "$BACKUP_DIR/systemd-services.txt" || true
  docker ps -a --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}' > "$BACKUP_DIR/docker-ps.txt" || true
  echo "$BACKUP_DIR"
}

cutover() {
  cd "$APP_DIR"
  backup_current_config
  systemctl stop foxbrain-core-api firefox-gateway-data firefox-explorer-identity 2>/dev/null || true
  docker compose -f "$COMPOSE_FILE" up -d --build
  docker compose -f "$COMPOSE_FILE" ps
  nginx -t
  systemctl reload nginx
}

write_final_report() {
  local report="$REPORT_DIR/PRODUCTION_NODE_MIGRATION_REPORT.md"
  {
    printf '# VAFOX Production Node Migration Report\n\n'
    printf '- Generated UTC: `%s`\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    printf '- Target system: `%s`\n' "$TARGET_SYSTEM"
    printf '- Target version: `%s`\n' "$TARGET_VERSION"
    printf '- App directory: `%s`\n' "$APP_DIR"
    printf '- Backup directory: `%s`\n' "$BACKUP_DIR"

    section 'Container Health'
    run_capture 'docker compose ps' bash -c "cd '$APP_DIR' && docker compose -f '$COMPOSE_FILE' ps"

    section 'Local Health Endpoints'
    run_capture '/health' curl -fsS --max-time 8 http://127.0.0.1/health
    run_capture '/health/runtime' curl -fsS --max-time 8 http://127.0.0.1/health/runtime
    run_capture '/api/health' curl -fsS --max-time 8 http://127.0.0.1/api/health

    section 'Domain Health Endpoints'
    for domain in $DOMAINS; do
      run_capture "https://$domain/health" curl -kfsS --max-time 8 "https://$domain/health"
      run_capture "https://$domain/health/runtime" curl -kfsS --max-time 8 "https://$domain/health/runtime"
      run_capture "https://$domain/api/health" curl -kfsS --max-time 8 "https://$domain/api/health"
    done

    section 'Version Assertions'
    assert_health_identity 'http://127.0.0.1/health'
    assert_health_identity 'http://127.0.0.1/health/runtime'
    assert_health_identity 'http://127.0.0.1/api/health'
    for domain in $DOMAINS; do
      assert_health_identity "https://$domain/health"
      assert_health_identity "https://$domain/health/runtime"
      assert_health_identity "https://$domain/api/health"
    done

  } > "$report"
  echo "$report"
}

usage() {
  cat <<USAGE
Usage: $0 <discover|legacy|prepare|backup|cutover|verify|all-audit>

Environment overrides:
  APP_DIR=/opt/foxbrain-faos
  COMPOSE_FILE=docker-compose.yml
  REPORT_DIR=\$APP_DIR/migration-reports
  DOMAINS="gateway.vafox.com ai.vafox.com core.vafox.com"
  FOXBRAIN_VERSION=AI-OS-V6-CLEAN-REBUILD-V1
USAGE
}

case "${1:-}" in
  discover) write_discovery_report ;;
  legacy) write_legacy_report ;;
  prepare) prepare_genesis ;;
  backup) backup_current_config ;;
  cutover) cutover ;;
  verify) write_final_report ;;
  all-audit) write_discovery_report && write_legacy_report ;;
  *) usage; exit 2 ;;
esac
