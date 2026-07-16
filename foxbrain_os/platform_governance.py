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

RELEASE_VERSION = "AI-OS-V4.0"
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


def version_payload(service: str, status: str = "running") -> dict:
    metadata = _deployment_metadata()
    return {
        "system": os.environ.get("FOXBRAIN_SYSTEM", metadata.get("system", SYSTEM_NAME)),
        "version": os.environ.get("FOXBRAIN_VERSION", metadata.get("version", RELEASE_VERSION)),
        "service": service,
        "commit": os.environ.get("GIT_COMMIT") or os.environ.get("COMMIT_SHA") or metadata.get("commit") or current_commit(),
        "build_time": os.environ.get("BUILD_TIME", metadata.get("build_time", "unknown")),
        "deploy_time": os.environ.get("DEPLOY_TIME", metadata.get("deploy_time", "unknown")),
        "environment": os.environ.get("FOXBRAIN_ENV") or os.environ.get("ENVIRONMENT") or metadata.get("environment", "development"),
        "status": status,
    }


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
