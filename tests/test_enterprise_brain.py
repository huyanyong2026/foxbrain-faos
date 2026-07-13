import sqlite3
import tempfile
import unittest
from pathlib import Path

from foxbrain_os.enterprise_brain import (
    activate_constitution,
    confirm_founder_memory,
    create_constitution_draft,
    create_founder_memory,
    ensure_enterprise_brain_schema,
    enterprise_asset_map,
    enterprise_brain_summary,
    enterprise_timeline,
)


class EnterpriseBrainTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.conn = sqlite3.connect(Path(self.temp.name) / "brain.db")
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("create table enterprise_objects(id integer primary key,archived_at integer)")
        self.conn.execute("create table living_objects(id integer primary key,status text)")
        self.conn.execute("create table documents(id integer primary key,deleted_at integer)")
        self.conn.execute("create table ceo_vault_items(id integer primary key,status text)")
        self.conn.execute("create table enterprise_memories(id integer primary key,archived_at integer)")
        self.conn.execute("create table knowledge_graph_edges(id integer primary key,status text)")
        self.conn.execute("create table sync_runs(id integer primary key,status text,started_at integer,finished_at integer)")
        self.conn.execute(
            """create table decision_insights(
            id integer primary key,title text,summary text,severity text,status text,evidence text,updated_at integer)"""
        )
        self.conn.execute(
            """create table timeline_events(
            id integer primary key,title text,body text,description text,source_type text,source_id text,
            occurred_at integer,created_at integer)"""
        )
        ensure_enterprise_brain_schema(self.conn)

    def tearDown(self):
        self.conn.close()
        self.temp.cleanup()

    def constitution(self):
        return create_constitution_draft(
            self.conn,
            "火狐狸企业宪章",
            "让更多人走向户外",
            "建设长期户外生活平台",
            ["长期主义", "顾客价值"],
            ["事实优先", "人工决策"],
            1,
            "founder_input",
            "FOUNDER-001",
            "Founder人工输入：企业宪章",
        )

    def test_records_require_a_traceable_source(self):
        with self.assertRaisesRegex(ValueError, "缺少来源"):
            create_constitution_draft(self.conn, "标题", "使命")
        with self.assertRaisesRegex(ValueError, "缺少来源"):
            create_founder_memory(self.conn, "判断", "当时情况", "最终判断")

    def test_constitution_is_versioned_and_manually_activated(self):
        first = self.constitution()
        self.assertEqual(first["status"], "draft")
        activate_constitution(self.conn, first["constitution_id"], 1)
        second = create_constitution_draft(
            self.conn, "企业宪章第二版", "使命不变", created_by=1,
            source_type="founder_input", source_id="FOUNDER-002", source_ref="Founder人工输入：企业宪章第二版",
        )
        self.assertEqual(second["version"], 2)
        self.assertEqual(self.conn.execute("select count(*) from enterprise_constitutions where status='active'").fetchone()[0], 1)

    def test_founder_memory_stays_draft_until_manual_confirmation(self):
        result = create_founder_memory(
            self.conn, "库存判断", "库存偏高", "先控制采购", "不能只看销售", "同时看库存和价格体系",
            created_by=1, source_type="founder_input", source_id="FOUNDER-MEM-001", source_ref="Founder人工输入：库存判断",
        )
        row = self.conn.execute("select * from founder_memories where memory_id=?", (result["memory_id"],)).fetchone()
        self.assertEqual(row["status"], "draft")
        self.assertEqual(row["access_scope"], "owner")
        confirm_founder_memory(self.conn, result["memory_id"], 1)
        self.assertEqual(self.conn.execute("select status from founder_memories where memory_id=?", (result["memory_id"],)).fetchone()[0], "confirmed")

    def test_summary_separates_fact_founder_and_evidence_backed_ai(self):
        self.conn.execute("insert into enterprise_objects values(1,null)")
        self.conn.execute("insert into sync_runs values(1,'success',100,200)")
        self.conn.execute("insert into decision_insights values(1,'有依据建议','摘要','high','new','[{\"source\":\"data_core\"}]',300)")
        self.conn.execute("insert into decision_insights values(2,'无依据建议','摘要','high','new','',300)")
        payload = enterprise_brain_summary(self.conn)
        self.assertEqual(payload["facts"]["sync"]["updated_at"], 200)
        self.assertEqual(payload["ai_analysis"]["total"], 2)
        self.assertEqual(payload["ai_analysis"]["with_evidence"], 1)
        self.assertFalse(payload["sap_write"])

    def test_asset_map_keeps_metric_evidence(self):
        self.conn.execute("insert into enterprise_objects values(1,null)")
        payload = enterprise_asset_map(self.conn)
        enterprise = next(item for item in payload["assets"] if item["key"] == "enterprise_objects")
        self.assertEqual(enterprise["count"], 1)
        self.assertEqual(enterprise["evidence"]["source_type"], "enterprise_objects")
        self.assertIn("不直接连接 SAP", payload["source_policy"])

    def test_timeline_keeps_fact_founder_and_ai_categories_separate(self):
        self.conn.execute("insert into timeline_events values(1,'门店事件','','开业','enterprise_objects','1',100,100)")
        self.conn.execute("insert into timeline_events values(2,'无来源事件','','不应进入','','',110,110)")
        create_founder_memory(
            self.conn, "Founder判断", "背景", "判断", created_by=1, occurred_at=120,
            source_type="founder_input", source_id="FM-1", source_ref="Founder人工输入",
        )
        self.conn.execute("insert into decision_insights values(1,'AI建议','摘要','medium','new','[{\"source\":\"fact\"}]',130)")
        events = enterprise_timeline(self.conn)["events"]
        self.assertEqual({event["kind"] for event in events}, {"enterprise_event", "founder_memory", "ai_advice"})
        self.assertNotIn("无来源事件", [event["title"] for event in events])

    def test_portal_exposes_six_ceo_modules_and_manual_write_routes(self):
        portal = (Path(__file__).resolve().parents[1] / "portal_v2.py").read_text(encoding="utf-8")
        for marker in (
            'path == "/enterprise-brain"',
            'path == "/enterprise-constitution"',
            'path == "/founder-memory"',
            'path == "/enterprise-timeline"',
            'path == "/enterprise-asset-map"',
            'path == "/ceo-decision-center"',
            'path.startswith("/api/enterprise-brain/")',
            "def require_ceo_brain_user",
        ):
            self.assertIn(marker, portal)
        self.assertIn('user["role"] not in ("boss", "admin")', portal)


if __name__ == "__main__":
    unittest.main()
