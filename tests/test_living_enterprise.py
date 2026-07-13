import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from foxbrain_os.brand_life_engine import seed_kailas
from foxbrain_os.living_enterprise import (
    LIFE_DIMENSIONS,
    LIFE_OBJECT_TYPES,
    add_future_item,
    ensure_living_enterprise_schema,
    living_enterprise_summary,
    living_object_payload,
    record_timeline_event,
    relate_life_objects,
    sync_life_context_links,
    sync_life_objects_from_confirmed_sources,
    upsert_life_object,
)


class LivingEnterpriseTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.conn = sqlite3.connect(Path(self.temp.name) / "living.db")
        self.conn.row_factory = sqlite3.Row
        self.conn.execute(
            """create table enterprise_objects(
            id integer primary key, object_type text, name text, code text, status text,
            metadata text, updated_at integer, archived_at integer)"""
        )
        rows = [
            (1, "store", "南山店", "STORE-NS", "active"),
            (2, "employee", "示例员工", "EMP-001", "active"),
            (3, "brand", "OSPREY", "BRAND-OSPREY", "active"),
            (4, "supplier", "示例供应商", "SUP-001", "active"),
            (5, "customer", "示例探索者", "CUST-001", "active"),
        ]
        self.conn.executemany(
            "insert into enterprise_objects values(?,?,?,?,?,?,?,null)",
            [(row_id, object_type, name, code, status, json.dumps({"confirmed": True}), 1000) for row_id, object_type, name, code, status in rows],
        )
        seed_kailas(self.conn)
        ensure_living_enterprise_schema(self.conn)

    def tearDown(self):
        self.conn.close()
        self.temp.cleanup()

    def test_framework_exposes_eight_dimensions_and_five_types(self):
        self.assertEqual(
            LIFE_DIMENSIONS,
            ("identity", "origin", "timeline", "state", "relationship", "memory", "decision", "future"),
        )
        self.assertEqual(len(LIFE_OBJECT_TYPES), 5)

    def test_portal_exposes_page_api_and_manual_rebuild_hooks(self):
        portal_source = (Path(__file__).resolve().parents[1] / "portal_v2.py").read_text(encoding="utf-8")
        for marker in (
            'path == "/living-enterprise"',
            'path == "/api/living-enterprise"',
            'path == "/api/living-enterprise/rebuild"',
            "def living_enterprise_page",
            "def living_object_page",
            "def api_living_enterprise_rebuild",
        ):
            self.assertIn(marker, portal_source)
        self.assertIn('"enterprise_objects": U(r"\\u4f01\\u4e1a\\u6570\\u5b57\\u6863\\u6848")', portal_source)
        self.assertNotIn('format(item["dimension"], item["source_type"], item["source_ref"])', portal_source)

    def test_source_is_required_for_every_object(self):
        with self.assertRaisesRegex(ValueError, "缺少来源"):
            upsert_life_object(
                self.conn,
                "store_life",
                "enterprise_object",
                "1",
                "南山店",
            )

    def test_sync_builds_all_first_batch_types_and_brand_life(self):
        result = sync_life_objects_from_confirmed_sources(self.conn)
        self.conn.commit()
        self.assertEqual(result["store_life"], 1)
        self.assertEqual(result["people_life"], 1)
        self.assertEqual(result["supplier_life"], 1)
        self.assertEqual(result["explorer_life"], 1)
        self.assertEqual(result["brand_life"], 2)
        summary = living_enterprise_summary(self.conn)
        self.assertEqual(summary["total_objects"], 6)
        self.assertEqual(summary["objects_without_source"], 0)

    def test_sync_is_idempotent(self):
        first = sync_life_objects_from_confirmed_sources(self.conn)
        second = sync_life_objects_from_confirmed_sources(self.conn)
        self.assertEqual(first["created"], 6)
        self.assertEqual(second["created"], 0)
        self.assertEqual(second["updated"], 0)
        self.assertEqual(second["unchanged"], 6)
        versions = [row[0] for row in self.conn.execute("select version from living_objects").fetchall()]
        self.assertEqual(versions, [1] * 6)

    def test_timeline_relationship_and_future_keep_sources(self):
        sync_life_objects_from_confirmed_sources(self.conn)
        store = self.conn.execute("select life_id from living_objects where object_type='store_life'").fetchone()[0]
        brand = self.conn.execute(
            "select life_id from living_objects where object_type='brand_life' and display_name='OSPREY'"
        ).fetchone()[0]
        source = {
            "source_type": "verified_test_record",
            "source_id": "CASE-001",
            "source_ref": "tests/test_living_enterprise.py#CASE-001",
            "source_time": "2026-07-13",
            "evidence": [{"field": "confirmed", "value": True}],
        }
        record_timeline_event(self.conn, store, "opening", "门店进入经营时间轴", "2026-07-13", **source)
        relate_life_objects(self.conn, store, brand, "operates_brand", **source)
        add_future_item(self.conn, store, "验证下一阶段门店目标", target_date="2026-08-01", **source)
        payload = living_object_payload(self.conn, store)
        self.assertEqual(len(payload["timeline"]), 1)
        self.assertEqual(len(payload["relationships"]), 1)
        self.assertEqual(len(payload["future"]), 1)
        self.assertTrue(payload["future"][0]["approval_required"])
        self.assertEqual(payload["timeline"][0]["source_type"], "verified_test_record")
        dimensions = {row["dimension"] for row in payload["sources"]}
        self.assertTrue({"identity", "origin", "state", "future", "timeline", "relationship"}.issubset(dimensions))

    def test_reviewed_memory_and_evidence_decision_are_linked(self):
        sync_life_objects_from_confirmed_sources(self.conn)
        self.conn.execute(
            """create table enterprise_memories(
            id integer primary key,title text,memory_type text,summary text,status text,
            related_object_type text,related_object_id integer,updated_at integer,archived_at integer)"""
        )
        self.conn.execute(
            "insert into enterprise_memories values(1,'门店复盘','decision','已批准经验','approved','store',1,2000,null)"
        )
        self.conn.execute(
            """create table decision_insights(
            id integer primary key,insight_type text,title text,summary text,status text,
            entity_type text,entity_id integer,evidence text,updated_at integer)"""
        )
        self.conn.execute(
            "insert into decision_insights values(1,'store_risk','门店判断','有依据的建议','new','store',1,'[{\"source\":\"metric\"}]',2000)"
        )
        result = sync_life_context_links(self.conn)
        store = self.conn.execute("select life_id from living_objects where object_type='store_life'").fetchone()[0]
        payload = living_object_payload(self.conn, store)
        self.assertEqual(result["memory_links"], 1)
        self.assertEqual(result["decision_links"], 1)
        self.assertEqual(len(payload["memories"]), 1)
        self.assertEqual(len(payload["decisions"]), 1)
        dimensions = {row["dimension"] for row in payload["sources"]}
        self.assertIn("memory", dimensions)
        self.assertIn("decision", dimensions)


if __name__ == "__main__":
    unittest.main()
