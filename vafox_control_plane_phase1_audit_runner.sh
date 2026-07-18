#!/usr/bin/env bash
set -uo pipefail

REPORT_DIR="/opt/vafox-audit/reports"
REPORT_FILE="${REPORT_DIR}/VAFOX_CONTROL_PLANE_PHASE1_REPORT.md"
AI_ROOT="/opt/ai-vafox"
CONTROL_ROOT="/opt/vafox-control"
HOST_IP="1.13.254.217"

PASS_COUNT=0
WARN_COUNT=0
FAIL_COUNT=0
INFO_COUNT=0
RISKS=()
RECOMMENDATIONS=()
CAPACITY_NOTES=()
CONTROL_PLANE_RECOMMENDATION="Conditional"
EXECUTIVE_VERDICT="Review Required"

mkdir -p "${REPORT_DIR}" 2>/dev/null || {
  echo "ERROR: cannot create report directory: ${REPORT_DIR}" >&2
  exit 1
}

TMP_REPORT="$(mktemp)" || exit 1
cleanup() {
  rm -f "${TMP_REPORT}"
}
trap cleanup EXIT

now_utc() {
  date -u '+%Y-%m-%d %H:%M:%S UTC'
}

run_cmd() {
  local cmd="$1"
  bash -lc "$cmd" 2>&1
}

status_line() {
  local status="$1"
  local text="$2"
  case "${status}" in
    PASS) PASS_COUNT=$((PASS_COUNT + 1)); echo "- ✅ PASS: ${text}" >> "${TMP_REPORT}" ;;
    WARN) WARN_COUNT=$((WARN_COUNT + 1)); echo "- ⚠️ WARN: ${text}" >> "${TMP_REPORT}" ;;
    FAIL) FAIL_COUNT=$((FAIL_COUNT + 1)); echo "- ❌ FAIL: ${text}" >> "${TMP_REPORT}" ;;
    INFO) INFO_COUNT=$((INFO_COUNT + 1)); echo "- ℹ️ INFO: ${text}" >> "${TMP_REPORT}" ;;
  esac
}

add_risk() {
  RISKS+=("$1")
}

add_recommendation() {
  RECOMMENDATIONS+=("$1")
}

add_capacity_note() {
  CAPACITY_NOTES+=("$1")
}

section() {
  echo "" >> "${TMP_REPORT}"
  echo "## $1" >> "${TMP_REPORT}"
  echo "" >> "${TMP_REPORT}"
}

code_block() {
  local title="$1"
  local body="$2"
  echo "" >> "${TMP_REPORT}"
  echo "### ${title}" >> "${TMP_REPORT}"
  echo "" >> "${TMP_REPORT}"
  echo '```text' >> "${TMP_REPORT}"
  printf '%s\n' "${body}" >> "${TMP_REPORT}"
  echo '```' >> "${TMP_REPORT}"
}

bytes_to_gib() {
  awk -v b="$1" 'BEGIN { if (b <= 0) { print "0.00" } else { printf "%.2f", b/1024/1024/1024 } }'
}

percent_int() {
  awk -v a="$1" -v b="$2" 'BEGIN { if (b <= 0) { print 0 } else { printf "%.0f", (a/b)*100 } }'
}

cpu_audit() {
  section "CPU"
  local cpu_count load1 load5 load15 cpu_model
  cpu_count="$(nproc 2>/dev/null || echo 0)"
  read -r load1 load5 load15 _ < /proc/loadavg 2>/dev/null || { load1="unknown"; load5="unknown"; load15="unknown"; }
  cpu_model="$(awk -F': ' '/model name/ {print $2; exit}' /proc/cpuinfo 2>/dev/null || true)"
  [ -n "${cpu_model}" ] || cpu_model="unknown"

  status_line INFO "Host IP target: ${HOST_IP}"
  status_line INFO "CPU cores: ${cpu_count}"
  status_line INFO "CPU model: ${cpu_model}"
  status_line INFO "Load average: ${load1}, ${load5}, ${load15}"

  if [ "${cpu_count}" -ge 8 ] 2>/dev/null; then
    status_line PASS "CPU core count is suitable for a small Control Plane footprint."
    add_capacity_note "CPU: ${cpu_count} cores available; suitable for Phase 1 Control Plane if AI workload headroom remains acceptable."
  elif [ "${cpu_count}" -ge 4 ] 2>/dev/null; then
    status_line WARN "CPU core count is modest; Control Plane should remain lightweight."
    add_capacity_note "CPU: ${cpu_count} cores available; capacity is modest and should be protected with container CPU limits."
    add_risk "CPU headroom may be constrained if AI containers spike."
  else
    status_line FAIL "CPU core count is low for co-locating AI and Control Plane workloads."
    add_capacity_note "CPU: ${cpu_count} cores available; not recommended without strict isolation or separate host."
    add_risk "Insufficient CPU capacity for reliable co-location."
  fi
}

memory_audit() {
  section "Memory"
  local mem_total_kb mem_avail_kb swap_total_kb mem_total_gib mem_avail_gib used_pct
  mem_total_kb="$(awk '/MemTotal/ {print $2}' /proc/meminfo 2>/dev/null || echo 0)"
  mem_avail_kb="$(awk '/MemAvailable/ {print $2}' /proc/meminfo 2>/dev/null || echo 0)"
  swap_total_kb="$(awk '/SwapTotal/ {print $2}' /proc/meminfo 2>/dev/null || echo 0)"
  mem_total_gib="$(awk -v kb="${mem_total_kb}" 'BEGIN { printf "%.2f", kb/1024/1024 }')"
  mem_avail_gib="$(awk -v kb="${mem_avail_kb}" 'BEGIN { printf "%.2f", kb/1024/1024 }')"
  used_pct="$(awk -v t="${mem_total_kb}" -v a="${mem_avail_kb}" 'BEGIN { if (t <= 0) print 0; else printf "%.0f", ((t-a)/t)*100 }')"

  status_line INFO "Total memory: ${mem_total_gib} GiB"
  status_line INFO "Available memory: ${mem_avail_gib} GiB"
  status_line INFO "Memory used: ${used_pct}%"
  status_line INFO "Swap total: $(awk -v kb="${swap_total_kb}" 'BEGIN { printf "%.2f", kb/1024/1024 }') GiB"

  if [ "${mem_total_kb}" -ge 33554432 ] && [ "${mem_avail_kb}" -ge 8388608 ]; then
    status_line PASS "Memory capacity and current availability are suitable for Phase 1."
    add_capacity_note "Memory: ${mem_total_gib} GiB total and ${mem_avail_gib} GiB available; suitable for Phase 1."
  elif [ "${mem_total_kb}" -ge 16777216 ] && [ "${mem_avail_kb}" -ge 4194304 ]; then
    status_line WARN "Memory is acceptable only for a lightweight Control Plane."
    add_capacity_note "Memory: ${mem_total_gib} GiB total and ${mem_avail_gib} GiB available; acceptable with memory limits and monitoring."
    add_risk "Memory pressure from AI workloads could affect Control Plane reliability."
  else
    status_line FAIL "Memory capacity or availability is insufficient for safe co-location."
    add_capacity_note "Memory: ${mem_total_gib} GiB total and ${mem_avail_gib} GiB available; insufficient for safe co-location."
    add_risk "Insufficient memory headroom for Phase 1 Control Plane."
  fi
}

disk_audit() {
  section "Disk"
  local root_df opt_df root_use opt_use
  root_df="$(df -hP / 2>/dev/null || true)"
  opt_df="$(df -hP /opt 2>/dev/null || true)"
  root_use="$(df -P / 2>/dev/null | awk 'NR==2 {gsub(/%/,"",$5); print $5}')"
  opt_use="$(df -P /opt 2>/dev/null | awk 'NR==2 {gsub(/%/,"",$5); print $5}')"
  code_block "Filesystem /" "${root_df}"
  code_block "Filesystem /opt" "${opt_df}"

  if [ "${opt_use:-100}" -lt 75 ] 2>/dev/null; then
    status_line PASS "/opt disk usage is below 75% (${opt_use}%)."
    add_capacity_note "Disk: /opt usage is ${opt_use}%; current free space appears suitable for Phase 1."
  elif [ "${opt_use:-100}" -lt 90 ] 2>/dev/null; then
    status_line WARN "/opt disk usage is elevated (${opt_use}%)."
    add_capacity_note "Disk: /opt usage is ${opt_use}%; proceed only after log/data growth budget is defined."
    add_risk "Disk growth may affect Docker, AI workloads, or Control Plane logs."
  else
    status_line FAIL "/opt disk usage is critical (${opt_use}%)."
    add_capacity_note "Disk: /opt usage is ${opt_use}%; not suitable until space is reclaimed or expanded."
    add_risk "Critical /opt disk utilization."
  fi

  if [ "${root_use:-100}" -ge 90 ] 2>/dev/null; then
    status_line FAIL "/ disk usage is critical (${root_use}%)."
    add_risk "Root filesystem is critically full."
  fi
}

docker_audit() {
  section "Docker Status"
  if ! command -v docker >/dev/null 2>&1; then
    status_line FAIL "Docker CLI is not installed or not in PATH."
    add_risk "Docker is unavailable; AI container and resource audit cannot be completed."
    return
  fi

  local docker_version docker_info docker_ps
  docker_version="$(docker version --format '{{.Server.Version}}' 2>/dev/null || true)"
  if [ -n "${docker_version}" ]; then
    status_line PASS "Docker daemon is reachable. Server version: ${docker_version}."
  else
    status_line FAIL "Docker daemon is not reachable by this audit user."
    add_risk "Docker daemon access unavailable; cannot validate container state."
    return
  fi

  docker_info="$(docker info --format 'Containers={{.Containers}} Running={{.ContainersRunning}} Paused={{.ContainersPaused}} Stopped={{.ContainersStopped}} Images={{.Images}} Driver={{.Driver}} CgroupDriver={{.CgroupDriver}} CgroupVersion={{.CgroupVersion}}' 2>/dev/null || true)"
  status_line INFO "Docker info: ${docker_info}"
  docker_ps="$(docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}' 2>/dev/null || true)"
  code_block "Running Containers" "${docker_ps}"

  section "Docker Resources"
  local docker_df docker_stats
  docker_df="$(docker system df 2>/dev/null || true)"
  docker_stats="$(docker stats --no-stream --format 'table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}\t{{.NetIO}}\t{{.BlockIO}}' 2>/dev/null || true)"
  code_block "Docker Disk Usage" "${docker_df}"
  code_block "Docker Runtime Stats" "${docker_stats}"
}

ai_container_audit() {
  section "AI Containers"
  if ! command -v docker >/dev/null 2>&1 || ! docker version >/dev/null 2>&1; then
    status_line WARN "Skipped AI container audit because Docker is unavailable."
    return
  fi

  local ai_containers count unhealthy restarting exited
  ai_containers="$(docker ps -a --format '{{.Names}}\t{{.Image}}\t{{.Status}}' | awk 'BEGIN{IGNORECASE=1} /ai|vafox|current-enterprise-ai|model|llm|gpu|nvidia/ {print}' 2>/dev/null || true)"
  count="$(printf '%s\n' "${ai_containers}" | sed '/^$/d' | wc -l | tr -d ' ')"
  code_block "Detected AI-related Containers" "${ai_containers:-No AI-related containers matched by name/image/status.}"

  if [ "${count}" -gt 0 ] 2>/dev/null; then
    status_line PASS "Detected ${count} AI-related container(s) for review."
  else
    status_line WARN "No AI-related containers detected by conservative name/image matching."
    add_risk "AI container naming may be non-standard, or AI workload may not be containerized."
  fi

  unhealthy="$(docker ps -a --filter health=unhealthy --format '{{.Names}} {{.Status}}' 2>/dev/null || true)"
  restarting="$(docker ps -a --filter status=restarting --format '{{.Names}} {{.Status}}' 2>/dev/null || true)"
  exited="$(docker ps -a --filter status=exited --format '{{.Names}} {{.Status}}' 2>/dev/null | head -50 || true)"
  [ -z "${unhealthy}" ] && status_line PASS "No unhealthy Docker containers reported." || { status_line FAIL "Unhealthy containers found."; code_block "Unhealthy Containers" "${unhealthy}"; add_risk "One or more containers are unhealthy."; }
  [ -z "${restarting}" ] && status_line PASS "No restarting Docker containers reported." || { status_line FAIL "Restarting containers found."; code_block "Restarting Containers" "${restarting}"; add_risk "One or more containers are stuck restarting."; }
  [ -z "${exited}" ] && status_line INFO "No exited containers reported." || code_block "Exited Containers (first 50)" "${exited}"
}

path_audit() {
  local path="$1"
  local label="$2"
  section "${label}"

  if [ -e "${path}" ]; then
    status_line PASS "${path} exists."
    local path_info du_info df_info perms
    path_info="$(stat -c 'Path=%n Type=%F Owner=%U Group=%G Mode=%A Modified=%y' "${path}" 2>/dev/null || true)"
    du_info="$(du -sh "${path}" 2>/dev/null || true)"
    df_info="$(df -hP "${path}" 2>/dev/null || true)"
    perms="$(find "${path}" -maxdepth 1 -mindepth 1 -printf '%M %u %g %p\n' 2>/dev/null | head -100 || true)"
    code_block "Path Metadata" "${path_info}"
    code_block "Path Size" "${du_info}"
    code_block "Path Filesystem" "${df_info}"
    code_block "Top-level Entries (read-only, first 100)" "${perms}"
  else
    status_line WARN "${path} does not exist."
    add_risk "Expected path missing: ${path}."
  fi
}

security_guardrails() {
  section "Read-only Guardrails"
  status_line PASS "Audit performs read-only inspection only; it does not install packages."
  status_line PASS "Audit does not modify Docker, Nginx, databases, current-enterprise-ai, or release artifacts."
  status_line INFO "Only write action is report generation at ${REPORT_FILE}."
}

finalize_verdict() {
  if [ "${FAIL_COUNT}" -gt 0 ]; then
    EXECUTIVE_VERDICT="Not Recommended Until Critical Findings Are Resolved"
    CONTROL_PLANE_RECOMMENDATION="No"
  elif [ "${WARN_COUNT}" -gt 4 ]; then
    EXECUTIVE_VERDICT="Conditionally Recommended With Mitigations"
    CONTROL_PLANE_RECOMMENDATION="Conditional"
  else
    EXECUTIVE_VERDICT="Recommended for Phase 1 With Standard Monitoring"
    CONTROL_PLANE_RECOMMENDATION="Yes"
  fi

  local final_report
  final_report="$(mktemp)" || exit 1
  {
    echo "# VAFOX Control Plane Phase 1 Audit Report"
    echo ""
    echo "- Generated: $(now_utc)"
    echo "- Target AI server: ${HOST_IP}"
    echo "- AI path: ${AI_ROOT}"
    echo "- Control Plane path: ${CONTROL_ROOT}"
    echo "- Report path: ${REPORT_FILE}"
    echo "- Mode: read-only audit"
    echo ""
    echo "## Executive Verdict"
    echo ""
    echo "${EXECUTIVE_VERDICT}"
    echo ""
    echo "- PASS: ${PASS_COUNT}"
    echo "- WARN: ${WARN_COUNT}"
    echo "- FAIL: ${FAIL_COUNT}"
    echo "- INFO: ${INFO_COUNT}"
    echo ""
    echo "## 是否推荐AI作为Control Plane"
    echo ""
    echo "${CONTROL_PLANE_RECOMMENDATION}"
    echo ""
    echo "## 容量判断"
    echo ""
    if [ "${#CAPACITY_NOTES[@]}" -eq 0 ]; then
      echo "- No capacity notes were generated."
    else
      printf -- '- %s\n' "${CAPACITY_NOTES[@]}"
    fi
    echo ""
    echo "## 风险"
    echo ""
    if [ "${#RISKS[@]}" -eq 0 ]; then
      echo "- No material risks identified by this read-only audit."
    else
      printf -- '- %s\n' "${RISKS[@]}"
    fi
    echo ""
    echo "## 下一步建议"
    echo ""
    if [ "${#RECOMMENDATIONS[@]}" -eq 0 ]; then
      echo "- Keep the Control Plane lightweight for Phase 1."
      echo "- Define Docker CPU and memory limits before production co-location."
      echo "- Add monitoring for CPU, memory, disk, Docker health, and container restarts."
      echo "- Confirm backup and rollback procedures before enabling Control Plane changes."
      echo "- Re-run this audit after any deployment, migration, or capacity change."
    else
      printf -- '- %s\n' "${RECOMMENDATIONS[@]}"
    fi
    cat "${TMP_REPORT}"
  } > "${final_report}"
  mv "${final_report}" "${REPORT_FILE}"
}

main() {
  echo "# Detailed Findings" > "${TMP_REPORT}"
  security_guardrails
  cpu_audit
  memory_audit
  disk_audit
  docker_audit
  ai_container_audit
  path_audit "${AI_ROOT}" "/opt/ai-vafox"
  path_audit "${CONTROL_ROOT}" "/opt/vafox-control Space"
  add_recommendation "Review this report at ${REPORT_FILE} and resolve FAIL findings before using AI as the Control Plane."
  finalize_verdict
  echo "VAFOX Control Plane Phase 1 audit complete: ${REPORT_FILE}"
}

main "$@"
