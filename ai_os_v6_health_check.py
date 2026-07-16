#!/usr/bin/env python3
"""Self health check for FoxBrain AI OS V6 clean architecture."""

from foxbrain_os.ai_os_v6 import health_check_payload


def main() -> int:
    payload = health_check_payload()
    for name, passed in payload["checks"].items():
        print(f"{name}: {'PASS' if passed else 'FAIL'}")
    print(f"Overall: {payload['status']}")
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
