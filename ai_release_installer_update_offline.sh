#!/usr/bin/env bash
set -Eeuo pipefail

# Offline updater for /opt/ai-vafox/ops/ai_release_tooling_installer.sh.
# Safe to run directly on ai.vafox.com when SSH delivery is unavailable.
# This script does not use ssh, git, docker, nginx, database tooling, or release cutover commands.

PROD_ROOT="${PROD_ROOT:-/opt/ai-vafox}"
OPS_DIR="${OPS_DIR:-${PROD_ROOT}/ops}"
INSTALLER_PATH="${INSTALLER_PATH:-${OPS_DIR}/ai_release_tooling_installer.sh}"
BACKUP_PATH="${BACKUP_PATH:-${INSTALLER_PATH}.backup}"
CURRENT_LINK="${CURRENT_LINK:-${PROD_ROOT}/current-enterprise-ai}"
EXPECTED_POINTER="${EXPECTED_POINTER:-${PROD_ROOT}/releases/fba3c17}"
REPORT_PATH="${REPORT_PATH:-AI_RELEASE_INSTALLER_OFFLINE_UPDATE_REPORT.md}"
EXPECTED_INSTALLER_SHA256="2df33663d8ae93b804ac0c6ffdfe99a72d2f5314e1ffb78442e5ee8afdcf4e44"
TMP_INSTALLER=""
POINTER_BEFORE=""
POINTER_AFTER=""
VALIDATION_RESULT="NOT_RUN"
HELP_RESULT="NOT_RUN"
CHECKSUM_RESULT="NOT_RUN"
BACKUP_RESULT="NOT_RUN"
UPDATE_RESULT="NOT_RUN"

log() { printf '[%s] %s
' "$(date -u +%H:%M:%S)" "$*"; }
fail() { echo "ERROR: $*" >&2; write_report "FAIL"; exit 1; }

cleanup() {
  if [ -n "${TMP_INSTALLER}" ] && [ -e "${TMP_INSTALLER}" ]; then
    rm -f "${TMP_INSTALLER}"
  fi
}
trap cleanup EXIT

pointer_target() {
  if [ -e "${CURRENT_LINK}" ] || [ -L "${CURRENT_LINK}" ]; then
    readlink -f "${CURRENT_LINK}"
  else
    printf '__missing__'
  fi
}

release_count() {
  if [ -d "${PROD_ROOT}/releases" ]; then
    find "${PROD_ROOT}/releases" -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' '
  else
    printf '0'
  fi
}

write_payload() {
  TMP_INSTALLER="$(mktemp "${TMPDIR:-/tmp}/ai_release_tooling_installer.fixed.XXXXXX")"
  cat > "${TMP_INSTALLER}" <<'INSTALLER_PAYLOAD'
#!/usr/bin/env bash
set -Eeuo pipefail

# Offline installer for AI release tooling on ai.vafox.com production.
# Installer-only safety: no cutover, no data change, no Docker restart, no symlink change.

TARGET_DOMAIN="${TARGET_DOMAIN:-ai.vafox.com}"
PROD_ROOT="${PROD_ROOT:-/opt/ai-vafox}"
OPS_DIR="${OPS_DIR:-${PROD_ROOT}/ops}"
TOOL_NAME="ai_genesis_candidate_build.sh"
TOOL_PATH="${OPS_DIR}/${TOOL_NAME}"
EXPECTED_CURRENT_TARGET="${EXPECTED_CURRENT_TARGET:-${PROD_ROOT}/releases/fba3c17}"
EXPECTED_SHA256="bdf1cc6a878e10b66d98edf26a79ad675403c0411020d053b97423452628ed6b"
TMP_FILE=""

log() { printf '[%s] %s\n' "$(date -u +%H:%M:%S)" "$*"; }
fail() { echo "ERROR: $*" >&2; exit 1; }
run() { log "+ $*"; "$@"; }

cleanup() {
  if [ -n "${TMP_FILE}" ] && [ -e "${TMP_FILE}" ]; then
    rm -f "${TMP_FILE}"
  fi
}
trap cleanup EXIT

usage() {
  cat <<'USAGE'
AI release tooling installer

Usage:
  bash ai_release_tooling_installer.sh --help
  bash ai_release_tooling_installer.sh

Installs the AI Genesis candidate build tooling into the production ops directory.
The --help path only displays this text and does not install payloads, create
release candidates, change symlinks, restart services, alter nginx, or touch data.

Safety guard:
  Requires current-enterprise-ai to resolve to ${PROD_ROOT}/releases/fba3c17.
USAGE
}

if [ "${1:-}" = "--help" ] || [ "${1:-}" = "-h" ]; then
  usage
  exit 0
fi

current_target() {
  if [ -L "${PROD_ROOT}/current-enterprise-ai" ]; then
    readlink -f "${PROD_ROOT}/current-enterprise-ai"
  else
    printf '__missing__'
  fi
}

verify_pointer() {
  local actual
  actual="$(current_target)"
  if [ "${actual}" != "${EXPECTED_CURRENT_TARGET}" ]; then
    fail "production pointer guard failed: ${PROD_ROOT}/current-enterprise-ai -> ${actual}, expected ${EXPECTED_CURRENT_TARGET}"
  fi
  log "production pointer verified: current-enterprise-ai -> ${actual}"
}

write_tool_payload() {
  TMP_FILE="$(mktemp "${TMPDIR:-/tmp}/ai_genesis_candidate_build.XXXXXX")"
  base64 -d > "${TMP_FILE}" <<'PAYLOAD_BASE64'
IyEvdXNyL2Jpbi9lbnYgYmFzaApzZXQgLUVldW8gcGlwZWZhaWwKCiMgQUkgR2VuZXNpcyByZWxl
YXNlLWNhbmRpZGF0ZSBidWlsZCBleGVjdXRvciBmb3IgYWkudmFmb3guY29tLgojIFRoaXMgc2Ny
aXB0IGNyZWF0ZXMsIGJ1aWxkcywgc3RhcnRzLCB2YWxpZGF0ZXMsIHJlcG9ydHMsIGFuZCBjbGVh
bnMgdXAgYW4KIyBpc29sYXRlZCBjYW5kaWRhdGUgcnVudGltZS4gSXQgbmV2ZXIgY2hhbmdlcyB0
aGUgcHJvZHVjdGlvbiBjdXJyZW50IHN5bWxpbmsuCgpUQVJHRVRfRE9NQUlOPSIke1RBUkdFVF9E
T01BSU46LWFpLnZhZm94LmNvbX0iClJDX1ZFUlNJT049IiR7UkNfVkVSU0lPTjotQUktT1MtVjYt
Q0xFQU4tUkVCVUlMRC1WMS1SQ30iClBST0RfUk9PVD0iJHtQUk9EX1JPT1Q6LS9vcHQvYWktdmFm
b3h9IgpTT1VSQ0VfUkVQTz0iJHtTT1VSQ0VfUkVQTzotJChnaXQgcmV2LXBhcnNlIC0tc2hvdy10
b3BsZXZlbCAyPi9kZXYvbnVsbCl9IgpSRUxFQVNFU19ESVI9IiR7UkVMRUFTRVNfRElSOi0ke1BS
T0RfUk9PVH0vcmVsZWFzZXN9IgpDVVJSRU5UX1NZTUxJTks9IiR7Q1VSUkVOVF9TWU1MSU5LOi0k
e1BST0RfUk9PVH0vY3VycmVudC1lbnRlcnByaXNlLWFpfSIKRVhQRUNURURfQ1VSUkVOVF9UQVJH
RVQ9IiR7RVhQRUNURURfQ1VSUkVOVF9UQVJHRVQ6LSR7UFJPRF9ST09UfS9yZWxlYXNlcy9mYmEz
YzE3fSIKUFJFVklFV19IT1NUPSIke1BSRVZJRVdfSE9TVDotMTI3LjAuMC4xfSIKUFJFVklFV19Q
T1JUPSIke1BSRVZJRVdfUE9SVDotMTgwODZ9IgpLRUVQX1JVTlRJTUU9IiR7S0VFUF9SVU5USU1F
Oi0wfSIKS0VFUF9GQUlMRURfUkVMRUFTRT0iJHtLRUVQX0ZBSUxFRF9SRUxFQVNFOi0wfSIKQUxM
T1dfRElSVFk9IiR7QUxMT1dfRElSVFk6LTB9IgoKdXNhZ2UoKSB7CiAgY2F0IDw8J1VTQUdFJwpB
SSBHZW5lc2lzIGNhbmRpZGF0ZSBidWlsZCB0b29saW5nCgpVc2FnZToKICBiYXNoIGFpX2dlbmVz
aXNfY2FuZGlkYXRlX2J1aWxkLnNoIC0taGVscAogIGJhc2ggYWlfZ2VuZXNpc19jYW5kaWRhdGVf
YnVpbGQuc2ggW2NhbmRpZGF0ZS1idWlsZCBvcHRpb25zIHZpYSBlbnZpcm9ubWVudCB2YXJpYWJs
ZXNdCgpTYWZldHkgZ3VhcmRyYWlsczoKICAtIENhbmRpZGF0ZS1vbmx5IHZhbGlkYXRpb247IG5v
IHByb2R1Y3Rpb24gY3V0b3Zlci4KICAtIERvZXMgbm90IGNoYW5nZSAvb3B0L2FpLXZhZm94L2N1
cnJlbnQtZW50ZXJwcmlzZS1haS4KICAtIFJlcXVpcmVzIGN1cnJlbnQtZW50ZXJwcmlzZS1haSAt
PiByZWxlYXNlcy9mYmEzYzE3IGJlZm9yZSBjYW5kaWRhdGUgYnVpbGQgZXhlY3V0aW9uLgogIC0g
Tm8gcHJvZHVjdGlvbiBkYXRhIG1pZ3JhdGlvbiBpcyBwZXJmb3JtZWQgYnkgdGhpcyBzY3JpcHQu
CgpDb21tb24gZW52aXJvbm1lbnQgdmFyaWFibGVzOgogIFBST0RfUk9PVD0vb3B0L2FpLXZhZm94
CiAgRVhQRUNURURfQ1VSUkVOVF9UQVJHRVQ9L29wdC9haS12YWZveC9yZWxlYXNlcy9mYmEzYzE3
CiAgUFJFVklFV19IT1NUPTEyNy4wLjAuMQogIFBSRVZJRVdfUE9SVD0xODA4NgogIEtFRVBfUlVO
VElNRT0wClVTQUdFCn0KCmlmIFsgIiR7MTotfSIgPSAiLS1oZWxwIiBdIHx8IFsgIiR7MTotfSIg
PSAiLWgiIF07IHRoZW4KICB1c2FnZQogIGV4aXQgMApmaQoKQlVJTERfVElNRV9VVEM9IiQoZGF0
ZSAtdSArJVklbSVkLSVIJU0lUykiCkJVSUxEX0lTT19VVEM9IiQoZGF0ZSAtdSArJVktJW0tJWRU
JUg6JU06JVNaKSIKR0lUX0NPTU1JVD0iJChnaXQgLUMgIiR7U09VUkNFX1JFUE99IiByZXYtcGFy
c2UgSEVBRCkiClNIT1JUX0NPTU1JVD0iJChnaXQgLUMgIiR7U09VUkNFX1JFUE99IiByZXYtcGFy
c2UgLS1zaG9ydCBIRUFEKSIKQ0FORElEQVRFX0lEPSIke0NBTkRJREFURV9JRDotYWktZ2VuZXNp
cy1yYy0ke0JVSUxEX1RJTUVfVVRDfS0ke1NIT1JUX0NPTU1JVH19IgpSRUxFQVNFX0RJUj0iJHtS
RUxFQVNFX0RJUjotJHtSRUxFQVNFU19ESVJ9LyR7Q0FORElEQVRFX0lEfX0iCkVWSURFTkNFX0RJ
Uj0iJHtSRUxFQVNFX0RJUn0vZXZpZGVuY2UiCkxPR19ESVI9IiR7UkVMRUFTRV9ESVJ9L2xvZ3Mi
ClJFUE9SVF9QQVRIPSIke1JFUE9SVF9QQVRIOi0ke1NPVVJDRV9SRVBPfS9BSV9HRU5FU0lTX0NB
TkRJREFURV9WQUxJREFUSU9OX1JFUE9SVC5tZH0iClBSRVZJRVdfUElEPSIiCkZBSUxFRD0wCgps
b2coKSB7IHByaW50ZiAnWyVzXSAlc1xuJyAiJChkYXRlIC11ICslSDolTTolUykiICIkKiIgfCB0
ZWUgLWEgIiR7RVZJREVOQ0VfRElSOi0vdG1wfS9leGVjdXRpb24ubG9nIjsgfQpydW4oKSB7IGxv
ZyAiKyAkKiI7ICIkQCIgMj4mMSB8IHRlZSAtYSAiJHtFVklERU5DRV9ESVJ9L2V4ZWN1dGlvbi5s
b2ciOyB9CnJlY29yZF9yZXN1bHQoKSB7CiAgbG9jYWwgYXJlYT0iJDEiIHN0YXR1cz0iJDIiIGV2
aWRlbmNlPSIkMyIgbm90ZXM9IiQ0IgogIHByaW50ZiAnJXN8JXN8JXN8JXNcbicgIiRhcmVhIiAi
JHN0YXR1cyIgIiRldmlkZW5jZSIgIiRub3RlcyIgPj4gIiR7RVZJREVOQ0VfRElSfS92YWxpZGF0
aW9uX3Jlc3VsdHMucHN2Igp9CgpjdXJyZW50X3RhcmdldCgpIHsKICBpZiBbIC1MICIke0NVUlJF
TlRfU1lNTElOS30iIF07IHRoZW4gcmVhZGxpbmsgLWYgIiR7Q1VSUkVOVF9TWU1MSU5LfSI7IGVs
c2UgcHJpbnRmICdfX21pc3NpbmdfXyc7IGZpCn0KCmFzc2VydF9wcm9kdWN0aW9uX3BvaW50ZXIo
KSB7CiAgbG9jYWwgYWN0dWFsCiAgYWN0dWFsPSIkKGN1cnJlbnRfdGFyZ2V0KSIKICBpZiBbICIk
e2FjdHVhbH0iICE9ICIke0VYUEVDVEVEX0NVUlJFTlRfVEFSR0VUfSIgXTsgdGhlbgogICAgZWNo
byAiUHJvZHVjdGlvbiBndWFyZCBmYWlsZWQ6ICR7Q1VSUkVOVF9TWU1MSU5LfSAtPiAke2FjdHVh
bH0sIGV4cGVjdGVkICR7RVhQRUNURURfQ1VSUkVOVF9UQVJHRVR9IiA+JjIKICAgIGV4aXQgMTAK
ICBmaQp9CgpjbGVhbnVwKCkgewogIGxvY2FsIGV4aXRfY29kZT0kPwogIHNldCArZQogIGlmIFsg
LW4gIiR7UFJFVklFV19QSUR9IiBdICYmIGtpbGwgLTAgIiR7UFJFVklFV19QSUR9IiAyPi9kZXYv
bnVsbDsgdGhlbgogICAga2lsbCAiJHtQUkVWSUVXX1BJRH0iIDI+L2Rldi9udWxsIHx8IHRydWUK
ICAgIHdhaXQgIiR7UFJFVklFV19QSUR9IiAyPi9kZXYvbnVsbCB8fCB0cnVlCiAgZmkKICBpZiBb
IC1uICIke1JFTEVBU0VfRElSOi19IiBdICYmIFsgIiR7RkFJTEVEfSIgPSAiMSIgXSAmJiBbICIk
e0tFRVBfRkFJTEVEX1JFTEVBU0V9IiAhPSAiMSIgXTsgdGhlbgogICAgcm0gLXJmICIke1JFTEVB
U0VfRElSfS9ydW50aW1lIgogIGZpCiAgaWYgWyAtbiAiJHtDVVJSRU5UX1NZTUxJTks6LX0iIF0g
JiYgWyAtZSAiJHtDVVJSRU5UX1NZTUxJTkt9IiBdOyB0aGVuCiAgICBsb2NhbCBhZnRlcgogICAg
YWZ0ZXI9IiQoY3VycmVudF90YXJnZXQpIgogICAgaWYgWyAiJHthZnRlcn0iICE9ICIke0VYUEVD
VEVEX0NVUlJFTlRfVEFSR0VUfSIgXTsgdGhlbgogICAgICBlY2hvICJDUklUSUNBTDogcHJvZHVj
dGlvbiBwb2ludGVyIGNoYW5nZWQgdG8gJHthZnRlcn07IHJlZnVzaW5nIGZ1cnRoZXIgY2xlYW51
cCIgPiYyCiAgICAgIGV4aXQgOTkKICAgIGZpCiAgZmkKICBleGl0ICIke2V4aXRfY29kZX0iCn0K
dHJhcCBjbGVhbnVwIEVYSVQKdHJhcCAnRkFJTEVEPTE7IGxvZyAiRmFpbHVyZSBvbiBsaW5lICR7
TElORU5PfSI7IGdlbmVyYXRlX3JlcG9ydCBmYWlsZWQgfHwgdHJ1ZScgRVJSCgp3cml0ZV9uZ2lu
eF9wcmV2aWV3KCkgewogIGNhdCA+ICIke1JFTEVBU0VfRElSfS9uZ2lueC1wcmV2aWV3L2FpLWdl
bmVzaXMtcHJldmlldy5jb25mIiA8PE5HSU5YCiMgUHJldmlldy1vbmx5IGxvY2F0aW9uLiBEbyBu
b3QgcmVwbGFjZSBwcm9kdWN0aW9uIHNlcnZlciBibG9ja3Mgb3IgY3VycmVudCBzeW1saW5rLgps
b2NhdGlvbiAvX19wcmV2aWV3L2FpLWdlbmVzaXMvJHtDQU5ESURBVEVfSUR9LyB7CiAgICBwcm94
eV9wYXNzIGh0dHA6Ly8ke1BSRVZJRVdfSE9TVH06JHtQUkVWSUVXX1BPUlR9LzsKICAgIHByb3h5
X3NldF9oZWFkZXIgSG9zdCAke1RBUkdFVF9ET01BSU59OwogICAgcHJveHlfc2V0X2hlYWRlciBY
LVJlbGVhc2UtQ2FuZGlkYXRlICR7Q0FORElEQVRFX0lEfTsKICAgIHByb3h5X3NldF9oZWFkZXIg
WC1Qcm9kdWN0aW9uLVBvaW50ZXIgJHtFWFBFQ1RFRF9DVVJSRU5UX1RBUkdFVH07Cn0KTkdJTlgK
fQoKZ2VuZXJhdGVfbWFuaWZlc3QoKSB7CiAgcHl0aG9uIC0gIiR7UkVMRUFTRV9ESVJ9IiAiJHtD
QU5ESURBVEVfSUR9IiAiJHtSQ19WRVJTSU9OfSIgIiR7VEFSR0VUX0RPTUFJTn0iICIke0dJVF9D
T01NSVR9IiAiJHtCVUlMRF9JU09fVVRDfSIgIiR7RVhQRUNURURfQ1VSUkVOVF9UQVJHRVR9IiAi
JHtQUkVWSUVXX1BPUlR9IiA8PCdQWScKaW1wb3J0IGhhc2hsaWIsIGpzb24sIG9zLCBzeXMKcmVs
ZWFzZV9kaXIsIGNhbmRpZGF0ZV9pZCwgdmVyc2lvbiwgdGFyZ2V0LCBjb21taXQsIGJ1aWx0X2F0
LCBleHBlY3RlZCwgcG9ydCA9IHN5cy5hcmd2WzE6XQpzZXJ2aWNlcyA9IFsiYXV0aCIsICJhZ2Vu
dHMiLCAia25vd2xlZGdlIiwgIndvcmtmbG93cyIsICJ3ZWNvbSIsICJhcGkiLCAibmdpbngtcHJl
dmlldyJdCm1hbmlmZXN0ID0gewogICAgInZlcnNpb24iOiB2ZXJzaW9uLAogICAgImNhbmRpZGF0
ZV9pZCI6IGNhbmRpZGF0ZV9pZCwKICAgICJ0YXJnZXQiOiB0YXJnZXQsCiAgICAiY3VycmVudF9w
cm9kdWN0aW9uIjogZiJjdXJyZW50LWVudGVycHJpc2UtYWkgLT4ge2V4cGVjdGVkfSIsCiAgICAi
Y29tbWl0IjogY29tbWl0LAogICAgImJ1aWxkX3RpbWVfdXRjIjogYnVpbHRfYXQsCiAgICAibW9k
ZSI6ICJyZWxlYXNlX2NhbmRpZGF0ZV9vbmx5IiwKICAgICJndWFyZHJhaWxzIjogWyJubyBwcm9k
dWN0aW9uIGN1dG92ZXIiLCAibm8gY3VycmVudCBzeW1saW5rIGNoYW5nZSIsICJubyBkYXRhIG1p
Z3JhdGlvbiJdLAogICAgInNlcnZpY2VzIjogW3sibmFtZSI6IG5hbWUsICJhcnRpZmFjdCI6ICgi
bmdpbngtcHJldmlldy9haS1nZW5lc2lzLXByZXZpZXcuY29uZiIgaWYgbmFtZSA9PSAibmdpbngt
cHJldmlldyIgZWxzZSBmImFwcHMvYWkve25hbWV9IiksICJwb3J0X29yX3NvY2tldCI6ICgicHJl
dmlldy1vbmx5IiBpZiBuYW1lID09ICJuZ2lueC1wcmV2aWV3IiBlbHNlIGYiMTI3LjAuMC4xOntw
b3J0fSIpfSBmb3IgbmFtZSBpbiBzZXJ2aWNlc10sCn0KZW50cmllcyA9IFtdCmZvciByb290LCBk
aXJzLCBmaWxlcyBpbiBvcy53YWxrKHJlbGVhc2VfZGlyKToKICAgIGRpcnNbOl0gPSBbZCBmb3Ig
ZCBpbiBkaXJzIGlmIGQgbm90IGluIHsibG9ncyIsICJldmlkZW5jZSIsICJydW50aW1lIiwgIi5n
aXQifV0KICAgIGZvciBmaWxlX25hbWUgaW4gZmlsZXM6CiAgICAgICAgcmVsID0gb3MucGF0aC5y
ZWxwYXRoKG9zLnBhdGguam9pbihyb290LCBmaWxlX25hbWUpLCByZWxlYXNlX2RpcikKICAgICAg
ICBpZiByZWwgaW4geyJSRUxFQVNFX01BTklGRVNULmpzb24iLCAiUkVMRUFTRV9NQU5JRkVTVC5q
c29uLnNoYTI1NiIsICJjaGVja3N1bXMuc2hhMjU2In06CiAgICAgICAgICAgIGNvbnRpbnVlCiAg
ICAgICAgaCA9IGhhc2hsaWIuc2hhMjU2KCkKICAgICAgICB3aXRoIG9wZW4ob3MucGF0aC5qb2lu
KHJvb3QsIGZpbGVfbmFtZSksICJyYiIpIGFzIGhhbmRsZToKICAgICAgICAgICAgZm9yIGNodW5r
IGluIGl0ZXIobGFtYmRhOiBoYW5kbGUucmVhZCgxMDI0ICogMTAyNCksIGIiIik6CiAgICAgICAg
ICAgICAgICBoLnVwZGF0ZShjaHVuaykKICAgICAgICBlbnRyaWVzLmFwcGVuZCgocmVsLCBoLmhl
eGRpZ2VzdCgpKSkKdHJlZV9oYXNoID0gaGFzaGxpYi5zaGEyNTYoIlxuIi5qb2luKGYie2RpZ2Vz
dH0gIHtyZWx9IiBmb3IgcmVsLCBkaWdlc3QgaW4gc29ydGVkKGVudHJpZXMpKS5lbmNvZGUoKSku
aGV4ZGlnZXN0KCkKbWFuaWZlc3RbImNoZWNrc3VtIl0gPSBmInNoYTI1Njp7dHJlZV9oYXNofSIK
bWFuaWZlc3RbImNoZWNrc3VtcyJdID0geyJyZWxlYXNlX3RyZWUiOiBmInNoYTI1Njp7dHJlZV9o
YXNofSJ9CndpdGggb3Blbihvcy5wYXRoLmpvaW4ocmVsZWFzZV9kaXIsICJSRUxFQVNFX01BTklG
RVNULmpzb24iKSwgInciLCBlbmNvZGluZz0idXRmLTgiKSBhcyBoYW5kbGU6CiAgICBqc29uLmR1
bXAobWFuaWZlc3QsIGhhbmRsZSwgaW5kZW50PTIsIGVuc3VyZV9hc2NpaT1GYWxzZSkKICAgIGhh
bmRsZS53cml0ZSgiXG4iKQpQWQogIChjZCAiJHtSRUxFQVNFX0RJUn0iICYmIGZpbmQgLiAtdHlw
ZSBmICEgLXBhdGggJy4vbG9ncy8qJyAhIC1wYXRoICcuL2V2aWRlbmNlLyonICEgLXBhdGggJy4v
cnVudGltZS8qJyAhIC1uYW1lICdjaGVja3N1bXMuc2hhMjU2JyAtcHJpbnQwIHwgc29ydCAteiB8
IHhhcmdzIC0wIHNoYTI1NnN1bSA+IGNoZWNrc3Vtcy5zaGEyNTYpCiAgKGNkICIke1JFTEVBU0Vf
RElSfSIgJiYgc2hhMjU2c3VtIFJFTEVBU0VfTUFOSUZFU1QuanNvbiA+IFJFTEVBU0VfTUFOSUZF
U1QuanNvbi5zaGEyNTYpCn0KCnNtb2tlKCkgewogIGxvY2FsIG5hbWU9IiQxIiB1cmw9IiQyIiBl
eHBlY3Q9IiQzIiBldmlkZW5jZT0iJHtFVklERU5DRV9ESVJ9L3Ntb2tlLSR7bmFtZX0ubG9nIgog
IGxvY2FsIGNvZGUKICBjb2RlPSIkKGN1cmwgLXNTIC1vICIke2V2aWRlbmNlfS5ib2R5IiAtdyAn
JXtodHRwX2NvZGV9JyAiJHt1cmx9IiB8fCB0cnVlKSIKICBwcmludGYgJ3VybD0lc1xuc3RhdHVz
PSVzXG5leHBlY3RlZD0lc1xuJyAiJHt1cmx9IiAiJHtjb2RlfSIgIiR7ZXhwZWN0fSIgPiAiJHtl
dmlkZW5jZX0iCiAgaWYgW1sgIiR7Y29kZX0iID1+ICR7ZXhwZWN0fSBdXTsgdGhlbiByZWNvcmRf
cmVzdWx0ICIkbmFtZSIgUEFTUyAiJGV2aWRlbmNlIiAiSFRUUCAke2NvZGV9IjsgZWxzZSBGQUlM
RUQ9MTsgcmVjb3JkX3Jlc3VsdCAiJG5hbWUiIEZBSUwgIiRldmlkZW5jZSIgIkhUVFAgJHtjb2Rl
fSI7IGZpCn0KCmdlbmVyYXRlX3JlcG9ydCgpIHsKICBsb2NhbCBvdmVyYWxsPSIkezE6LWNvbXBs
ZXRlZH0iCiAgcHl0aG9uIC0gIiR7UkVQT1JUX1BBVEh9IiAiJHtDQU5ESURBVEVfSUR9IiAiJHtU
QVJHRVRfRE9NQUlOfSIgIiR7RVhQRUNURURfQ1VSUkVOVF9UQVJHRVR9IiAiJHtHSVRfQ09NTUlU
fSIgIiR7UkVMRUFTRV9ESVJ9IiAiJHtvdmVyYWxsfSIgIiR7RVZJREVOQ0VfRElSfS92YWxpZGF0
aW9uX3Jlc3VsdHMucHN2IiA8PCdQWScKaW1wb3J0IGRhdGV0aW1lLCBwYXRobGliLCBzeXMKcmVw
b3J0LCBjYW5kaWRhdGUsIHRhcmdldCwgZXhwZWN0ZWQsIGNvbW1pdCwgcmVsZWFzZSwgb3ZlcmFs
bCwgcmVzdWx0cyA9IHN5cy5hcmd2WzE6XQpyb3dzID0gW10KcGF0aCA9IHBhdGhsaWIuUGF0aChy
ZXN1bHRzKQppZiBwYXRoLmV4aXN0cygpOgogICAgZm9yIGxpbmUgaW4gcGF0aC5yZWFkX3RleHQo
KS5zcGxpdGxpbmVzKCk6CiAgICAgICAgcm93cy5hcHBlbmQobGluZS5zcGxpdCgnfCcsIDMpKQpz
dGF0dXMgPSAiUEFTUyIgaWYgb3ZlcmFsbCA9PSAiY29tcGxldGVkIiBhbmQgYWxsKHJbMV0gPT0g
IlBBU1MiIGZvciByIGluIHJvd3MpIGVsc2UgIkZBSUwiCmxpbmVzID0gWwogICAgIiMgQUkgR2Vu
ZXNpcyBDYW5kaWRhdGUgVmFsaWRhdGlvbiBSZXBvcnQiLCAiIiwKICAgIGYiR2VuZXJhdGVkIFVU
QzogYHtkYXRldGltZS5kYXRldGltZS51dGNub3coKS5yZXBsYWNlKG1pY3Jvc2Vjb25kPTApLmlz
b2Zvcm1hdCgpfVpgIiwgZiJUYXJnZXQ6IGB7dGFyZ2V0fWAiLCBmIkNhbmRpZGF0ZSBJRDogYHtj
YW5kaWRhdGV9YCIsIGYiUmVsZWFzZSBkaXJlY3Rvcnk6IGB7cmVsZWFzZX1gIiwgZiJDb21taXQ6
IGB7Y29tbWl0fWAiLCBmIkN1cnJlbnQgcHJvZHVjdGlvbiBwb2ludGVyIHJlcXVpcmVkOiBgY3Vy
cmVudC1lbnRlcnByaXNlLWFpIC0+IHtleHBlY3RlZH1gIiwgZiJPdmVyYWxsIHN0YXR1czogKip7
c3RhdHVzfSoqIiwgIiIsCiAgICAiIyMgR3VhcmRyYWlscyIsICIiLCAiLSBObyBwcm9kdWN0aW9u
IGN1dG92ZXIgcGVyZm9ybWVkLiIsICItIE5vIGN1cnJlbnQgc3ltbGluayBjaGFuZ2UgcGVyZm9y
bWVkLiIsICItIE5vIGRhdGEgbWlncmF0aW9uIHBlcmZvcm1lZC4iLCAiLSBQcmV2aWV3IHJ1bnRp
bWUgaXMgY2FuZGlkYXRlLXNjb3BlZCBvbmx5LiIsICIiLAogICAgIiMjIFZhbGlkYXRpb24gUmVz
dWx0cyIsICIiLCAifCBBcmVhIHwgU3RhdHVzIHwgRXZpZGVuY2UgfCBOb3RlcyB8IiwgInwtLS18
LS0tfC0tLXwtLS18IiwKXQpmb3IgYXJlYSwgcmVzdWx0LCBldmlkZW5jZSwgbm90ZXMgaW4gcm93
czoKICAgIGxpbmVzLmFwcGVuZChmInwge2FyZWF9IHwge3Jlc3VsdH0gfCBge2V2aWRlbmNlfWAg
fCB7bm90ZXN9IHwiKQpsaW5lcyArPSBbIiIsICIjIyBDbGVhbnVwIiwgIiIsICJQcmV2aWV3IHBy
b2Nlc3MgaXMgc3RvcHBlZCBhdXRvbWF0aWNhbGx5IHVubGVzcyBgS0VFUF9SVU5USU1FPTFgIGlz
IHNldC4gRmFpbGVkIHJ1bnRpbWUgc2NyYXRjaCBkYXRhIGlzIHJlbW92ZWQgdW5sZXNzIGBLRUVQ
X0ZBSUxFRF9SRUxFQVNFPTFgIGlzIHNldC4iLCAiIl0KcGF0aGxpYi5QYXRoKHJlcG9ydCkud3Jp
dGVfdGV4dCgiXG4iLmpvaW4obGluZXMpLCBlbmNvZGluZz0idXRmLTgiKQpQWQp9CgptYWluKCkg
ewogIG1rZGlyIC1wICIke0VWSURFTkNFX0RJUn0iICIke0xPR19ESVJ9IiAiJHtSRUxFQVNFX0RJ
Un0vbmdpbngtcHJldmlldyIKICA6ID4gIiR7RVZJREVOQ0VfRElSfS92YWxpZGF0aW9uX3Jlc3Vs
dHMucHN2IgogIGFzc2VydF9wcm9kdWN0aW9uX3BvaW50ZXIKICByZWNvcmRfcmVzdWx0ICJQcm9k
dWN0aW9uIHBvaW50ZXIgdW5jaGFuZ2VkIChwcmUpIiBQQVNTICIke0VWSURFTkNFX0RJUn0vZXhl
Y3V0aW9uLmxvZyIgIiQoY3VycmVudF90YXJnZXQpIgoKICBpZiBbICIke0FMTE9XX0RJUlRZfSIg
IT0gIjEiIF0gJiYgWyAtbiAiJChnaXQgLUMgIiR7U09VUkNFX1JFUE99IiBzdGF0dXMgLS1zaG9y
dCkiIF07IHRoZW4KICAgIGVjaG8gIldvcmtpbmcgdHJlZSBpcyBub3QgY2xlYW4uIENvbW1pdCBv
ciBzdGFzaCBjaGFuZ2VzLCBvciBzZXQgQUxMT1dfRElSVFk9MSBmb3IgbG9jYWwgcmVoZWFyc2Fs
LiIgPiYyCiAgICBleGl0IDExCiAgZmkKICBnaXQgLUMgIiR7U09VUkNFX1JFUE99IiBhcmNoaXZl
IC0tZm9ybWF0PXRhciBIRUFEIHwgdGFyIC14IC1DICIke1JFTEVBU0VfRElSfSIKICByZWNvcmRf
cmVzdWx0ICJTb3VyY2UgcHJlcGFyYXRpb24iIFBBU1MgIiR7RVZJREVOQ0VfRElSfS9leGVjdXRp
b24ubG9nIiAiYXJjaGl2ZWQgJHtHSVRfQ09NTUlUfSIKCiAgd3JpdGVfbmdpbnhfcHJldmlldwog
IHJ1biBweXRob24gLW0gY29tcGlsZWFsbCAiJHtSRUxFQVNFX0RJUn0vYXBwcyIgIiR7UkVMRUFT
RV9ESVJ9L2ZveGJyYWluX29zIiAiJHtSRUxFQVNFX0RJUn0vdGVzdHMiCiAgcmVjb3JkX3Jlc3Vs
dCAiQnVpbGQgcHJvY2VzcyIgUEFTUyAiJHtFVklERU5DRV9ESVJ9L2V4ZWN1dGlvbi5sb2ciICJw
eXRob24gY29tcGlsZWFsbCBjb21wbGV0ZWQiCgogIGdlbmVyYXRlX21hbmlmZXN0CiAgcnVuIHB5
dGhvbiAtbSBqc29uLnRvb2wgIiR7UkVMRUFTRV9ESVJ9L1JFTEVBU0VfTUFOSUZFU1QuanNvbiIK
ICBydW4gc2hhMjU2c3VtIC1jICIke1JFTEVBU0VfRElSfS9SRUxFQVNFX01BTklGRVNULmpzb24u
c2hhMjU2IgogIHJlY29yZF9yZXN1bHQgIlJFTEVBU0VfTUFOSUZFU1QuanNvbiIgUEFTUyAiJHtS
RUxFQVNFX0RJUn0vUkVMRUFTRV9NQU5JRkVTVC5qc29uIiAibWFuaWZlc3QgYW5kIFNIQTI1NiBn
ZW5lcmF0ZWQiCgogIChjZCAiJHtSRUxFQVNFX0RJUn0iICYmIFBZVEhPTlBBVEg9IiR7UkVMRUFT
RV9ESVJ9IiBGT1hCUkFJTl9FTlY9cmVsZWFzZV9jYW5kaWRhdGUgQVBQX0VOVj1yZWxlYXNlX2Nh
bmRpZGF0ZSBSRUxFQVNFX0lEPSIke0NBTkRJREFURV9JRH0iIFdFQ09NX01PREU9ZHJ5X3J1biBw
eXRob24gLW0gZmxhc2sgLS1hcHAgYXBwcy5haS5hcHAgcnVuIC0taG9zdCAiJHtQUkVWSUVXX0hP
U1R9IiAtLXBvcnQgIiR7UFJFVklFV19QT1JUfSIgPiAiJHtMT0dfRElSfS9wcmV2aWV3LXJ1bnRp
bWUubG9nIiAyPiYxKSAmCiAgUFJFVklFV19QSUQ9JCEKICBzbGVlcCAzCiAgaWYgISBraWxsIC0w
ICIke1BSRVZJRVdfUElEfSIgMj4vZGV2L251bGw7IHRoZW4gRkFJTEVEPTE7IHJlY29yZF9yZXN1
bHQgIlByZXZpZXcgcnVudGltZSBzdGFydHVwIiBGQUlMICIke0xPR19ESVJ9L3ByZXZpZXctcnVu
dGltZS5sb2ciICJwcm9jZXNzIGV4aXRlZCI7IGdlbmVyYXRlX3JlcG9ydCBmYWlsZWQ7IGV4aXQg
MTI7IGZpCiAgcmVjb3JkX3Jlc3VsdCAiUHJldmlldyBydW50aW1lIHN0YXJ0dXAiIFBBU1MgIiR7
TE9HX0RJUn0vcHJldmlldy1ydW50aW1lLmxvZyIgInBpZCAke1BSRVZJRVdfUElEfSwgJHtQUkVW
SUVXX0hPU1R9OiR7UFJFVklFV19QT1JUfSIKCiAgc21va2UgImxvZ2luIiAiaHR0cDovLyR7UFJF
VklFV19IT1NUfToke1BSRVZJRVdfUE9SVH0vbG9naW4iICdeKDIwMHwzMDIpJCcKICBzbW9rZSAi
YXV0aCIgImh0dHA6Ly8ke1BSRVZJRVdfSE9TVH06JHtQUkVWSUVXX1BPUlR9L29wcy1hcGkvaWRl
bnRpdHkvbWUiICdeKDQwMXw0MDN8MzAyKSQnCiAgc21va2UgImFnZW50cyIgImh0dHA6Ly8ke1BS
RVZJRVdfSE9TVH06JHtQUkVWSUVXX1BPUlR9L2FnZW50cyIgJ14oMjAwfDMwMikkJwogIHNtb2tl
ICJrbm93bGVkZ2UiICJodHRwOi8vJHtQUkVWSUVXX0hPU1R9OiR7UFJFVklFV19QT1JUfS9rbm93
bGVkZ2UiICdeKDIwMHwzMDIpJCcKICBzbW9rZSAid29ya2Zsb3dzIiAiaHR0cDovLyR7UFJFVklF
V19IT1NUfToke1BSRVZJRVdfUE9SVH0vdGFza3MiICdeKDIwMHwzMDIpJCcKICBzbW9rZSAiV2VD
b20iICJodHRwOi8vJHtQUkVWSUVXX0hPU1R9OiR7UFJFVklFV19QT1JUfS93ZWNvbSIgJ14oMjAw
fDMwMikkJwogIHNtb2tlICJBUEkiICJodHRwOi8vJHtQUkVWSUVXX0hPU1R9OiR7UFJFVklFV19Q
T1JUfS9oZWFsdGgvdmVyc2lvbiIgJ14oMjAwfDUwMykkJwogIHNtb2tlICJuZ2lueCBwcmV2aWV3
IiAiaHR0cDovLyR7UFJFVklFV19IT1NUfToke1BSRVZJRVdfUE9SVH0vIiAnXigyMDB8MzAyKSQn
CiAgYXNzZXJ0X3Byb2R1Y3Rpb25fcG9pbnRlcgogIHJlY29yZF9yZXN1bHQgIlByb2R1Y3Rpb24g
cG9pbnRlciB1bmNoYW5nZWQgKHBvc3QpIiBQQVNTICIke0VWSURFTkNFX0RJUn0vZXhlY3V0aW9u
LmxvZyIgIiQoY3VycmVudF90YXJnZXQpIgoKICBnZW5lcmF0ZV9yZXBvcnQgY29tcGxldGVkCiAg
aWYgWyAiJHtGQUlMRUR9IiA9ICIxIiBdOyB0aGVuIGV4aXQgMjA7IGZpCiAgaWYgWyAiJHtLRUVQ
X1JVTlRJTUV9IiAhPSAiMSIgXTsgdGhlbiBraWxsICIke1BSRVZJRVdfUElEfSIgMj4vZGV2L251
bGwgfHwgdHJ1ZTsgd2FpdCAiJHtQUkVWSUVXX1BJRH0iIDI+L2Rldi9udWxsIHx8IHRydWU7IFBS
RVZJRVdfUElEPSIiOyBmaQogIGxvZyAiQ2FuZGlkYXRlIHZhbGlkYXRpb24gcmVwb3J0OiAke1JF
UE9SVF9QQVRIfSIKfQoKbWFpbiAiJEAiCg==
PAYLOAD_BASE64
}

main() {
  log "AI release tooling offline installer for ${TARGET_DOMAIN}"
  log "Safety mode: installer only; no cutover, no data change, no Docker restart, no symlink change"

  verify_pointer

  run mkdir -p "${OPS_DIR}"
  write_tool_payload

  local actual_sha
  actual_sha="$(sha256sum "${TMP_FILE}" | awk '{print $1}')"
  if [ "${actual_sha}" != "${EXPECTED_SHA256}" ]; then
    fail "embedded tooling checksum mismatch: got ${actual_sha}, expected ${EXPECTED_SHA256}"
  fi
  log "embedded tooling checksum verified: ${actual_sha}"

  run install -m 0755 "${TMP_FILE}" "${TOOL_PATH}"
  run chmod 755 "${TOOL_PATH}"

  actual_sha="$(sha256sum "${TOOL_PATH}" | awk '{print $1}')"
  if [ "${actual_sha}" != "${EXPECTED_SHA256}" ]; then
    fail "installed tooling checksum mismatch: got ${actual_sha}, expected ${EXPECTED_SHA256}"
  fi
  log "installed tooling checksum verified: ${actual_sha}"

  run bash "${TOOL_PATH}" --help

  verify_pointer
  log "Install complete: ${TOOL_PATH}"
}

main "$@"
INSTALLER_PAYLOAD
}

write_report() {
  local status="${1:-PASS}"
  cat > "${REPORT_PATH}" <<REPORT
# AI Release Installer Offline Update Report

Generated UTC: $(date -u +%Y-%m-%dT%H:%M:%SZ)
Target: ai.vafox.com
Production root: \`${PROD_ROOT}\`

## Backup Path

- Backup path: \`${BACKUP_PATH}\`
- Backup result: ${BACKUP_RESULT}

## Updated File

- Updated file: \`${INSTALLER_PATH}\`
- Update result: ${UPDATE_RESULT}
- Expected SHA256: \`${EXPECTED_INSTALLER_SHA256}\`
- Checksum result: ${CHECKSUM_RESULT}

## Validation Result

- Syntax validation: ${VALIDATION_RESULT}
- Fixed guard verification: requires \`EXPECTED_CURRENT_TARGET="\${PROD_ROOT}/releases/fba3c17"\` logic and \`readlink -f\` pointer resolution.
- Help validation: ${HELP_RESULT}

## Production Pointer Before/After

- Before: \`${POINTER_BEFORE}\`
- After: \`${POINTER_AFTER}\`
- Required invariant: \`${EXPECTED_POINTER}\`

## Safety Confirmation

- No SSH was used.
- No git command was used.
- No docker restart was performed.
- No nginx change was performed.
- No database change was performed.
- No release cutover was performed.
- \`${CURRENT_LINK}\` was not changed by this updater.
- Final status: ${status}
REPORT
}

main() {
  log "Starting offline installer update for ${INSTALLER_PATH}"
  POINTER_BEFORE="$(pointer_target)"
  local releases_before releases_after
  releases_before="$(release_count)"

  if [ "${POINTER_BEFORE}" != "${EXPECTED_POINTER}" ]; then
    fail "production pointer before update is ${POINTER_BEFORE}, expected ${EXPECTED_POINTER}"
  fi

  write_payload
  local payload_sha
  payload_sha="$(sha256sum "${TMP_INSTALLER}" | awk '{print $1}')"
  if [ "${payload_sha}" != "${EXPECTED_INSTALLER_SHA256}" ]; then
    CHECKSUM_RESULT="FAIL: payload ${payload_sha}"
    fail "payload checksum mismatch"
  fi
  CHECKSUM_RESULT="PASS: payload ${payload_sha}"

  mkdir -p "${OPS_DIR}"
  if [ -f "${INSTALLER_PATH}" ]; then
    cp -p "${INSTALLER_PATH}" "${BACKUP_PATH}"
  else
    : > "${BACKUP_PATH}"
  fi
  BACKUP_RESULT="PASS"

  install -m 0755 "${TMP_INSTALLER}" "${INSTALLER_PATH}"
  UPDATE_RESULT="PASS"

  local installed_sha
  installed_sha="$(sha256sum "${INSTALLER_PATH}" | awk '{print $1}')"
  if [ "${installed_sha}" != "${EXPECTED_INSTALLER_SHA256}" ]; then
    CHECKSUM_RESULT="FAIL: installed ${installed_sha}"
    fail "installed checksum mismatch"
  fi
  CHECKSUM_RESULT="PASS: payload and installed ${installed_sha}"

  bash -n "${INSTALLER_PATH}"
  VALIDATION_RESULT="PASS: bash -n ${INSTALLER_PATH}"

  if ! grep -Eq 'EXPECTED_CURRENT_TARGET=.*(\$\{PROD_ROOT\}/releases/fba3c17|/opt/ai-vafox/releases/fba3c17)' "${INSTALLER_PATH}"; then
    VALIDATION_RESULT="FAIL: fixed guard string missing"
    fail "fixed guard string missing"
  fi
  if ! grep -q 'readlink -f' "${INSTALLER_PATH}"; then
    VALIDATION_RESULT="FAIL: readlink -f missing"
    fail "absolute-path readlink guard missing"
  fi
  VALIDATION_RESULT="PASS: syntax and fixed guard"

  bash "${INSTALLER_PATH}" --help >/tmp/ai_release_installer_help_check.out
  HELP_RESULT="PASS: help only"

  POINTER_AFTER="$(pointer_target)"
  releases_after="$(release_count)"
  if [ "${POINTER_AFTER}" != "${EXPECTED_POINTER}" ]; then
    fail "production pointer after help is ${POINTER_AFTER}, expected ${EXPECTED_POINTER}"
  fi
  if [ "${releases_after}" != "${releases_before}" ]; then
    fail "release directory count changed during help check: before=${releases_before} after=${releases_after}"
  fi

  write_report "PASS"
  log "Offline installer update complete. Report: ${REPORT_PATH}"
}

main "$@"
