#!/usr/bin/env bash
set -Eeuo pipefail

# AI Genesis release-candidate build executor for ai.vafox.com.
# This script creates, builds, starts, validates, reports, and cleans up an
# isolated candidate runtime. It never changes the production current symlink.

TARGET_DOMAIN="${TARGET_DOMAIN:-ai.vafox.com}"
RC_VERSION="${RC_VERSION:-AI-OS-V6-CLEAN-REBUILD-V1-RC}"
PROD_ROOT="${PROD_ROOT:-/opt/ai-vafox}"
SOURCE_REPO="${SOURCE_REPO:-$(git rev-parse --show-toplevel 2>/dev/null)}"
RELEASES_DIR="${RELEASES_DIR:-${PROD_ROOT}/releases}"
CURRENT_SYMLINK="${CURRENT_SYMLINK:-${PROD_ROOT}/current-enterprise-ai}"
EXPECTED_CURRENT_TARGET="${EXPECTED_CURRENT_TARGET:-releases/fba3c17}"
PREVIEW_HOST="${PREVIEW_HOST:-127.0.0.1}"
PREVIEW_PORT="${PREVIEW_PORT:-18086}"
KEEP_RUNTIME="${KEEP_RUNTIME:-0}"
KEEP_FAILED_RELEASE="${KEEP_FAILED_RELEASE:-0}"
ALLOW_DIRTY="${ALLOW_DIRTY:-0}"

usage() {
  cat <<'USAGE'
AI Genesis candidate build tooling

Usage:
  bash ai_genesis_candidate_build.sh --help
  bash ai_genesis_candidate_build.sh [candidate-build options via environment variables]

Safety guardrails:
  - Candidate-only validation; no production cutover.
  - Does not change /opt/ai-vafox/current-enterprise-ai.
  - Requires current-enterprise-ai -> releases/fba3c17 before candidate build execution.
  - No production data migration is performed by this script.

Common environment variables:
  PROD_ROOT=/opt/ai-vafox
  EXPECTED_CURRENT_TARGET=releases/fba3c17
  PREVIEW_HOST=127.0.0.1
  PREVIEW_PORT=18086
  KEEP_RUNTIME=0
USAGE
}

if [ "${1:-}" = "--help" ] || [ "${1:-}" = "-h" ]; then
  usage
  exit 0
fi

BUILD_TIME_UTC="$(date -u +%Y%m%d-%H%M%S)"
BUILD_ISO_UTC="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
GIT_COMMIT="$(git -C "${SOURCE_REPO}" rev-parse HEAD)"
SHORT_COMMIT="$(git -C "${SOURCE_REPO}" rev-parse --short HEAD)"
CANDIDATE_ID="${CANDIDATE_ID:-ai-genesis-rc-${BUILD_TIME_UTC}-${SHORT_COMMIT}}"
RELEASE_DIR="${RELEASE_DIR:-${RELEASES_DIR}/${CANDIDATE_ID}}"
EVIDENCE_DIR="${RELEASE_DIR}/evidence"
LOG_DIR="${RELEASE_DIR}/logs"
REPORT_PATH="${REPORT_PATH:-${SOURCE_REPO}/AI_GENESIS_CANDIDATE_VALIDATION_REPORT.md}"
PREVIEW_PID=""
FAILED=0

log() { printf '[%s] %s\n' "$(date -u +%H:%M:%S)" "$*" | tee -a "${EVIDENCE_DIR:-/tmp}/execution.log"; }
run() { log "+ $*"; "$@" 2>&1 | tee -a "${EVIDENCE_DIR}/execution.log"; }
record_result() {
  local area="$1" status="$2" evidence="$3" notes="$4"
  printf '%s|%s|%s|%s\n' "$area" "$status" "$evidence" "$notes" >> "${EVIDENCE_DIR}/validation_results.psv"
}

current_target() {
  if [ -L "${CURRENT_SYMLINK}" ]; then readlink "${CURRENT_SYMLINK}"; else printf '__missing__'; fi
}

assert_production_pointer() {
  local actual
  actual="$(current_target)"
  if [ "${actual}" != "${EXPECTED_CURRENT_TARGET}" ]; then
    echo "Production guard failed: ${CURRENT_SYMLINK} -> ${actual}, expected ${EXPECTED_CURRENT_TARGET}" >&2
    exit 10
  fi
}

cleanup() {
  local exit_code=$?
  set +e
  if [ -n "${PREVIEW_PID}" ] && kill -0 "${PREVIEW_PID}" 2>/dev/null; then
    kill "${PREVIEW_PID}" 2>/dev/null || true
    wait "${PREVIEW_PID}" 2>/dev/null || true
  fi
  if [ -n "${RELEASE_DIR:-}" ] && [ "${FAILED}" = "1" ] && [ "${KEEP_FAILED_RELEASE}" != "1" ]; then
    rm -rf "${RELEASE_DIR}/runtime"
  fi
  if [ -n "${CURRENT_SYMLINK:-}" ] && [ -e "${CURRENT_SYMLINK}" ]; then
    local after
    after="$(current_target)"
    if [ "${after}" != "${EXPECTED_CURRENT_TARGET}" ]; then
      echo "CRITICAL: production pointer changed to ${after}; refusing further cleanup" >&2
      exit 99
    fi
  fi
  exit "${exit_code}"
}
trap cleanup EXIT
trap 'FAILED=1; log "Failure on line ${LINENO}"; generate_report failed || true' ERR

write_nginx_preview() {
  cat > "${RELEASE_DIR}/nginx-preview/ai-genesis-preview.conf" <<NGINX
# Preview-only location. Do not replace production server blocks or current symlink.
location /__preview/ai-genesis/${CANDIDATE_ID}/ {
    proxy_pass http://${PREVIEW_HOST}:${PREVIEW_PORT}/;
    proxy_set_header Host ${TARGET_DOMAIN};
    proxy_set_header X-Release-Candidate ${CANDIDATE_ID};
    proxy_set_header X-Production-Pointer ${EXPECTED_CURRENT_TARGET};
}
NGINX
}

generate_manifest() {
  python - "${RELEASE_DIR}" "${CANDIDATE_ID}" "${RC_VERSION}" "${TARGET_DOMAIN}" "${GIT_COMMIT}" "${BUILD_ISO_UTC}" "${EXPECTED_CURRENT_TARGET}" "${PREVIEW_PORT}" <<'PY'
import hashlib, json, os, sys
release_dir, candidate_id, version, target, commit, built_at, expected, port = sys.argv[1:]
services = ["auth", "agents", "knowledge", "workflows", "wecom", "api", "nginx-preview"]
manifest = {
    "version": version,
    "candidate_id": candidate_id,
    "target": target,
    "current_production": f"current-enterprise-ai -> {expected}",
    "commit": commit,
    "build_time_utc": built_at,
    "mode": "release_candidate_only",
    "guardrails": ["no production cutover", "no current symlink change", "no data migration"],
    "services": [{"name": name, "artifact": ("nginx-preview/ai-genesis-preview.conf" if name == "nginx-preview" else f"apps/ai/{name}"), "port_or_socket": ("preview-only" if name == "nginx-preview" else f"127.0.0.1:{port}")} for name in services],
}
entries = []
for root, dirs, files in os.walk(release_dir):
    dirs[:] = [d for d in dirs if d not in {"logs", "evidence", "runtime", ".git"}]
    for file_name in files:
        rel = os.path.relpath(os.path.join(root, file_name), release_dir)
        if rel in {"RELEASE_MANIFEST.json", "RELEASE_MANIFEST.json.sha256", "checksums.sha256"}:
            continue
        h = hashlib.sha256()
        with open(os.path.join(root, file_name), "rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                h.update(chunk)
        entries.append((rel, h.hexdigest()))
tree_hash = hashlib.sha256("\n".join(f"{digest}  {rel}" for rel, digest in sorted(entries)).encode()).hexdigest()
manifest["checksum"] = f"sha256:{tree_hash}"
manifest["checksums"] = {"release_tree": f"sha256:{tree_hash}"}
with open(os.path.join(release_dir, "RELEASE_MANIFEST.json"), "w", encoding="utf-8") as handle:
    json.dump(manifest, handle, indent=2, ensure_ascii=False)
    handle.write("\n")
PY
  (cd "${RELEASE_DIR}" && find . -type f ! -path './logs/*' ! -path './evidence/*' ! -path './runtime/*' ! -name 'checksums.sha256' -print0 | sort -z | xargs -0 sha256sum > checksums.sha256)
  (cd "${RELEASE_DIR}" && sha256sum RELEASE_MANIFEST.json > RELEASE_MANIFEST.json.sha256)
}

smoke() {
  local name="$1" url="$2" expect="$3" evidence="${EVIDENCE_DIR}/smoke-${name}.log"
  local code
  code="$(curl -sS -o "${evidence}.body" -w '%{http_code}' "${url}" || true)"
  printf 'url=%s\nstatus=%s\nexpected=%s\n' "${url}" "${code}" "${expect}" > "${evidence}"
  if [[ "${code}" =~ ${expect} ]]; then record_result "$name" PASS "$evidence" "HTTP ${code}"; else FAILED=1; record_result "$name" FAIL "$evidence" "HTTP ${code}"; fi
}

generate_report() {
  local overall="${1:-completed}"
  python - "${REPORT_PATH}" "${CANDIDATE_ID}" "${TARGET_DOMAIN}" "${EXPECTED_CURRENT_TARGET}" "${GIT_COMMIT}" "${RELEASE_DIR}" "${overall}" "${EVIDENCE_DIR}/validation_results.psv" <<'PY'
import datetime, pathlib, sys
report, candidate, target, expected, commit, release, overall, results = sys.argv[1:]
rows = []
path = pathlib.Path(results)
if path.exists():
    for line in path.read_text().splitlines():
        rows.append(line.split('|', 3))
status = "PASS" if overall == "completed" and all(r[1] == "PASS" for r in rows) else "FAIL"
lines = [
    "# AI Genesis Candidate Validation Report", "",
    f"Generated UTC: `{datetime.datetime.utcnow().replace(microsecond=0).isoformat()}Z`", f"Target: `{target}`", f"Candidate ID: `{candidate}`", f"Release directory: `{release}`", f"Commit: `{commit}`", f"Current production pointer required: `current-enterprise-ai -> {expected}`", f"Overall status: **{status}**", "",
    "## Guardrails", "", "- No production cutover performed.", "- No current symlink change performed.", "- No data migration performed.", "- Preview runtime is candidate-scoped only.", "",
    "## Validation Results", "", "| Area | Status | Evidence | Notes |", "|---|---|---|---|",
]
for area, result, evidence, notes in rows:
    lines.append(f"| {area} | {result} | `{evidence}` | {notes} |")
lines += ["", "## Cleanup", "", "Preview process is stopped automatically unless `KEEP_RUNTIME=1` is set. Failed runtime scratch data is removed unless `KEEP_FAILED_RELEASE=1` is set.", ""]
pathlib.Path(report).write_text("\n".join(lines), encoding="utf-8")
PY
}

main() {
  mkdir -p "${EVIDENCE_DIR}" "${LOG_DIR}" "${RELEASE_DIR}/nginx-preview"
  : > "${EVIDENCE_DIR}/validation_results.psv"
  assert_production_pointer
  record_result "Production pointer unchanged (pre)" PASS "${EVIDENCE_DIR}/execution.log" "$(current_target)"

  if [ "${ALLOW_DIRTY}" != "1" ] && [ -n "$(git -C "${SOURCE_REPO}" status --short)" ]; then
    echo "Working tree is not clean. Commit or stash changes, or set ALLOW_DIRTY=1 for local rehearsal." >&2
    exit 11
  fi
  git -C "${SOURCE_REPO}" archive --format=tar HEAD | tar -x -C "${RELEASE_DIR}"
  record_result "Source preparation" PASS "${EVIDENCE_DIR}/execution.log" "archived ${GIT_COMMIT}"

  write_nginx_preview
  run python -m compileall "${RELEASE_DIR}/apps" "${RELEASE_DIR}/foxbrain_os" "${RELEASE_DIR}/tests"
  record_result "Build process" PASS "${EVIDENCE_DIR}/execution.log" "python compileall completed"

  generate_manifest
  run python -m json.tool "${RELEASE_DIR}/RELEASE_MANIFEST.json"
  run sha256sum -c "${RELEASE_DIR}/RELEASE_MANIFEST.json.sha256"
  record_result "RELEASE_MANIFEST.json" PASS "${RELEASE_DIR}/RELEASE_MANIFEST.json" "manifest and SHA256 generated"

  (cd "${RELEASE_DIR}" && PYTHONPATH="${RELEASE_DIR}" FOXBRAIN_ENV=release_candidate APP_ENV=release_candidate RELEASE_ID="${CANDIDATE_ID}" WECOM_MODE=dry_run python -m flask --app apps.ai.app run --host "${PREVIEW_HOST}" --port "${PREVIEW_PORT}" > "${LOG_DIR}/preview-runtime.log" 2>&1) &
  PREVIEW_PID=$!
  sleep 3
  if ! kill -0 "${PREVIEW_PID}" 2>/dev/null; then FAILED=1; record_result "Preview runtime startup" FAIL "${LOG_DIR}/preview-runtime.log" "process exited"; generate_report failed; exit 12; fi
  record_result "Preview runtime startup" PASS "${LOG_DIR}/preview-runtime.log" "pid ${PREVIEW_PID}, ${PREVIEW_HOST}:${PREVIEW_PORT}"

  smoke "login" "http://${PREVIEW_HOST}:${PREVIEW_PORT}/login" '^(200|302)$'
  smoke "auth" "http://${PREVIEW_HOST}:${PREVIEW_PORT}/ops-api/identity/me" '^(401|403|302)$'
  smoke "agents" "http://${PREVIEW_HOST}:${PREVIEW_PORT}/agents" '^(200|302)$'
  smoke "knowledge" "http://${PREVIEW_HOST}:${PREVIEW_PORT}/knowledge" '^(200|302)$'
  smoke "workflows" "http://${PREVIEW_HOST}:${PREVIEW_PORT}/tasks" '^(200|302)$'
  smoke "WeCom" "http://${PREVIEW_HOST}:${PREVIEW_PORT}/wecom" '^(200|302)$'
  smoke "API" "http://${PREVIEW_HOST}:${PREVIEW_PORT}/health/version" '^(200|503)$'
  smoke "nginx preview" "http://${PREVIEW_HOST}:${PREVIEW_PORT}/" '^(200|302)$'
  assert_production_pointer
  record_result "Production pointer unchanged (post)" PASS "${EVIDENCE_DIR}/execution.log" "$(current_target)"

  generate_report completed
  if [ "${FAILED}" = "1" ]; then exit 20; fi
  if [ "${KEEP_RUNTIME}" != "1" ]; then kill "${PREVIEW_PID}" 2>/dev/null || true; wait "${PREVIEW_PID}" 2>/dev/null || true; PREVIEW_PID=""; fi
  log "Candidate validation report: ${REPORT_PATH}"
}

main "$@"
