#!/usr/bin/env bash
# VAFOX_INFRA_AUDIT_ONE_COMMAND_RUNNER
# One-command, read-mostly infrastructure audit runner for VAFOX servers.
# Usage: bash vafox_infra_audit_runner.sh
# Safety: this script only reads system state and writes its own report under
# /opt/vafox-audit/reports/. It does not change Docker, Nginx, databases, or services.

set -u

REPORT_ROOT="/opt/vafox-audit/reports"
RUN_TS="$(date -u +%Y%m%dT%H%M%SZ)"
HOST_SHORT="$(hostname -s 2>/dev/null || hostname 2>/dev/null || echo unknown-host)"
REPORT_FILE="${REPORT_ROOT}/vafox_infra_audit_${HOST_SHORT}_${RUN_TS}.md"

KNOWN_HUYAN_IP="140.143.207.194"
KNOWN_AI_IP="1.13.254.217"
KNOWN_CORE_IP="139.199.174.36"

mkdir -p "$REPORT_ROOT" || {
  echo "ERROR: cannot create ${REPORT_ROOT}. Try running with a user that can write /opt." >&2
  exit 1
}

command_exists() { command -v "$1" >/dev/null 2>&1; }

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

append_text() {
  {
    echo
    echo "$1"
  } >> "$REPORT_FILE"
}

collect_local_ips() {
  {
    hostname -I 2>/dev/null || true
    if command_exists ip; then
      ip -o -4 addr show 2>/dev/null | awk '{print $4}' | cut -d/ -f1 || true
      ip -o -6 addr show scope global 2>/dev/null | awk '{print $4}' | cut -d/ -f1 || true
    fi
  } | tr ' ' '\n' | sed '/^$/d' | sort -u
}

LOCAL_IPS="$(collect_local_ips)"
SERVER_ID="Unknown"
SERVER_ROLE="unknown"
SERVER_IP="unknown"
AUDIT_FOCUS="Generic VAFOX infrastructure audit. This host IP is not one of the registered VAFOX audit targets."

case "${LOCAL_IPS}" in
  *"${KNOWN_HUYAN_IP}"*)
    SERVER_ID="Huyan"
    SERVER_ROLE="huyan"
    SERVER_IP="${KNOWN_HUYAN_IP}"
    AUDIT_FOCUS="Huyan node audit: host baseline, public edge clues, automation/runtime directories."
    ;;
  *"${KNOWN_AI_IP}"*)
    SERVER_ID="AI"
    SERVER_ROLE="ai"
    SERVER_IP="${KNOWN_AI_IP}"
    AUDIT_FOCUS="AI node audit: model/application runtime clues, Docker/Nginx exposure, data and backup hints."
    ;;
  *"${KNOWN_CORE_IP}"*)
    SERVER_ID="Core"
    SERVER_ROLE="core"
    SERVER_IP="${KNOWN_CORE_IP}"
    AUDIT_FOCUS="Core node audit: core API/runtime clues, Nginx routing, persistence and backup hints."
    ;;
esac

cat > "$REPORT_FILE" <<HEADER
# VAFOX Infrastructure Audit Report

- Generated UTC: ${RUN_TS}
- Hostname: ${HOST_SHORT}
- Detected identity: ${SERVER_ID}
- Detected target IP: ${SERVER_IP}
- Audit profile: ${SERVER_ROLE}
- Safety mode: read-only audit; only this report file is written.
- Report path: ${REPORT_FILE}

## Registered VAFOX Targets

| Identity | IP |
| --- | --- |
| Huyan | ${KNOWN_HUYAN_IP} |
| AI | ${KNOWN_AI_IP} |
| Core | ${KNOWN_CORE_IP} |

## Audit Logic Selected

${AUDIT_FOCUS}
HEADER

run_section "Host Identity" sh -c 'echo "Hostname: $(hostname 2>/dev/null || true)"; echo "FQDN: $(hostname -f 2>/dev/null || true)"; echo "Kernel: $(uname -a 2>/dev/null || true)"; echo "OS:"; (cat /etc/os-release 2>/dev/null || true); echo "Uptime:"; uptime 2>/dev/null || true; echo "Current user: $(id 2>/dev/null || true)"'
run_section "Detected IP Addresses" sh -c 'hostname -I 2>/dev/null || true; command -v ip >/dev/null 2>&1 && ip addr show 2>/dev/null || true'
run_section "CPU / Memory / Disk" sh -c 'echo "CPU:"; (lscpu 2>/dev/null || cat /proc/cpuinfo 2>/dev/null | head -80 || true); echo; echo "Memory:"; free -h 2>/dev/null || cat /proc/meminfo 2>/dev/null | head -40 || true; echo; echo "Disk usage:"; df -hT 2>/dev/null || true; echo; echo "Block devices:"; lsblk -f 2>/dev/null || true'
run_section "Docker" sh -c 'if command -v docker >/dev/null 2>&1; then docker --version; echo; docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"; echo; docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.ID}}\t{{.Size}}"; echo; docker network ls; else echo "Docker command not found."; fi'
run_section "Nginx" sh -c 'if command -v nginx >/dev/null 2>&1; then nginx -v; echo; nginx -T 2>/dev/null | sed -n "1,260p"; else echo "Nginx command not found."; fi; echo; echo "Common Nginx paths:"; find /etc/nginx -maxdepth 3 -type f 2>/dev/null | sort || true'
run_section "Network" sh -c 'echo "Routes:"; (ip route show 2>/dev/null || route -n 2>/dev/null || true); echo; echo "Listening sockets:"; (ss -tulpen 2>/dev/null || netstat -tulpen 2>/dev/null || true); echo; echo "Firewall clues:"; (ufw status 2>/dev/null || true); (firewall-cmd --state 2>/dev/null && firewall-cmd --list-all 2>/dev/null || true); (iptables -S 2>/dev/null | sed -n "1,120p" || true)'
run_section "SSL Clues" sh -c 'echo "Certificate files under common paths:"; find /etc/letsencrypt /etc/nginx /opt /srv /var/www -maxdepth 5 \( -name "*.crt" -o -name "*.pem" -o -name "*.key" \) 2>/dev/null | sort | sed -n "1,240p"; echo; echo "Certbot:"; certbot certificates 2>/dev/null || echo "certbot unavailable or no readable certificates."'
run_section "Application Directories" sh -c 'echo "Top-level candidates:"; find /opt /srv /var/www /home -maxdepth 3 -type d 2>/dev/null | sort | sed -n "1,260p"; echo; echo "Compose/package clues:"; find /opt /srv /var/www /home -maxdepth 5 -type f \( -name "docker-compose.yml" -o -name "compose.yml" -o -name "package.json" -o -name "requirements.txt" -o -name "pyproject.toml" -o -name "*.service" \) 2>/dev/null | sort | sed -n "1,260p"'
run_section "Backup Clues" sh -c 'echo "Backup-like directories/files:"; find /opt /srv /var /home -maxdepth 5 \( -iname "*backup*" -o -iname "*bak*" -o -iname "*.sql" -o -iname "*.dump" -o -iname "*.tar.gz" -o -iname "*.tgz" \) 2>/dev/null | sort | sed -n "1,260p"; echo; echo "Cron clues:"; (crontab -l 2>/dev/null || true); find /etc/cron.d /etc/cron.daily /etc/cron.hourly /etc/cron.weekly /etc/cron.monthly -maxdepth 2 -type f 2>/dev/null | sort | xargs -r sed -n "1,80p" 2>/dev/null || true'

{
  echo
  echo "## Risks"
  echo
  echo "The following are audit prompts, not automatic verdicts. Review the evidence sections above."
  echo
  echo "- Unknown identity risk: detected when local IPs do not match Huyan/AI/Core registered IPs. Current identity: ${SERVER_ID}."
  echo "- Capacity risk: check CPU load, memory pressure, disk usage above 80%, and inode exhaustion."
  echo "- Docker risk: check containers with broad host port exposure, stale images, privileged mounts, or unhealthy status."
  echo "- Nginx risk: check duplicate server_name entries, plaintext-only listeners, proxy targets to missing services, and exposed default sites."
  echo "- Network risk: check unexpected listening ports, broad firewall allow rules, and services bound to 0.0.0.0."
  echo "- SSL risk: check missing certificates, expired certificates, private key file exposure, and domains not covered by certbot output."
  echo "- Application directory risk: check unknown deployments under /opt, /srv, /var/www, and /home."
  echo "- Backup risk: check missing scheduled backups, unencrypted database dumps, and backups stored only on the same host."
  echo
  echo "## Read-only Safety Confirmation"
  echo
  echo "This runner does not call package managers, docker modification commands, nginx reload/test modification flows, database clients, systemctl restart/reload, or service management commands."
} >> "$REPORT_FILE"

echo "VAFOX infrastructure audit completed."
echo "Identity: ${SERVER_ID} (${SERVER_IP})"
echo "Report: ${REPORT_FILE}"
