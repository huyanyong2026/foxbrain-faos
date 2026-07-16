#!/usr/bin/env python3
"""FoxBrain AI OS V5.1 runtime automation health check.

The check is deterministic by default so CI can validate the automation chain
without production credentials. Set FOXBRAIN_HEALTH_LIVE=1 to also probe live
/runtime endpoints with optional bearer token FOXBRAIN_HEALTH_TOKEN.
"""
from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from urllib.error import URLError
from urllib.request import Request, urlopen

from foxbrain_os.ai_os_v5 import build_ai_os_v5_contract, route_identity, route_intent, run_automation
from foxbrain_os.platform_governance import RELEASE_VERSION

SERVICES = {
    "gateway": "https://gateway.vafox.com",
    "huyan": "https://huyan.vafox.com",
    "ai": "https://ai.vafox.com",
    "core": "https://core.vafox.com",
}
EXPECTED_VERSION = "AI-OS-V5.1"

@dataclass(frozen=True)
class CheckResult:
    name: str
    status: str
    detail: str


def _live_runtime(service: str, base_url: str) -> CheckResult:
    token = os.environ.get("FOXBRAIN_HEALTH_TOKEN", "")
    request = Request(f"{base_url.rstrip('/')}/runtime")
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    try:
        with urlopen(request, timeout=8) as response:  # nosec B310 - operator controlled health URL allowlist above
            payload = json.loads(response.read().decode("utf-8"))
        version = payload.get("version")
        ok = version == EXPECTED_VERSION and payload.get("runtime_status") in {"running", "healthy"}
        return CheckResult(service, "PASS" if ok else "FAIL", f"runtime version={version!r}")
    except (URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
        return CheckResult(service, "FAIL", f"runtime probe failed: {exc}")


def run_checks(live: bool = False) -> dict:
    contract = build_ai_os_v5_contract()
    ai_route = route_intent("分析企业当前最大风险")
    inventory_loop = run_automation("inventory_change", owner="procurement")
    sales_loop = run_automation("sales_change", owner="commerce")

    results = [
        CheckResult("Gateway", "PASS" if route_identity("CEO")["destination"] == "huyan.vafox.com" else "FAIL", "CEO identity routes to Huyan"),
        CheckResult("Huyan", "PASS" if contract["huyan"]["ceo_autonomous_command_center"]["decision_center"] else "FAIL", "CEO command center modules present"),
        CheckResult("AI", "PASS" if not ai_route["manual_agent_selection_required"] and len(ai_route["required_agents"]) >= 2 else "FAIL", "AI Router automatic multi-agent risk routing"),
        CheckResult("Core", "PASS" if contract["core"]["flow"][:3] == ["SAP", "Core", "AI"] else "FAIL", "Core digital twin feeds AI"),
        CheckResult("Data Chain", "PASS" if contract["acceptance"]["data_chain"] == "PASS" else "FAIL", "Identity→Data→AI→Decision→Action→Memory connected"),
        CheckResult("Automation", "PASS" if inventory_loop["task_creation"]["status"] == "pending_human_approval" and sales_loop["opportunity"]["status"] == "generated" else "FAIL", "inventory task and sales opportunity loops validated"),
        CheckResult("Version", "PASS" if RELEASE_VERSION == EXPECTED_VERSION and contract["version"] == EXPECTED_VERSION else "FAIL", f"expected {EXPECTED_VERSION}, got {RELEASE_VERSION}/{contract['version']}"),
    ]
    if live:
        results.extend(_live_runtime(service, url) for service, url in SERVICES.items())

    payload = {
        "version": EXPECTED_VERSION,
        "overall_status": "PASS" if all(item.status == "PASS" for item in results) else "FAIL",
        "checks": [item.__dict__ for item in results],
    }
    return payload


def main() -> int:
    payload = run_checks(live=os.environ.get("FOXBRAIN_HEALTH_LIVE") == "1")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["overall_status"] == "PASS" else 1

if __name__ == "__main__":
    sys.exit(main())
