"""Enterprise OS platform alignment metadata and health model.

This module is intentionally declarative: it defines the shared version,
read-only data-chain contract, and health endpoints used to align Core, AI,
Huyan, and Gateway without writing to SAP or duplicating business facts in AI.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, List

ENTERPRISE_OS_VERSION = "0.20.5"
NEXT_ENTERPRISE_OS_VERSION = "0.21"
RELEASE_NAME = "FoxBrain Enterprise OS V0.20.5 Platform Alignment"


@dataclass(frozen=True)
class PlatformContract:
    name: str
    responsibility: str
    source_of_truth: str
    health_endpoint: str
    release_unit: str
    write_policy: str


PLATFORM_CONTRACTS: Dict[str, PlatformContract] = {
    "core": PlatformContract(
        name="Core",
        responsibility="SAP Mirror + enterprise data service",
        source_of_truth="Read-only SAP B1 mirror and approved enterprise datasets",
        health_endpoint="/api/v1/data-health",
        release_unit="apps/core_api + infra/sap-mirror",
        write_policy="read_only_sap_mirror_no_direct_sap_write",
    ),
    "ai": PlatformContract(
        name="AI",
        responsibility="AI capability center, workflow automation, and replenishment worker",
        source_of_truth="Core APIs only; no second business-facts database",
        health_endpoint="/ops-api/connections/check",
        release_unit="apps/ai",
        write_policy="derived_ai_work_products_only",
    ),
    "huyan": PlatformContract(
        name="Huyan",
        responsibility="CEO operating center",
        source_of_truth="Core and approved AI outputs with evidence links",
        health_endpoint="/healthz",
        release_unit="portal_v2.py + infra/nginx/huyan*.conf",
        write_policy="portal_state_only_no_sap_write",
    ),
    "gateway": PlatformContract(
        name="Gateway",
        responsibility="Unified entry, authentication, and public status proxy",
        source_of_truth="Core public APIs",
        health_endpoint="/healthz",
        release_unit="apps/gateway",
        write_policy="read_only_public_proxy",
    ),
}

RELEASE_GATES: List[str] = [
    "unit_tests_pass",
    "workflow_scripts_guard_pass",
    "security_boundaries_pass",
    "core_readonly_contract_pass",
    "deployment_health_verified",
]


def platform_manifest() -> dict:
    """Return the unified Enterprise OS manifest used by docs, CI, and release checks."""

    return {
        "version": ENTERPRISE_OS_VERSION,
        "next_version": NEXT_ENTERPRISE_OS_VERSION,
        "release_name": RELEASE_NAME,
        "data_chain": "SAP B1 -> SAP Mirror -> Core -> Gateway/Huyan/AI",
        "sap_policy": "SAP B1 remains protected: no direct writes and no finance-flow changes.",
        "core_policy": "Core is the only enterprise data understanding layer.",
        "ai_policy": "AI consumes Core APIs and stores only prompts, approvals, evidence, and derived work products.",
        "platforms": {key: asdict(value) for key, value in PLATFORM_CONTRACTS.items()},
        "release_gates": RELEASE_GATES,
    }


def validate_manifest(manifest: dict | None = None) -> List[str]:
    """Validate non-negotiable platform alignment rules."""

    manifest = manifest or platform_manifest()
    violations: List[str] = []
    if "SAP B1" not in manifest.get("sap_policy", "") or "no direct writes" not in manifest.get("sap_policy", ""):
        violations.append("sap_readonly_policy_missing")
    if not manifest.get("core_policy", "").startswith("Core is the only"):
        violations.append("core_single_understanding_layer_missing")
    ai_source = manifest.get("platforms", {}).get("ai", {}).get("source_of_truth", "")
    if "Core APIs only" not in ai_source:
        violations.append("ai_core_source_of_truth_missing")
    for key in ("core", "ai", "huyan", "gateway"):
        platform = manifest.get("platforms", {}).get(key)
        if not platform:
            violations.append(f"{key}_contract_missing")
        elif not platform.get("health_endpoint"):
            violations.append(f"{key}_health_endpoint_missing")
    return violations
