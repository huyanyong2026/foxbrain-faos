#!/usr/bin/env python3
"""Verify FoxBrain AI OS V5 runtime endpoints after deployment."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

EXPECTED_VERSION = os.environ.get("FOXBRAIN_EXPECTED_VERSION", "AI-OS-V5")
DEFAULT_ENDPOINTS = {
    "gateway": "https://gateway.vafox.com/health/runtime",
    "huyan": "https://huyan.vafox.com/health/runtime",
    "ai": "https://ai.vafox.com/health/runtime",
    "core": "https://core.vafox.com/health/runtime",
}


def endpoint_for(service: str) -> str:
    return os.environ.get(f"{service.upper()}_RUNTIME_URL", DEFAULT_ENDPOINTS[service])


def fetch_json(url: str, timeout: int = 10) -> dict:
    request = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def verify_service(service: str) -> tuple[bool, str]:
    url = endpoint_for(service)
    try:
        payload = fetch_json(url)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        return False, f"{service}: FAIL ({url}) {exc}"
    version_ok = payload.get("version") == EXPECTED_VERSION
    status_ok = payload.get("status") == "running" and payload.get("runtime_status") == "running"
    system_ok = payload.get("system") == "FoxBrain"
    if version_ok and status_ok and system_ok:
        return True, f"{service}: PASS {payload.get('version')} {payload.get('commit', 'unknown')}"
    return False, f"{service}: FAIL expected={EXPECTED_VERSION} payload={payload}"


def main() -> int:
    results = [verify_service(service) for service in DEFAULT_ENDPOINTS]
    for ok, line in results:
        print(line)
    return 0 if all(ok for ok, _ in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
