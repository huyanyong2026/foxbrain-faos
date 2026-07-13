"""Run the Core-to-AI replenishment job daily without SAP access."""

from __future__ import annotations

import json
import os
import time
from datetime import datetime
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo


TIMEZONE = ZoneInfo(os.environ.get("REPLENISHMENT_TIMEZONE", "Asia/Shanghai"))
RUN_TIME = os.environ.get("REPLENISHMENT_RUN_TIME", "22:30")
AI_INTERNAL_URL = os.environ.get(
    "AI_INTERNAL_REPLENISHMENT_URL", "http://enterprise-ai:5010/ops-api/internal/replenishment/run"
)


def should_run(now, last_success_date, run_time=RUN_TIME):
    hour, minute = (int(value) for value in run_time.split(":"))
    return (now.hour, now.minute) >= (hour, minute) and last_success_date != now.date().isoformat()


def trigger_job():
    token = os.environ.get("INTERNAL_SERVICE_TOKEN", "")
    if not token:
        raise RuntimeError("INTERNAL_SERVICE_TOKEN is required")
    request = Request(
        AI_INTERNAL_URL, data=b"{}", method="POST",
        headers={"Content-Type": "application/json", "X-FoxBrain-Service-Token": token},
    )
    with urlopen(request, timeout=180) as response:
        payload = json.loads(response.read().decode("utf-8"))
        if response.status != 200 or not payload.get("ok"):
            raise RuntimeError("replenishment job failed")
        return payload


def log(event, **details):
    print(json.dumps({"at": datetime.now(TIMEZONE).isoformat(timespec="seconds"), "event": event, **details}, ensure_ascii=False), flush=True)


def main():
    last_success_date = None
    log("worker_started", run_time=RUN_TIME, source="core.vafox.com")
    while True:
        now = datetime.now(TIMEZONE)
        if should_run(now, last_success_date):
            try:
                result = trigger_job()
                last_success_date = now.date().isoformat()
                log("replenishment_completed", batch_id=result.get("batch_id"), created=result.get("created"))
            except (HTTPError, URLError, TimeoutError, RuntimeError, ValueError, json.JSONDecodeError) as exc:
                log("replenishment_failed", error=str(exc)[:500])
                time.sleep(300)
                continue
        time.sleep(30)


if __name__ == "__main__":
    main()
