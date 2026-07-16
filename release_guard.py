#!/usr/bin/env python3
"""FoxBrain release guard: blocks mixed AI OS V5.1 deployments."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

EXPECTED_VERSION = "AI-OS-V5.1"
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
            if data.get(key) != EXPECTED_VERSION:
                failures.append(f"{service}.{key}: expected {EXPECTED_VERSION}, got {data.get(key)!r}")
        if data.get("deployment_version") != EXPECTED_VERSION or data.get("runtime_version") != EXPECTED_VERSION:
            failures.append(f"{service}: deployment/runtime version mismatch")
    return {"status": "PASS" if not failures else "FAIL", "expected_version": EXPECTED_VERSION, "failures": failures}


def main(argv: list[str]) -> int:
    path = argv[1] if len(argv) > 1 else os.environ.get("FOXBRAIN_RELEASE_MANIFEST", "release-manifest.json")
    result = validate_manifest(load_manifest(path))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "PASS" else 1

if __name__ == "__main__":
    sys.exit(main(sys.argv))
