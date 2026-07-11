import importlib.util
import json
import os
import shutil
import tempfile
import time
import unittest
from pathlib import Path


TEST_APP_DIR = tempfile.mkdtemp(prefix="foxbrain-natural-")
os.environ["APP_DIR"] = TEST_APP_DIR
os.environ["SAP_SUMMARY_FILE"] = str(Path(TEST_APP_DIR) / "missing-summary.json")
SPEC = importlib.util.spec_from_file_location(
    "foxbrain_portal_natural_test",
    Path(__file__).resolve().parents[1] / "portal_v2.py",
)
portal = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(portal)


class NaturalExperienceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        portal.init()
        now = int(time.time())
        with portal.db() as conn:
            conn.execute(
                "insert into users(email,name,phone,store,role,status,password_hash,created_at,updated_at) values(?,?,?,?,?,?,?,?,?)",
                ("natural@example.test", "测试老板", "", "总部", "admin", "approved", portal.hp("test-only-password"), now, now),
            )

    def setUp(self):
        self.app = object.__new__(portal.App)
        with portal.db() as conn:
            conn.execute("delete from timeline_events")
            conn.execute("delete from tasks")
            conn.execute("delete from copilot_messages")
            conn.execute("delete from copilot_sessions")
            self.user = conn.execute("select * from users where email=?", ("natural@example.test",)).fetchone()

    def test_page_context_is_clean_and_bounded(self):
        context = self.app.copilot_page_context(
            {"ctx_page": "/brand-intelligence", "ctx_title": "Osprey 品牌分析", "ignored": "x"}
        )
        self.assertEqual(context["page"], "/brand-intelligence")
        self.assertEqual(context["title"], "Osprey 品牌分析")
        self.assertNotIn("ignored", context)

    def test_follow_up_reuses_session_and_keeps_context(self):
        first, first_code = self.app.create_copilot_answer(
            self.user,
            "这个品牌现在怎么样？",
            "",
            "",
            {"page": "/brand-intelligence", "title": "Osprey 品牌分析", "name": "Osprey"},
        )
        second, second_code = self.app.create_copilot_answer(
            self.user,
            "为什么？下一步做什么？",
            "",
            str(first["session_id"]),
            {"page": "/brand-intelligence", "title": "Osprey 品牌分析", "name": "Osprey"},
        )
        self.assertEqual(first_code, 200)
        self.assertEqual(second_code, 200)
        self.assertEqual(second["session_id"], first["session_id"])
        with portal.db() as conn:
            self.assertEqual(conn.execute("select count(*) from copilot_sessions").fetchone()[0], 1)
            self.assertEqual(conn.execute("select count(*) from copilot_messages where session_id=?", (first["session_id"],)).fetchone()[0], 4)
            latest = conn.execute("select context_json from copilot_messages where session_id=? and role='assistant' order by id desc limit 1", (first["session_id"],)).fetchone()
        context = json.loads(latest["context_json"])
        self.assertEqual(context["context"]["page_context"]["name"], "Osprey")
        self.assertEqual(context["context"]["conversation_context"]["session_id"], first["session_id"])

    def test_action_draft_requires_evidence_and_is_idempotent(self):
        answer, answer_code = self.app.create_copilot_answer(
            self.user,
            "今天企业最需要处理什么？",
            "",
            "",
            {"page": "/", "title": "老板经营大脑"},
        )
        self.assertEqual(answer_code, 200)
        with portal.db() as conn:
            message = conn.execute("select id from copilot_messages where id=? and role='assistant'", (answer["message_id"],)).fetchone()
        created, code = self.app.copilot_action_draft(self.user, message["id"])
        repeated, repeated_code = self.app.copilot_action_draft(self.user, message["id"])
        self.assertEqual(code, 200)
        self.assertEqual(repeated_code, 200)
        self.assertEqual(created["task_id"], repeated["task_id"])
        with portal.db() as conn:
            task = conn.execute("select * from tasks where id=?", (created["task_id"],)).fetchone()
        self.assertEqual(task["status"], "draft")
        self.assertEqual(task["source_type"], "copilot_message")


def tearDownModule():
    shutil.rmtree(TEST_APP_DIR, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
