#!/usr/bin/env bash
set -Eeuo pipefail

# Minimal replacement updater for ai.vafox.com production installer.
# This script only backs up and replaces ai_release_tooling_installer.sh, then
# validates help output and confirms the production current symlink is unchanged.
# It does not use base64, tar, git, docker, nginx, database tooling, candidate
# builds, or symlink changes.

PROD_ROOT="${PROD_ROOT:-/opt/ai-vafox}"
OPS_DIR="${OPS_DIR:-${PROD_ROOT}/ops}"
INSTALLER_PATH="${INSTALLER_PATH:-${OPS_DIR}/ai_release_tooling_installer.sh}"
BACKUP_PATH="${BACKUP_PATH:-${INSTALLER_PATH}.backup}"
CURRENT_LINK="${CURRENT_LINK:-${PROD_ROOT}/current-enterprise-ai}"
EXPECTED_CURRENT_TARGET="${EXPECTED_CURRENT_TARGET:-${PROD_ROOT}/releases/fba3c17}"
TMP_INSTALLER=""

log() { printf '[%s] %s\n' "$(date -u +%H:%M:%S)" "$*"; }
fail() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }

cleanup() {
  if [ -n "${TMP_INSTALLER}" ] && [ -e "${TMP_INSTALLER}" ]; then
    rm -f "${TMP_INSTALLER}"
  fi
}
trap cleanup EXIT

usage() {
  cat <<'USAGE'
Minimal AI installer replacement updater

Usage:
  bash ai_release_installer_replace_only.sh

Actions performed:
  1. Backup /opt/ai-vafox/ops/ai_release_tooling_installer.sh to
     /opt/ai-vafox/ops/ai_release_tooling_installer.sh.backup
  2. Replace ai_release_tooling_installer.sh with fixed safe content
  3. Validate the replacement with bash -n
  4. Verify EXPECTED_CURRENT_TARGET points at releases/fba3c17
  5. Run the replacement installer with --help only
  6. Verify current-enterprise-ai remains on releases/fba3c17

Forbidden actions: base64 payloads, tar archives, git, docker, nginx, database
operations, candidate builds, and symlink changes.
USAGE
}

if [ "${1:-}" = "--help" ] || [ "${1:-}" = "-h" ]; then
  usage
  exit 0
fi

current_target() {
  if [ -e "${CURRENT_LINK}" ] || [ -L "${CURRENT_LINK}" ]; then
    readlink -f "${CURRENT_LINK}"
  else
    printf '__missing__'
  fi
}

verify_current_target_unchanged() {
  local actual
  actual="$(current_target)"
  if [ "${actual}" != "${EXPECTED_CURRENT_TARGET}" ]; then
    fail "${CURRENT_LINK} resolves to ${actual}; expected ${EXPECTED_CURRENT_TARGET}"
  fi
  log "verified ${CURRENT_LINK} -> ${actual}"
}

write_fixed_installer() {
  TMP_INSTALLER="$(mktemp "${TMPDIR:-/tmp}/ai_release_tooling_installer.fixed.XXXXXX")"
  cat > "${TMP_INSTALLER}" <<'INSTALLER'
#!/usr/bin/env bash
set -Eeuo pipefail

# Fixed minimal AI release tooling installer for ai.vafox.com production.
# Help-only safety replacement. It does not install payloads, create candidate
# builds, change symlinks, invoke git/tar/docker/nginx/database commands, or
# modify production runtime state.

TARGET_DOMAIN="${TARGET_DOMAIN:-ai.vafox.com}"
PROD_ROOT="${PROD_ROOT:-/opt/ai-vafox}"
CURRENT_LINK="${CURRENT_LINK:-${PROD_ROOT}/current-enterprise-ai}"
EXPECTED_CURRENT_TARGET="${EXPECTED_CURRENT_TARGET:-${PROD_ROOT}/releases/fba3c17}"

usage() {
  cat <<'USAGE'
AI release tooling installer

Usage:
  bash /opt/ai-vafox/ops/ai_release_tooling_installer.sh --help

This fixed minimal installer is intentionally help-only. It exists to replace a
corrupted generated installer safely while preserving production state.

Safety guard:
  EXPECTED_CURRENT_TARGET defaults to ${PROD_ROOT}/releases/fba3c17.

Forbidden actions: base64 payloads, tar archives, git, docker, nginx, database
operations, candidate builds, and symlink changes.
USAGE
}

if [ "${1:-}" = "--help" ] || [ "${1:-}" = "-h" ]; then
  usage
  exit 0
fi

printf 'ERROR: this fixed minimal installer is help-only; run with --help.\n' >&2
exit 2
INSTALLER
}

main() {
  log "starting minimal installer replacement for ${INSTALLER_PATH}"
  verify_current_target_unchanged

  [ -f "${INSTALLER_PATH}" ] || fail "installer not found: ${INSTALLER_PATH}"
  mkdir -p "${OPS_DIR}"

  cp -p "${INSTALLER_PATH}" "${BACKUP_PATH}"
  log "backup written: ${BACKUP_PATH}"

  write_fixed_installer
  install -m 0755 "${TMP_INSTALLER}" "${INSTALLER_PATH}"
  log "replacement written: ${INSTALLER_PATH}"

  bash -n "${INSTALLER_PATH}"
  log "syntax validation passed"

  if ! grep -n 'EXPECTED_CURRENT_TARGET=.*\(releases/fba3c17\|\${PROD_ROOT}/releases/fba3c17\)' "${INSTALLER_PATH}" >/dev/null; then
    fail "EXPECTED_CURRENT_TARGET does not use ${PROD_ROOT}/releases/fba3c17 or \${PROD_ROOT}/releases/fba3c17"
  fi
  log "EXPECTED_CURRENT_TARGET verification passed"

  bash "${INSTALLER_PATH}" --help
  log "help-only execution completed"

  verify_current_target_unchanged
  log "minimal installer replacement completed safely"
}

main "$@"
