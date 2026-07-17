#!/usr/bin/env python3
"""Verify VAFOX production runtime metadata after deployment."""
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request

REQUIRED_FIELDS = {"version", "commit", "build_time", "status", "runtime_status"}
DEFAULT_SERVICES = {
    "gateway": "https://gateway.vafox.com/health/runtime",
    "ai": "https://ai.vafox.com/health/runtime",
    "huyan": "https://huyan.vafox.com/health/runtime",
}


def fetch_json(url: str, timeout: int) -> tuple[int, dict]:
    request = urllib.request.Request(url, headers={"Accept": "application/json", "Cache-Control": "no-cache"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        payload = json.loads(response.read().decode("utf-8"))
        return response.status, payload


def verify(name: str, url: str, expected_commit: str | None, expected_version: str | None, timeout: int) -> tuple[bool, dict]:
    result = {"service": name, "url": url}
    try:
        http_status, payload = fetch_json(url, timeout)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        result.update({"status": "FAIL", "error": str(exc)})
        return False, result
    missing = sorted(REQUIRED_FIELDS - set(payload))
    commit_ok = not expected_commit or str(payload.get("commit", "")).startswith(expected_commit)
    version_ok = not expected_version or payload.get("version") == expected_version
    status_ok = http_status == 200 and payload.get("status") == "running" and payload.get("runtime_status") == "running"
    ok = not missing and commit_ok and version_ok and status_ok
    result.update(
        {
            "status": "PASS" if ok else "FAIL",
            "http_status": http_status,
            "missing": missing,
            "version": payload.get("version"),
            "commit": payload.get("commit"),
            "build_time": payload.get("build_time"),
            "runtime_status": payload.get("runtime_status"),
            "commit_ok": commit_ok,
            "version_ok": version_ok,
        }
    )
    return ok, result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--expected-commit")
    parser.add_argument("--expected-version")
    parser.add_argument("--timeout", type=int, default=10)
    parser.add_argument("--endpoint", action="append", default=[], help="name=url override; may be repeated")
    args = parser.parse_args()

    endpoints = dict(DEFAULT_SERVICES)
    for item in args.endpoint:
        name, url = item.split("=", 1)
        endpoints[name] = url

    checks = [verify(name, url, args.expected_commit, args.expected_version, args.timeout) for name, url in endpoints.items()]
    report = {"overall": "PASS" if all(ok for ok, _ in checks) else "FAIL", "checks": [item for _, item in checks]}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["overall"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
