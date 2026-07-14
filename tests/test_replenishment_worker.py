import unittest
from datetime import datetime
from zoneinfo import ZoneInfo

from apps.ai.replenishment_worker import should_run


TZ = ZoneInfo("Asia/Shanghai")


class ReplenishmentWorkerTests(unittest.TestCase):
    def test_waits_until_2230(self):
        self.assertFalse(should_run(datetime(2026, 7, 13, 22, 29, tzinfo=TZ), None))
        self.assertTrue(should_run(datetime(2026, 7, 13, 22, 30, tzinfo=TZ), None))

    def test_runs_only_once_after_success(self):
        now = datetime(2026, 7, 13, 23, 0, tzinfo=TZ)
        self.assertFalse(should_run(now, "2026-07-13"))
        self.assertTrue(should_run(now, "2026-07-12"))


if __name__ == "__main__":
    unittest.main()
