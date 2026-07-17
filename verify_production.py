#!/usr/bin/env python3
"""Verify FoxBrain AI OS V4 production visibility endpoints."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import urllib.request

SERVICES = {
    "Gateway": "https://gateway.vafox.com/health/version",
    "Huyan": "https://huyan.vafox.com/health/version",
    "AI": "https://ai.vafox.com/health/version",
    "Core": "https://core.vafox.com/health/version",
}
from foxbrain_os.platform_governance import RELEASE_VERSION

EXPECTED_VERSION = RELEASE_VERSION


def local_commit() -> str:
    return subprocess.check_output(["git", "rev-parse", "--short=12", "HEAD"], text=True).strip()


def fetch_json(url: str, timeout: int) -> dict:
    with urllib.request.urlopen(url, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify production FoxBrain version metadata")
    parser.add_argument("--version", default=os.environ.get("FOXBRAIN_VERSION", EXPECTED_VERSION))
    parser.add_argument("--timeout", type=int, default=8)
    parser.add_argument("--service", action="append", help="Override as Name=https://host/health/version")
    args = parser.parse_args()
    services = dict(SERVICES)
    for item in args.service or []:
        name, url = item.split("=", 1)
        services[name] = url

    expected_commit = os.environ.get("GIT_COMMIT", local_commit())[:12]
    failed = False
    print(f"Git commit: {expected_commit}")
    for name, url in services.items():
        try:
            payload = fetch_json(url, args.timeout)
            version_ok = payload.get("version") == args.version
            status_ok = payload.get("status") in {"running", "healthy", "ok"}
            commit = str(payload.get("commit", ""))
            commit_ok = commit.startswith(expected_commit) or expected_commit.startswith(commit[:12])
            ok = version_ok and status_ok and commit_ok
            failed = failed or not ok
            print(f"{name}: {'PASS' if ok else 'FAIL'}")
            print(f"Version: {payload.get('version')}")
            print(f"Commit: {payload.get('commit')}")
        except Exception as exc:
            failed = True
            print(f"{name}: FAIL ({exc})")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
