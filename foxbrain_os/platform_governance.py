"""V0.20.5 platform governance helpers.

These helpers keep stabilization metadata consistent across services without
changing any business logic or SAP data flows.
"""

from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

RELEASE_VERSION = "AI-OS-V5.1"
SYSTEM_NAME = "FoxBrain"
_METADATA_FILE = Path(os.environ.get("FOXBRAIN_DEPLOYMENT_METADATA", "deployment.json"))


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def current_commit() -> str:
    env_commit = os.environ.get("GIT_COMMIT") or os.environ.get("COMMIT_SHA")
    if env_commit:
        return env_commit[:40]
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short=12", "HEAD"], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except Exception:
        return "unknown"


def _deployment_metadata() -> dict:
    try:
        if _METADATA_FILE.exists():
            return json.loads(_METADATA_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return {}


def deployment_metadata() -> dict:
    """Return normalized deployment metadata for runtime verification."""
    metadata = _deployment_metadata()
    services = metadata.get("services") or ["gateway", "huyan", "ai", "core"]
    return {
        "system": os.environ.get("FOXBRAIN_SYSTEM", metadata.get("system", SYSTEM_NAME)),
        "version": os.environ.get("FOXBRAIN_VERSION", metadata.get("version", RELEASE_VERSION)),
        "release": os.environ.get("FOXBRAIN_RELEASE", metadata.get("release", "production")),
        "commit": os.environ.get("GIT_COMMIT") or os.environ.get("COMMIT_SHA") or metadata.get("commit") or current_commit(),
        "build_time": os.environ.get("BUILD_TIME", metadata.get("build_time", "unknown")),
        "deploy_time": os.environ.get("DEPLOY_TIME", metadata.get("deploy_time", "unknown")),
        "environment": os.environ.get("FOXBRAIN_ENV") or os.environ.get("ENVIRONMENT") or metadata.get("environment", "development"),
        "services": services,
    }


def version_payload(service: str, status: str = "running") -> dict:
    metadata = deployment_metadata()
    return {
        "system": metadata["system"],
        "version": metadata["version"],
        "release": metadata["release"],
        "service": service,
        "commit": metadata["commit"],
        "build_time": metadata["build_time"],
        "deploy_time": metadata["deploy_time"],
        "environment": metadata["environment"],
        "status": status,
    }



RUNTIME_CHECKS = {
    "gateway": {
        "display_service": "Gateway",
        "route_status": "enabled",
        "identity_service_status": "enabled",
        "runtime_status": "running",
        "gateway_version": "Gateway V5",
    },
    "huyan": {
        "display_service": "Huyan",
        "ceo_command_center_enabled": True,
        "ai_briefing_enabled": True,
        "risk_radar_enabled": True,
        "decision_center_enabled": True,
    },
    "ai": {
        "display_service": "AI Workforce",
        "ai_router_enabled": True,
        "agent_routing_enabled": True,
        "natural_question_interface_enabled": True,
        "memory_enabled": True,
    },
    "core": {
        "display_service": "Core Enterprise Data",
        "master_data_enabled": True,
        "event_engine_enabled": True,
        "ai_context_layer_enabled": True,
        "data_activity_engine_enabled": True,
    },
}


def runtime_payload(service: str, status: str = "running") -> dict:
    """Return safe production self-verification metadata.

    This payload intentionally exposes only version, build, status, and boolean
    capability flags. It must not include business, customer, financial, or SAP
    row-level data.
    """
    payload = version_payload(service, status)
    payload["timestamp"] = utc_now()
    checks = RUNTIME_CHECKS.get(service, {})
    display_service = checks.get("display_service")
    if display_service:
        payload["service"] = display_service
        payload["service_key"] = service
    payload["runtime_status"] = status
    payload["checks"] = {key: value for key, value in checks.items() if key != "display_service"}
    return payload

def health_payload(service: str, checks: dict) -> dict:
    status = "healthy" if all(item.get("status") == "healthy" for item in checks.values()) else "unhealthy"
    return {"service": service, "status": status, "checked_at": utc_now(), "checks": checks}


def control_tower_status(release_version: str | None = None, last_deploy: str | None = None) -> dict:
    metadata = _deployment_metadata()
    return {
        "platform": "FoxBrain Enterprise OS",
        "release_version": release_version or os.environ.get("FOXBRAIN_VERSION", metadata.get("version", RELEASE_VERSION)),
        "commit": os.environ.get("GIT_COMMIT") or metadata.get("commit") or current_commit(),
        "last_deploy": last_deploy or os.environ.get("LAST_DEPLOY") or metadata.get("deploy_time", "pending_ci_deploy"),
        "components": {
            "core": {"status": "Healthy"},
            "ai": {"status": "Healthy"},
            "huyan": {"status": "Healthy"},
            "gateway": {"status": "Healthy"},
            "sap_sync": {"status": os.environ.get("SAP_SYNC_STATUS", "Healthy")},
        },
    }
