"""Fetch a read-only Data Core health snapshot and write an auditable JSON report."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from foxbrain_os.enterprise_data_service import EnterpriseDataClient


def main():
    output = Path(os.environ.get("DATA_HEALTH_REPORT_PATH", "DATA_HEALTH_REPORT.json"))
    client = EnterpriseDataClient(
        os.environ.get("CORE_BASE_URL", "https://core.vafox.com"),
        os.environ.get("CORE_API_TOKEN", ""),
        cache_seconds=0,
    )
    result = client.data_health()
    if not result.get("ok"):
        print("Data Core health check failed", file=sys.stderr)
        return 1
    temporary = output.with_suffix(output.suffix + ".tmp")
    temporary.write_text(json.dumps(result["data"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(output)
    print(str(output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
