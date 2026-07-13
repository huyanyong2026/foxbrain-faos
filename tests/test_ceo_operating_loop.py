import sqlite3
import tempfile
import unittest
from pathlib import Path

from foxbrain_os.ceo_operating_loop import (
    attach_ai_analysis,
    confirm_decision_memory,
    confirm_operating_review,
    create_decision_memory,
    create_enterprise_question,
    create_morning_brief,
    create_operating_review,
    ensure_ceo_operating_loop_schema,
    evidence_chain,
    operating_loop_summary,
    review_ai_analysis,
)


FACTS = {"sales": 100, "inventory": 50}
EVIDENCE = [{
    "source_type": "core.vafox.com",
    "source_id": "facts-20260713",
    "source_ref": "Data Core企业事实快照/2026-07-13",
    "source_layer": "data_core",
    "statement": "销售额100，库存50",
}]


class CEOOperatingLoopTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.conn = sqlite3.connect(Path(self.temp.name) / "loop.db")
        self.conn.row_factory = sqlite3.Row
        ensure_ceo_operating_loop_schema(self.conn)

    def tearDown(self):
        self.conn.close()
        self.temp.cleanup()

    def test_morning_brief_is_idempotent_and_waits_for_ai(self):
        first = create_morning_brief(self.conn, "2026-07-13", FACTS, EVIDENCE, 1)
        second = create_morning_brief(self.conn, "2026-07-13", FACTS, EVIDENCE, 1)
        self.assertEqual(first["brief_id"], second["brief_id"])
        self.assertEqual(first["status"], "waiting_ai")
        self.assertTrue(second["duplicate"])

    def test_ai_analysis_must_come_from_ai_vafox_and_have_evidence(self):
        brief = create_morning_brief(self.conn, "2026-07-13", FACTS, EVIDENCE, 1)
        with self.assertRaisesRegex(ValueError, "ai.vafox.com"):
            attach_ai_analysis(self.conn, "morning_brief", brief["brief_id"], "建议关注库存", EVIDENCE, "https://example.com/analysis/1")
        with self.assertRaisesRegex(ValueError, "ai.vafox.com"):
            attach_ai_analysis(self.conn, "morning_brief", brief["brief_id"], "建议关注库存", EVIDENCE, "https://ai.vafox.com.evil.example/analysis/1")
        with self.assertRaisesRegex(ValueError, "可追溯依据"):
            attach_ai_analysis(self.conn, "morning_brief", brief["brief_id"], "建议关注库存", [], "https://ai.vafox.com/analysis/1")
        result = attach_ai_analysis(self.conn, "morning_brief", brief["brief_id"], "建议关注库存", EVIDENCE, "https://ai.vafox.com/analysis/1")
        self.assertEqual(result["status"], "pending_review")

    def test_ai_suggestion_requires_manual_review(self):
        question = create_enterprise_question(self.conn, "库存是否需要调整？", FACTS, EVIDENCE, created_by=1)
        with self.assertRaisesRegex(ValueError, "尚未进入人工复核"):
            review_ai_analysis(self.conn, "enterprise_question", question["question_id"], True, 1)
        attach_ai_analysis(self.conn, "enterprise_question", question["question_id"], "建议先复核库存", EVIDENCE, "https://ai.vafox.com/analysis/Q1")
        row = self.conn.execute("select status from enterprise_questions where question_id=?", (question["question_id"],)).fetchone()
        self.assertEqual(row["status"], "pending_review")
        reviewed = review_ai_analysis(self.conn, "enterprise_question", question["question_id"], True, 1)
        self.assertEqual(reviewed["status"], "confirmed")

    def test_decision_cannot_use_unconfirmed_ai_analysis(self):
        question = create_enterprise_question(self.conn, "是否采购？", FACTS, EVIDENCE, created_by=1)
        with self.assertRaisesRegex(ValueError, "尚未经过人工确认"):
            create_decision_memory(self.conn, "采购判断", "暂缓采购", "库存偏高", EVIDENCE, 1, question["question_id"])

    def test_decision_and_review_form_closed_loop(self):
        question = create_enterprise_question(self.conn, "是否采购？", FACTS, EVIDENCE, created_by=1)
        attach_ai_analysis(self.conn, "enterprise_question", question["question_id"], "建议暂缓", EVIDENCE, "https://ai.vafox.com/analysis/Q2")
        review_ai_analysis(self.conn, "enterprise_question", question["question_id"], True, 1)
        decision = create_decision_memory(self.conn, "采购判断", "暂缓采购", "库存偏高", EVIDENCE, 1, question["question_id"])
        self.assertEqual(decision["status"], "draft")
        confirm_decision_memory(self.conn, decision["decision_id"], 1)
        review = create_operating_review(self.conn, decision["decision_id"], "库存下降10%", EVIDENCE, 1, lessons="控制采购有效")
        self.assertEqual(review["status"], "draft")
        confirm_operating_review(self.conn, review["review_id"], 1)
        summary = operating_loop_summary(self.conn)
        self.assertEqual(summary["decisions_confirmed"], 1)
        self.assertEqual(summary["reviews_confirmed"], 1)

    def test_evidence_chain_preserves_core_and_ai_layers(self):
        question = create_enterprise_question(self.conn, "今日风险？", FACTS, EVIDENCE, created_by=1)
        attach_ai_analysis(self.conn, "enterprise_question", question["question_id"], "库存风险", EVIDENCE, "https://ai.vafox.com/analysis/Q3")
        links = evidence_chain(self.conn, "enterprise_question", question["question_id"])["evidence"]
        self.assertEqual({row["source_layer"] for row in links}, {"data_core", "ai_analysis"})

    def test_missing_evidence_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "可追溯依据"):
            create_enterprise_question(self.conn, "无依据问题", FACTS, [], created_by=1)
        with self.assertRaisesRegex(ValueError, "可追溯依据"):
            create_morning_brief(self.conn, "2026-07-14", FACTS, [], 1)

    def test_portal_exposes_five_loop_modules(self):
        portal = (Path(__file__).resolve().parents[1] / "portal_v2.py").read_text(encoding="utf-8")
        for marker in (
            'path == "/ceo-operating-loop"',
            'path == "/ceo-morning-brief"',
            'path == "/enterprise-question-center"',
            'path == "/decision-memory"',
            'path == "/evidence-chain"',
            'path == "/operating-review"',
        ):
            self.assertIn(marker, portal)


if __name__ == "__main__":
    unittest.main()
