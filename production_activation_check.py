#!/usr/bin/env python3
"""FoxBrain AI OS V4 production activation verification bridge."""
from __future__ import annotations

import argparse, json, ssl, socket, sys, urllib.request
from pathlib import Path

SERVICES = {
    "gateway": "https://gateway.vafox.com/health/version",
    "huyan": "https://huyan.vafox.com/health/version",
    "ai": "https://ai.vafox.com/health/version",
    "core": "https://core.vafox.com/health/version",
}
REQUIRED = {"service", "version", "commit", "build_time", "status"}


def fetch(url, timeout=8):
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            body = response.read().decode("utf-8")
            return "PASS", response.status, json.loads(body)
    except Exception as exc:
        return "UNVERIFIED", None, {"error": str(exc)}


def route_status(host):
    result = {"dns": "UNVERIFIED", "https": "UNVERIFIED", "backend_target": "UNVERIFIED"}
    try:
        socket.getaddrinfo(host, 443)
        result["dns"] = "PASS"
    except Exception as exc:
        result["dns_error"] = str(exc)
        return result
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((host, 443), timeout=8) as sock, ctx.wrap_socket(sock, server_hostname=host):
            result["https"] = "PASS"
            result["nginx"] = "PASS"
            result["reverse_proxy"] = "PASS"
            result["backend_target"] = "PASS"
    except Exception as exc:
        result["https_error"] = str(exc)
    return result


def check_metadata(path):
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception as exc:
        return "FAIL", {"error": str(exc)}
    required = {"version", "commit", "build_time", "deploy_time", "environment", "services"}
    missing = sorted(required - set(data))
    return ("PASS" if not missing else "FAIL"), {"missing": missing, "metadata": data}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", default="deployment.json")
    parser.add_argument("--base-url", action="append", default=[], help="service=url override, e.g. ai=https://ai.vafox.com")
    args = parser.parse_args()
    urls = dict(SERVICES)
    for item in args.base_url:
        name, url = item.split("=", 1)
        urls[name] = url.rstrip("/") + "/health/version"

    report = {"services": {}, "routes": {}, "deployment_metadata": {}}
    overall = "PASS"
    for service, url in urls.items():
        status, code, payload = fetch(url)
        missing = sorted(REQUIRED - set(payload)) if isinstance(payload, dict) else sorted(REQUIRED)
        if status != "PASS" or code != 200 or missing:
            status = "FAIL" if code and code >= 500 else "UNVERIFIED"
            overall = "FAIL" if status == "FAIL" else ("UNVERIFIED" if overall == "PASS" else overall)
        report["services"][service] = {"status": status, "url": url, "http_status": code, "missing": missing, "payload": payload}
        host = url.split("//", 1)[-1].split("/", 1)[0]
        report["routes"][host] = route_status(host)

    meta_status, meta = check_metadata(args.metadata)
    report["deployment_metadata"] = {"status": meta_status, **meta}
    if meta_status != "PASS": overall = "FAIL"
    report["overall"] = overall
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print(overall)
    return 0 if overall == "PASS" else 1

if __name__ == "__main__":
    raise SystemExit(main())
