#!/usr/bin/env bash
set -Eeuo pipefail

# Repository convenience wrapper for the release-candidate build tooling.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec bash "${SCRIPT_DIR}/scripts/ai_genesis_candidate_build.sh" "$@"
