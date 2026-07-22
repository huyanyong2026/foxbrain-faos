#!/usr/bin/env python3
"""VAFOX Genesis release guard: blocks mixed or legacy runtime deployments."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

EXPECTED_VERSION = "v1.0.0"
LEGACY_VERSION_TOKENS = ("AI-OS-V4", "AI-OS-V5", "AI-OS-V5.1", "FoxBrain Enterprise OS")
REQUIRED_SERVICES = ("gateway", "huyan", "ai", "core")
REQUIRED_KEYS = ("frontend_version", "backend_version", "api_version", "database_schema_version")


def load_manifest(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def validate_manifest(manifest: dict) -> dict:
    failures: list[str] = []
    services = manifest.get("services", {})
    for service in REQUIRED_SERVICES:
        data = services.get(service)
        if not isinstance(data, dict):
            failures.append(f"{service}: missing service manifest")
            continue
        for key in REQUIRED_KEYS:
            value = data.get(key)
            if value != EXPECTED_VERSION:
                failures.append(f"{service}.{key}: expected {EXPECTED_VERSION}, got {value!r}")
            if isinstance(value, str) and any(token in value for token in LEGACY_VERSION_TOKENS):
                failures.append(f"{service}.{key}: obsolete legacy version {value!r} is not a Genesis release")
        for key in ("deployment_version", "runtime_version"):
            value = data.get(key)
            if value != EXPECTED_VERSION:
                failures.append(f"{service}.{key}: expected {EXPECTED_VERSION}, got {value!r}")
            if isinstance(value, str) and any(token in value for token in LEGACY_VERSION_TOKENS):
                failures.append(f"{service}.{key}: obsolete legacy version {value!r} is not a Genesis release")
    return {"status": "PASS" if not failures else "FAIL", "expected_version": EXPECTED_VERSION, "failures": failures}


def main(argv: list[str]) -> int:
    path = argv[1] if len(argv) > 1 else os.environ.get("FOXBRAIN_RELEASE_MANIFEST", "release-manifest.json")
    result = validate_manifest(load_manifest(path))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "PASS" else 1

if __name__ == "__main__":
    sys.exit(main(sys.argv))
