#!/usr/bin/env python3
"""Generate FoxBrain deployment metadata without changing business logic."""
from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def git_commit() -> str:
    return os.environ.get("GIT_COMMIT") or os.environ.get("COMMIT_SHA") or subprocess.check_output(["git", "rev-parse", "--short=12", "HEAD"], text=True).strip()


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def main() -> int:
    output = Path(os.environ.get("FOXBRAIN_DEPLOYMENT_METADATA", "deployment.json"))
    build_time = os.environ.get("BUILD_TIME", now())
    payload = {
        "system": "FoxBrain",
        "version": os.environ.get("FOXBRAIN_VERSION", "AI-OS-V6-CLEAN-REBUILD-V1"),
        "release": os.environ.get("FOXBRAIN_RELEASE", "production"),
        "commit": git_commit(),
        "build_time": build_time,
        "deploy_time": os.environ.get("DEPLOY_TIME", build_time),
        "environment": os.environ.get("FOXBRAIN_ENV") or os.environ.get("ENVIRONMENT", "production"),
        "services": ["gateway", "huyan", "ai", "core"],
    }
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
