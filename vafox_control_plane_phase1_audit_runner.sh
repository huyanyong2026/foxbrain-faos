#!/usr/bin/env bash
# VAFOX_CONTROL_PLANE_PHASE1_AUDIT_OFFLINE_RUNNER
# Read-only Phase 1 readiness audit runner for the VAFOX AI server.
# Target: ai.vafox.com / 1.13.254.217
# Usage: bash vafox_control_plane_phase1_audit_runner.sh
# Safety: only creates /opt/vafox-audit/reports when needed and writes the report file.
# It does not install software, modify Docker, Nginx, databases, current-enterprise-ai, or release paths.

set -u

TARGET_DOMAIN="ai.vafox.com"
TARGET_IP="1.13.254.217"
REPORT_ROOT="/opt/vafox-audit/reports"
REPORT_FILE="${REPORT_ROOT}/VAFOX_CONTROL_PLANE_PHASE1_REPORT.md"
RUN_TS="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
HOSTNAME_FULL="$(hostname -f 2>/dev/null || hostname 2>/dev/null || echo unknown-host)"
HOSTNAME_SHORT="$(hostname -s 2>/dev/null || hostname 2>/dev/null || echo unknown-host)"

mkdir -p "$REPORT_ROOT" || {
  echo "ERROR: cannot create ${REPORT_ROOT}. Run with a user allowed to write /opt/vafox-audit/reports." >&2
  exit 1
}

command_exists() { command -v "$1" >/dev/null 2>&1; }


collect_local_ips() {
  {
    hostname -I 2>/dev/null || true
    if command_exists ip; then
      ip -o -4 addr show 2>/dev/null | awk '{print $4}' | cut -d/ -f1 || true
      ip -o -6 addr show scope global 2>/dev/null | awk '{print $4}' | cut -d/ -f1 || true
    fi
  } | tr ' ' '\n' | sed '/^$/d' | sort -u
}

run_section() {
  local title="$1"
  shift
  {
    echo
    echo "## ${title}"
    echo
    echo '```text'
    "$@" 2>&1 || true
    echo '```'
  } >> "$REPORT_FILE"
}

append_section_text() {
  local title="$1"
  local body="$2"
  {
    echo
    echo "## ${title}"
    echo
    printf '%s\n' "$body"
  } >> "$REPORT_FILE"
}

LOCAL_IPS="$(collect_local_ips)"
TARGET_MATCH="No"
printf '%s\n' "$LOCAL_IPS" | grep -qx "$TARGET_IP" && TARGET_MATCH="Yes"

CPU_CORES="$(getconf _NPROCESSORS_ONLN 2>/dev/null || nproc 2>/dev/null || echo 0)"
MEM_TOTAL_MIB="$(awk '/MemTotal:/ {printf "%.0f", $2/1024}' /proc/meminfo 2>/dev/null || echo 0)"
MEM_AVAIL_MIB="$(awk '/MemAvailable:/ {printf "%.0f", $2/1024}' /proc/meminfo 2>/dev/null || echo 0)"
ROOT_USED_PCT="$(df -P / 2>/dev/null | awk 'NR==2 {gsub(/%/,"",$5); print $5+0}' || echo 0)"
OPT_AI_EXISTS="No"
[ -d /opt/ai-vafox ] && OPT_AI_EXISTS="Yes"
CONTROL_AVAIL_MIB="$(df -Pm /opt/vafox-control 2>/dev/null | awk 'NR==2 {print $4+0}' || true)"
if [ -z "${CONTROL_AVAIL_MIB}" ]; then
  CONTROL_PARENT="/opt"
  [ -d /opt/vafox-control ] && CONTROL_PARENT="/opt/vafox-control"
  CONTROL_AVAIL_MIB="$(df -Pm "$CONTROL_PARENT" 2>/dev/null | awk 'NR==2 {print $4+0}' || echo 0)"
fi

DOCKER_STATE="Unavailable"
DOCKER_RUNNING="0"
AI_CONTAINER_COUNT="0"
AI_CONTAINER_HEALTHY="Unknown"
if command_exists docker; then
  if docker info >/dev/null 2>&1; then
    DOCKER_STATE="Running"
    DOCKER_RUNNING="$(docker ps -q 2>/dev/null | wc -l | awk '{print $1}')"
    AI_CONTAINER_COUNT="$(docker ps --format '{{.Names}}' 2>/dev/null | grep -Ei '(ai|vafox|current-enterprise-ai|ollama|llm|model|open-webui|qwen|rag)' | wc -l | awk '{print $1}')"
    UNHEALTHY_AI="$(docker ps --format '{{.Names}} {{.Status}}' 2>/dev/null | grep -Ei '(ai|vafox|current-enterprise-ai|ollama|llm|model|open-webui|qwen|rag)' | grep -Eiv '(healthy|Up)' || true)"
    [ -z "$UNHEALTHY_AI" ] && AI_CONTAINER_HEALTHY="No obvious unhealthy AI container in docker ps output" || AI_CONTAINER_HEALTHY="Review required"
  else
    DOCKER_STATE="Installed but daemon inaccessible or stopped"
  fi
fi

CAPACITY="Not recommended"
RECOMMENDATION="Not recommended as Control Plane until risks are remediated"
RISK_FLAGS=""
[ "$TARGET_MATCH" = "No" ] && RISK_FLAGS="${RISK_FLAGS}- Host IP does not exactly match ${TARGET_IP}; verify this audit ran on the AI server.\n"
[ "${CPU_CORES:-0}" -lt 4 ] && RISK_FLAGS="${RISK_FLAGS}- CPU capacity below minimum baseline of 4 cores.\n"
[ "${MEM_TOTAL_MIB:-0}" -lt 8192 ] && RISK_FLAGS="${RISK_FLAGS}- Memory below minimum baseline of 8 GiB.\n"
[ "${ROOT_USED_PCT:-0}" -ge 80 ] && RISK_FLAGS="${RISK_FLAGS}- Root filesystem usage is at or above 80%.\n"
[ "${CONTROL_AVAIL_MIB:-0}" -lt 10240 ] && RISK_FLAGS="${RISK_FLAGS}- /opt/vafox-control target filesystem has less than 10 GiB available.\n"
[ "$DOCKER_STATE" != "Running" ] && RISK_FLAGS="${RISK_FLAGS}- Docker is not confirmed running.\n"
[ "$OPT_AI_EXISTS" = "No" ] && RISK_FLAGS="${RISK_FLAGS}- /opt/ai-vafox is missing; confirm AI runtime layout.\n"

if [ -z "$RISK_FLAGS" ]; then
  CAPACITY="Recommended with normal Phase 1 safeguards"
  RECOMMENDATION="Recommended as Control Plane candidate for Phase 1"
elif [ "${CPU_CORES:-0}" -ge 4 ] && [ "${MEM_TOTAL_MIB:-0}" -ge 8192 ] && [ "${ROOT_USED_PCT:-0}" -lt 90 ] && [ "${CONTROL_AVAIL_MIB:-0}" -ge 5120 ] && [ "$DOCKER_STATE" = "Running" ]; then
  CAPACITY="Conditionally acceptable"
  RECOMMENDATION="Conditionally recommended only after listed risks are reviewed"
fi

cat > "$REPORT_FILE" <<HEADER
# VAFOX Control Plane Phase 1 Readiness Audit Report

- Generated UTC: ${RUN_TS}
- Target domain: ${TARGET_DOMAIN}
- Target IP: ${TARGET_IP}
- Hostname: ${HOSTNAME_FULL}
- Short hostname: ${HOSTNAME_SHORT}
- Local target IP match: ${TARGET_MATCH}
- Safety mode: read-only audit; only ${REPORT_FILE} is written.
- Report path: ${REPORT_FILE}

## Executive Verdict

| Question | Answer |
| --- | --- |
| Recommend AI server as Control Plane? | ${RECOMMENDATION} |
| Capacity judgment | ${CAPACITY} |
| CPU cores detected | ${CPU_CORES} |
| Memory total MiB | ${MEM_TOTAL_MIB} |
| Memory available MiB | ${MEM_AVAIL_MIB} |
| Root disk used percent | ${ROOT_USED_PCT}% |
| /opt/vafox-control available MiB | ${CONTROL_AVAIL_MIB} |
| Docker state | ${DOCKER_STATE} |
| Running Docker containers | ${DOCKER_RUNNING} |
| AI service container matches | ${AI_CONTAINER_COUNT} |
| AI service container health signal | ${AI_CONTAINER_HEALTHY} |
| /opt/ai-vafox exists | ${OPT_AI_EXISTS} |

## Risk Summary

$(if [ -n "$RISK_FLAGS" ]; then printf '%b' "$RISK_FLAGS"; else echo "- No baseline blocking risks detected by this read-only runner."; fi)
HEADER

run_section "1. CPU" sh -c 'echo "Online processors: $(getconf _NPROCESSORS_ONLN 2>/dev/null || nproc 2>/dev/null || true)"; echo; lscpu 2>/dev/null || cat /proc/cpuinfo 2>/dev/null | sed -n "1,120p"; echo; uptime 2>/dev/null || true'
run_section "2. Memory" sh -c 'free -h 2>/dev/null || true; echo; sed -n "1,40p" /proc/meminfo 2>/dev/null || true'
run_section "3. Disk" sh -c 'df -hT 2>/dev/null || true; echo; df -ih 2>/dev/null || true; echo; lsblk -f 2>/dev/null || true'
run_section "4. Docker Status" sh -c 'if command -v docker >/dev/null 2>&1; then docker --version; echo; docker info 2>/dev/null | sed -n "1,180p" || echo "Docker daemon inaccessible or stopped."; echo; docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || true; else echo "Docker command not found."; fi'
run_section "5. Docker Resource Usage" sh -c 'if command -v docker >/dev/null 2>&1; then docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}\t{{.NetIO}}\t{{.BlockIO}}\t{{.PIDs}}" 2>/dev/null || echo "Docker stats unavailable."; echo; docker system df 2>/dev/null || true; else echo "Docker command not found."; fi'
run_section "6. AI Service Containers" sh -c 'if command -v docker >/dev/null 2>&1; then echo "AI-like containers:"; docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null | { head -n 1; grep -Ei "(ai|vafox|current-enterprise-ai|ollama|llm|model|open-webui|qwen|rag)" || true; }; echo; echo "AI-like images:"; docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.ID}}\t{{.Size}}" 2>/dev/null | { head -n 1; grep -Ei "(ai|vafox|enterprise|ollama|llm|model|open-webui|qwen|rag)" || true; }; else echo "Docker command not found."; fi'
run_section "7. /opt/ai-vafox" sh -c 'if [ -d /opt/ai-vafox ]; then stat /opt/ai-vafox; echo; find /opt/ai-vafox -maxdepth 2 -mindepth 1 -printf "%M %u %g %s %TY-%Tm-%Td %TH:%TM %p\n" 2>/dev/null | sort | sed -n "1,220p"; else echo "/opt/ai-vafox does not exist."; fi'
run_section "8. /opt/vafox-control Available Space" sh -c 'TARGET=/opt/vafox-control; if [ -e "$TARGET" ]; then stat "$TARGET" 2>/dev/null || true; df -hT "$TARGET" 2>/dev/null || true; df -Pm "$TARGET" 2>/dev/null || true; else echo "$TARGET does not exist; checking parent filesystem /opt."; df -hT /opt 2>/dev/null || df -hT / 2>/dev/null || true; df -Pm /opt 2>/dev/null || df -Pm / 2>/dev/null || true; fi'

append_section_text "Capacity Judgment" "- Baseline used by this runner: at least 4 CPU cores, 8 GiB RAM, root filesystem below 80% used, at least 10 GiB available for /opt/vafox-control, Docker running, and /opt/ai-vafox present.\n- Result: ${CAPACITY}.\n- Interpretation: Control Plane Phase 1 should remain lightweight; production rollout should still validate workload-specific CPU, RAM, disk, and container headroom against real traffic."
append_section_text "Next Step Recommendations" "1. Review every risk item above before scheduling Phase 1 Control Plane work.\n2. If conditionally acceptable, reserve disk for /opt/vafox-control and confirm AI service container headroom during peak usage.\n3. Keep Phase 1 changes isolated from Docker/Nginx/database/current-enterprise-ai/release until a separate approved deployment window.\n4. Re-run this audit immediately before implementation and archive this report with the Phase 1 change record."
append_section_text "Read-only Safety Confirmation" "This script only reads system state and writes ${REPORT_FILE}. It does not install software, create directories outside ${REPORT_ROOT}, modify Docker, modify Nginx, modify databases, modify current-enterprise-ai, or modify release paths."

echo "VAFOX Control Plane Phase 1 readiness audit completed."
echo "Report: ${REPORT_FILE}"
