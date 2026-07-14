#!/usr/bin/env bash
set -euo pipefail

BASE="${FOXBrain_SAP_BASE:-/opt/foxbrain/sap_sync}"
REPORT_DIR="${FOXBrain_REPORT_DIR:-/opt/foxbrain/reports}"
DATE_STAMP="$(date '+%F')"
LOG_DIR="$BASE/logs"
INCOMING="$BASE/incoming"
PROCESSED="$BASE/processed"
ERROR_DIR="$BASE/error"
REPORT="$REPORT_DIR/sap-sync-report-$DATE_STAMP.txt"

mkdir -p "$INCOMING" "$PROCESSED" "$ERROR_DIR" "$LOG_DIR" "$REPORT_DIR"

{
  echo "VAFOX SAP nightly sync"
  echo "Started: $(date '+%F %T')"
  echo "Mode: file_sync_placeholder"
  echo "Policy: read_only_snapshot"
  echo
} > "$REPORT"

shopt -s nullglob
files=("$INCOMING"/*.csv "$INCOMING"/*.xlsx "$INCOMING"/*.xls)

if [ "${#files[@]}" -eq 0 ]; then
  echo "No SAP export files found in $INCOMING." | tee -a "$REPORT"
  echo "Finished: $(date '+%F %T')" >> "$REPORT"
  exit 0
fi

for file in "${files[@]}"; do
  name="$(basename "$file")"
  target="$PROCESSED/${DATE_STAMP}_$name"
  echo "Processing $name" | tee -a "$REPORT"
  if cp "$file" "$target"; then
    mv "$file" "$target.source"
    echo "Processed: $target" | tee -a "$REPORT"
  else
    mv "$file" "$ERROR_DIR/${DATE_STAMP}_$name" || true
    echo "Failed: $name" | tee -a "$REPORT"
  fi
done

echo "Finished: $(date '+%F %T')" >> "$REPORT"
