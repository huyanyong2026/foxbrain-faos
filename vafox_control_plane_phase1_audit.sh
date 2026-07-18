#!/usr/bin/env bash
set -Eeuo pipefail

# VAFOX Control Plane Phase 1 bootstrap audit for ai.vafox.com (1.13.254.217).
# Read-only audit: no install, no Docker restart, no Nginx change, no database change,
# no production release, and no current-enterprise-ai modification.

TARGET_DOMAIN="${TARGET_DOMAIN:-ai.vafox.com}"
TARGET_IP="${TARGET_IP:-1.13.254.217}"
CONTROL_PLANE_DIR="${CONTROL_PLANE_DIR:-/opt/vafox-control}"
PROD_ROOT="${PROD_ROOT:-/opt/ai-vafox}"
CURRENT_AI_LINK="${CURRENT_AI_LINK:-${PROD_ROOT}/current-enterprise-ai}"
REPORT_PATH="${REPORT_PATH:-VAFOX_CONTROL_PLANE_PHASE1_REPORT.md}"
MIN_FREE_GB="${MIN_FREE_GB:-10}"
MIN_AVAILABLE_MEM_MB="${MIN_AVAILABLE_MEM_MB:-1024}"
MIN_AVAILABLE_CPU="${MIN_AVAILABLE_CPU:-1}"

usage() {
  cat <<USAGE
VAFOX Control Plane Phase 1 bootstrap audit

Usage:
  bash vafox_control_plane_phase1_audit.sh [--help]

This script only reads host/runtime state and writes ${REPORT_PATH}.
It does not install packages, create ${CONTROL_PLANE_DIR}, restart Docker,
change Nginx, modify databases, create releases, or change current-enterprise-ai.

Environment overrides:
  TARGET_DOMAIN=${TARGET_DOMAIN}
  TARGET_IP=${TARGET_IP}
  CONTROL_PLANE_DIR=${CONTROL_PLANE_DIR}
  PROD_ROOT=${PROD_ROOT}
  REPORT_PATH=${REPORT_PATH}
  MIN_FREE_GB=${MIN_FREE_GB}
  MIN_AVAILABLE_MEM_MB=${MIN_AVAILABLE_MEM_MB}
  MIN_AVAILABLE_CPU=${MIN_AVAILABLE_CPU}
USAGE
}

if [ "${1:-}" = "--help" ] || [ "${1:-}" = "-h" ]; then
  usage
  exit 0
fi

command_exists() { command -v "$1" >/dev/null 2>&1; }
trim() { sed 's/[[:space:]]\+$//' <<<"$*"; }

safe_capture() {
  local cmd="$1"
  set +e
  local output
  output="$(bash -c "$cmd" 2>&1)"
  local code=$?
  set -e
  if [ "${code}" -eq 0 ]; then
    printf '%s' "${output}"
  else
    printf 'unavailable (exit %s): %s' "${code}" "${output}"
  fi
}

bytes_to_gb() {
  awk -v bytes="${1:-0}" 'BEGIN { printf "%.1f", bytes / 1024 / 1024 / 1024 }'
}

collect_scalar_facts() {
  HOSTNAME_VALUE="$(hostname 2>/dev/null || printf 'unknown')"
  KERNEL_VALUE="$(uname -srmo 2>/dev/null || printf 'unknown')"
  AUDIT_TIME_UTC="$(date -u +'%Y-%m-%dT%H:%M:%SZ')"
  CPU_COUNT="$(getconf _NPROCESSORS_ONLN 2>/dev/null || nproc 2>/dev/null || printf '0')"
  LOAD_AVG="$(awk '{print $1" "$2" "$3}' /proc/loadavg 2>/dev/null || printf 'unknown')"
  MEM_TOTAL_MB="$(awk '/MemTotal:/ {printf "%d", $2/1024}' /proc/meminfo 2>/dev/null || printf '0')"
  MEM_AVAILABLE_MB="$(awk '/MemAvailable:/ {printf "%d", $2/1024}' /proc/meminfo 2>/dev/null || printf '0')"

  local df_line
  df_line="$(df -PB1 /opt 2>/dev/null | awk 'NR==2 {print $2" "$4" "$5" "$6}' || true)"
  if [ -z "${df_line}" ]; then
    df_line="$(df -PB1 / 2>/dev/null | awk 'NR==2 {print $2" "$4" "$5" "$6}' || true)"
  fi
  DISK_TOTAL_BYTES="$(awk '{print $1}' <<<"${df_line:-0 0 unknown unknown}")"
  DISK_AVAILABLE_BYTES="$(awk '{print $2}' <<<"${df_line:-0 0 unknown unknown}")"
  DISK_USED_PCT="$(awk '{print $3}' <<<"${df_line:-0 0 unknown unknown}")"
  DISK_MOUNT="$(awk '{print $4}' <<<"${df_line:-0 0 unknown unknown}")"
  DISK_AVAILABLE_GB="$(bytes_to_gb "${DISK_AVAILABLE_BYTES}")"

  DOCKER_CLI="missing"
  DOCKER_DAEMON="unknown"
  DOCKER_RUNNING_COUNT="0"
  DOCKER_NAMES=""
  if command_exists docker; then
    DOCKER_CLI="present"
    if docker info >/dev/null 2>&1; then
      DOCKER_DAEMON="reachable"
      DOCKER_RUNNING_COUNT="$(docker ps -q 2>/dev/null | wc -l | awk '{print $1}')"
      DOCKER_NAMES="$(docker ps --format '{{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}' 2>/dev/null || true)"
    else
      DOCKER_DAEMON="not reachable"
    fi
  fi

  CURRENT_AI_TARGET="not present"
  if [ -L "${CURRENT_AI_LINK}" ]; then
    CURRENT_AI_TARGET="$(readlink -f "${CURRENT_AI_LINK}" 2>/dev/null || readlink "${CURRENT_AI_LINK}" 2>/dev/null || printf 'unreadable')"
  elif [ -e "${CURRENT_AI_LINK}" ]; then
    CURRENT_AI_TARGET="exists but is not a symlink"
  fi

  CONTROL_DIR_STATE="absent"
  if [ -e "${CONTROL_PLANE_DIR}" ]; then
    CONTROL_DIR_STATE="present"
  fi

  LISTENING_PORTS="$(safe_capture "ss -ltnp 2>/dev/null || netstat -ltnp 2>/dev/null || true")"
  AI_PROCESS_HINTS="$(safe_capture "ps -eo pid,ppid,comm,args --sort=comm | rg -i 'ai-vafox|current-enterprise-ai|vafox|node|python|uvicorn|gunicorn|docker|nginx' | rg -v 'vafox_control_plane_phase1_audit|VAFOX_CONTROL_PLANE_PHASE1_REPORT|rg -i ai-vafox' | head -n 80 || true")"
}

assess_readiness() {
  RISKS=()
  NEXT_STEPS=()
  SUITABLE="YES"

  if [ "${CPU_COUNT:-0}" -lt "${MIN_AVAILABLE_CPU}" ]; then
    SUITABLE="NO"
    RISKS+=("CPU capacity is below the Phase 1 planning threshold (${CPU_COUNT} < ${MIN_AVAILABLE_CPU}).")
  fi
  if [ "${MEM_AVAILABLE_MB:-0}" -lt "${MIN_AVAILABLE_MEM_MB}" ]; then
    SUITABLE="NO"
    RISKS+=("Available memory is below the Phase 1 planning threshold (${MEM_AVAILABLE_MB} MB < ${MIN_AVAILABLE_MEM_MB} MB).")
  fi
  local disk_free_int
  disk_free_int="$(awk -v gb="${DISK_AVAILABLE_GB:-0}" 'BEGIN {print int(gb)}')"
  if [ "${disk_free_int}" -lt "${MIN_FREE_GB}" ]; then
    SUITABLE="NO"
    RISKS+=("/opt disk free space is below the Phase 1 planning threshold (${DISK_AVAILABLE_GB} GB < ${MIN_FREE_GB} GB).")
  fi
  if [ "${DOCKER_CLI}" = "missing" ] || [ "${DOCKER_DAEMON}" != "reachable" ]; then
    RISKS+=("Docker is not fully reachable; future Control Plane container planning needs a separate maintenance window.")
  fi
  if [ "${CONTROL_DIR_STATE}" = "present" ]; then
    RISKS+=("${CONTROL_PLANE_DIR} already exists; future work must audit ownership and contents before using it.")
  fi
  if [ "${CURRENT_AI_TARGET}" = "exists but is not a symlink" ]; then
    RISKS+=("${CURRENT_AI_LINK} exists but is not a symlink; production pointer assumptions need manual review.")
  fi

  NEXT_STEPS+=("Review this report with operations before any Phase 2 design or install work.")
  NEXT_STEPS+=("If approved, prepare a separate Phase 2 plan that explicitly covers ports, users, storage, backups, and rollback.")
  NEXT_STEPS+=("Keep AI runtime, Nginx, Docker, databases, production releases, and current-enterprise-ai unchanged until an approved maintenance window.")
}

write_report() {
  {
    printf '# VAFOX Control Plane Phase 1 Report\n\n'
    printf -- '- Target: `%s` (`%s`)\n' "${TARGET_DOMAIN}" "${TARGET_IP}"
    printf -- '- Audit time UTC: `%s`\n' "${AUDIT_TIME_UTC}"
    printf -- '- Hostname: `%s`\n' "${HOSTNAME_VALUE}"
    printf -- '- Mode: `read-only Phase 1 bootstrap audit`\n'
    printf -- '- Proposed future path: `%s`\n\n' "${CONTROL_PLANE_DIR}"
    printf '## Deployment suitability\n\n'
    printf '**Suitable to proceed to Control Plane planning:** `%s`\n\n' "${SUITABLE}"
    printf 'This report does not approve or perform installation. It only indicates whether the host appears suitable for future planning of `%s`.\n\n' "${CONTROL_PLANE_DIR}"
    printf '## Safety guardrails observed\n\n'
    printf -- '- No AI business code changed.\n- Docker was not restarted.\n- Nginx was not modified.\n- Databases were not modified.\n- No production release was created.\n- `%s` was not changed.\n- `%s` was not created.\n\n' "${CURRENT_AI_LINK}" "${CONTROL_PLANE_DIR}"
    printf '## Current system resources\n\n'
    printf '| Item | Value |\n| --- | --- |\n'
    printf '| Kernel | `%s` |\n' "${KERNEL_VALUE}"
    printf '| CPU online cores | `%s` |\n' "${CPU_COUNT}"
    printf '| Load average | `%s` |\n' "${LOAD_AVG}"
    printf '| Memory total | `%s MB` |\n' "${MEM_TOTAL_MB}"
    printf '| Memory available | `%s MB` |\n\n' "${MEM_AVAILABLE_MB}"
    printf '## Docker status\n\n'
    printf '| Item | Value |\n| --- | --- |\n'
    printf '| Docker CLI | `%s` |\n' "${DOCKER_CLI}"
    printf '| Docker daemon | `%s` |\n' "${DOCKER_DAEMON}"
    printf '| Running containers | `%s` |\n\n' "${DOCKER_RUNNING_COUNT}"
    printf '### Running containers\n\n```text\n%s\n```\n\n' "${DOCKER_NAMES:-none detected or unavailable}"
    printf '## Disk space\n\n'
    printf '| Mount checked | Total | Available | Used |\n| --- | ---: | ---: | ---: |\n'
    printf '| `%s` | `%s GB` | `%s GB` | `%s` |\n\n' "${DISK_MOUNT}" "$(bytes_to_gb "${DISK_TOTAL_BYTES}")" "${DISK_AVAILABLE_GB}" "${DISK_USED_PCT}"
    printf '## Current AI service occupancy\n\n'
    printf -- '- Production root checked: `%s`\n' "${PROD_ROOT}"
    printf -- '- Current AI pointer: `%s` -> `%s`\n' "${CURRENT_AI_LINK}" "${CURRENT_AI_TARGET}"
    printf -- '- Future Control Plane directory state: `%s` is `%s`\n\n' "${CONTROL_PLANE_DIR}" "${CONTROL_DIR_STATE}"
    printf '### Listening TCP ports\n\n```text\n%s\n```\n\n' "${LISTENING_PORTS:-unavailable}"
    printf '### AI/service process hints\n\n```text\n%s\n```\n\n' "${AI_PROCESS_HINTS:-none detected or unavailable}"
    printf '## Risks\n\n'
    if [ "${#RISKS[@]}" -eq 0 ]; then
      printf -- '- No blocking Phase 1 readiness risks detected by this read-only audit.\n'
    else
      local risk
      for risk in "${RISKS[@]}"; do printf -- '- %s\n' "${risk}"; done
    fi
    printf '\n## Recommended next steps\n\n'
    local step
    for step in "${NEXT_STEPS[@]}"; do printf -- '- %s\n' "${step}"; done
  } > "${REPORT_PATH}"
}

collect_scalar_facts
assess_readiness
write_report
printf 'Wrote read-only Phase 1 report: %s\n' "${REPORT_PATH}"
