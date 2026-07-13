import unittest
from pathlib import Path

from apps.ai.connectors import ReadOnlyJSONConnector
from apps.ai.domain import (
    AGENT_ROLES,
    SCHEMA_STATEMENTS,
    normalize_evidence,
    require_human_approval,
    validate_feedback,
    validate_task,
)


ROOT = Path(__file__).resolve().parents[1]
AI_ROOT = ROOT / "apps" / "ai"
EVIDENCE = [{
    "source_layer": "data_core",
    "source_type": "core.vafox.com",
    "source_id": "batch-1",
    "source_ref": "https://core.vafox.com/batches/1",
    "statement": "库存事实来自只读副本",
}]


class EnterpriseAIPlatformTest(unittest.TestCase):
    def test_five_agents_have_explicit_roles(self):
        self.assertEqual(len(AGENT_ROLES), 5)
        self.assertEqual({row[0] for row in AGENT_ROLES}, {"business", "inventory", "brand", "content", "enterprise"})

    def test_evidence_is_required_and_complete(self):
        self.assertEqual(normalize_evidence(EVIDENCE)[0]["source_id"], "batch-1")
        with self.assertRaisesRegex(ValueError, "可追溯依据"):
            normalize_evidence([])
        with self.assertRaisesRegex(ValueError, "每条依据"):
            normalize_evidence([{"source_type": "core.vafox.com"}])

    def test_human_approval_is_mandatory(self):
        self.assertEqual(require_human_approval("pending", "approve"), "approved")
        self.assertEqual(require_human_approval("pending_review", "reject"), "rejected")
        with self.assertRaises(ValueError):
            require_human_approval("approved", "approve")

    def test_task_keeps_source_and_evidence(self):
        self.assertEqual(validate_task("复核库存", "ai_agent_run", "RUN-1", "ai.vafox.com/runs/1", EVIDENCE), EVIDENCE)
        with self.assertRaisesRegex(ValueError, "保留来源"):
            validate_task("复核库存", "", "", "", EVIDENCE)

    def test_feedback_requires_known_type_and_valid_score(self):
        self.assertEqual(validate_feedback("effective", "5"), 5)
        with self.assertRaises(ValueError):
            validate_feedback("automatic_learning")
        with self.assertRaises(ValueError):
            validate_feedback("effective", 8)

    def test_connectors_are_https_and_host_locked(self):
        ReadOnlyJSONConnector("https://core.vafox.com", "core.vafox.com")
        with self.assertRaisesRegex(ValueError, "https"):
            ReadOnlyJSONConnector("http://core.vafox.com", "core.vafox.com")
        with self.assertRaisesRegex(ValueError, "core.vafox.com"):
            ReadOnlyJSONConnector("https://core.vafox.com.evil.example", "core.vafox.com")

    def test_schema_covers_six_modules_and_evidence(self):
        schema = "\n".join(SCHEMA_STATEMENTS)
        for table in ("ai_agents", "enterprise_connections", "ai_agent_runs", "ai_knowledge_items", "ai_tasks", "ai_feedback", "ai_evidence_links", "wecom_connections"):
            self.assertIn(table, schema)

    def test_routes_are_separate_from_dify_api(self):
        source = (AI_ROOT / "app.py").read_text(encoding="utf-8")
        for route in ("/dashboard", "/workbench", "/agents", "/wecom", "/knowledge", "/tasks", "/feedback", "/ops-api/health", "/ops-api/exchange/approved-runs"):
            self.assertIn(route, source)
        self.assertIn("human_required", (AI_ROOT / "domain.py").read_text(encoding="utf-8"))

    def test_user_pages_are_chinese_and_hide_technical_fields(self):
        combined = "\n".join(path.read_text(encoding="utf-8") for path in (AI_ROOT / "templates").glob("*.html"))
        for label in ("AI工作台", "Agent中心", "企业微信", "知识中心", "任务中心", "反馈学习"):
            self.assertIn(label, combined)
        for technical in ("ai_agent_runs", "enterprise_connections", "jsonb", "postgres"):
            self.assertNotIn(technical, combined.lower())

    def test_no_sap_write_or_direct_database_connection(self):
        source = "\n".join(path.read_text(encoding="utf-8") for path in AI_ROOT.rglob("*.py"))
        for marker in ("47.107.", "SAPADMIN", "pytds", "pymssql", "update O", "insert into O"):
            self.assertNotIn(marker, source)


if __name__ == "__main__":
    unittest.main()
