#!/usr/bin/env bash
set -euo pipefail

APP_URL="${APP_URL:-http://127.0.0.1:8088}"
REPORT_DIR="${FOXBrain_REPORT_DIR:-/opt/foxbrain/reports}"
DATE_STAMP="$(date '+%F')"
REPORT="$REPORT_DIR/ai-context-refresh-$DATE_STAMP.txt"

mkdir -p "$REPORT_DIR"

{
  echo "VAFOX AI context refresh"
  echo "Started: $(date '+%F %T')"
  echo "Source: $APP_URL/api/health"
  echo
} > "$REPORT"

curl -fsS "$APP_URL/api/health" >> "$REPORT" || {
  echo
  echo "WARN: health endpoint unavailable; context refresh skipped." >> "$REPORT"
}

echo >> "$REPORT"
echo "Finished: $(date '+%F %T')" >> "$REPORT"
