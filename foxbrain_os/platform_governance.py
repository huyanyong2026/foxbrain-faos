"""V0.20.5 platform governance helpers.

These helpers keep stabilization metadata consistent across services without
changing any business logic or SAP data flows.
"""

from __future__ import annotations

import os
import subprocess
from datetime import datetime, timezone

RELEASE_VERSION = "0.20.5"


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


def version_payload(service: str) -> dict:
    return {
        "service": service,
        "version": os.environ.get("FOXBRAIN_VERSION", RELEASE_VERSION),
        "commit": current_commit(),
        "build_time": os.environ.get("BUILD_TIME", "unknown"),
        "environment": os.environ.get("FOXBRAIN_ENV") or os.environ.get("ENVIRONMENT", "development"),
    }


def health_payload(service: str, checks: dict) -> dict:
    status = "healthy" if all(item.get("status") == "healthy" for item in checks.values()) else "unhealthy"
    return {"service": service, "status": status, "checked_at": utc_now(), "checks": checks}


def control_tower_status(release_version: str | None = None, last_deploy: str | None = None) -> dict:
    return {
        "platform": "FoxBrain Enterprise OS",
        "release_version": release_version or os.environ.get("FOXBRAIN_VERSION", RELEASE_VERSION),
        "last_deploy": last_deploy or os.environ.get("LAST_DEPLOY", "pending_ci_deploy"),
        "components": {
            "core": {"status": "Healthy"},
            "ai": {"status": "Healthy"},
            "huyan": {"status": "Healthy"},
            "gateway": {"status": "Healthy"},
            "sap_sync": {"status": os.environ.get("SAP_SYNC_STATUS", "Healthy")},
        },
    }
