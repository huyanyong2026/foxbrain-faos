import sqlite3
import tempfile
import unittest
from pathlib import Path

from foxbrain_os.life_import import (
    approve_import,
    ensure_life_import_schema,
    import_batch_detail,
    life_object_allowed,
    rollback_import,
    stage_import_bytes,
    update_import_mapping,
)
from foxbrain_os.living_enterprise import ensure_living_enterprise_schema


def utf16_tsv(rows):
    return ("\r\n".join("\t".join(row) for row in rows) + "\r\n").encode("utf-16")


class LifeImportTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "life-import"
        self.conn = sqlite3.connect(Path(self.temp.name) / "test.db")
        self.conn.row_factory = sqlite3.Row
        ensure_life_import_schema(self.conn)

    def tearDown(self):
        self.conn.close()
        self.temp.cleanup()

    def supplier_file(self):
        return utf16_tsv([
            ["业务伙伴代码", "业务伙伴名称", "组名称", "电话 1", "联系人", "地址", "合作时间"],
            ["V001", "示例供应商", "供应商", "13800000000", "张三", "深圳", "2025-01-01"],
        ])

    def test_stage_preserves_original_and_requires_review(self):
        result = stage_import_bytes(
            self.conn, self.supplier_file(), "供应商资料.xls", "supplier_life", self.root, 1, "2026-07-14"
        )
        self.conn.commit()
        self.assertFalse(result["duplicate"])
        batch = result["batch"]
        self.assertEqual(batch["status"], "review_required")
        self.assertEqual(batch["row_count"], 1)
        self.assertEqual(batch["error_count"], 0)
        self.assertTrue(Path(batch["stored_path"]).is_file())
        self.assertEqual(Path(batch["stored_path"]).read_bytes(), self.supplier_file())
        self.assertEqual(self.conn.execute("select count(*) from living_objects").fetchone()[0], 0)

    def test_same_file_is_reported_without_silent_overwrite(self):
        first = stage_import_bytes(
            self.conn, self.supplier_file(), "供应商资料.xls", "supplier_life", self.root, 1
        )
        second = stage_import_bytes(
            self.conn, self.supplier_file(), "第二次上传.xls", "supplier_life", self.root, 1
        )
        self.assertTrue(second["duplicate"])
        self.assertEqual(second["batch"]["batch_id"], first["batch"]["batch_id"])
        self.assertEqual(self.conn.execute("select count(*) from life_import_batches").fetchone()[0], 1)

    def test_errors_block_approval(self):
        data = utf16_tsv([
            ["物料编号", "物料描述", "制造商名称", "组名称"],
            ["P001", "示例产品一", "KAILAS", "服装"],
            ["P001", "示例产品二", "KAILAS", "服装"],
        ])
        staged = stage_import_bytes(self.conn, data, "物料查询.xls", "product_life", self.root, 1)
        self.assertEqual(staged["batch"]["error_count"], 1)
        with self.assertRaisesRegex(ValueError, "仍有错误行"):
            approve_import(self.conn, staged["batch"]["batch_id"], 1, True)
        self.assertEqual(self.conn.execute("select count(*) from living_objects").fetchone()[0], 0)

    def test_warning_requires_explicit_confirmation(self):
        data = utf16_tsv([
            ["FUserCode", "FUserName"],
            ["1", "店长"],
        ])
        staged = stage_import_bytes(self.conn, data, "员工.xls", "people_life", self.root, 1)
        self.assertEqual(staged["batch"]["warning_count"], 1)
        detail = import_batch_detail(self.conn, staged["batch"]["batch_id"])
        codes = {item["code"] for item in detail["batch"]["rows"][0]["validation"]}
        self.assertIn("possible_shared_account", codes)
        with self.assertRaisesRegex(ValueError, "必须勾选确认"):
            approve_import(self.conn, staged["batch"]["batch_id"], 1, False)

    def test_manual_mapping_rechecks_custom_sap_headers(self):
        data = utf16_tsv([
            ["供应商代号", "供应商全称", "业务联系人", "联系电话", "联系地址", "开始合作"],
            ["V002", "自定义字段供应商", "李四", "13900000000", "深圳", "2024-01-01"],
        ])
        staged = stage_import_bytes(self.conn, data, "供应商自定义字段.xls", "supplier_life", self.root, 1)
        self.assertEqual(staged["batch"]["error_count"], 1)
        result = update_import_mapping(self.conn, staged["batch"]["batch_id"], {
            "supplier_code": "供应商代号", "supplier_name": "供应商全称",
            "contact": "业务联系人", "phone": "联系电话", "address": "联系地址",
            "cooperation_start": "开始合作",
        }, 1)
        self.assertEqual(result["errors"], 0)
        self.assertEqual(result["warnings"], 0)
        approved = approve_import(self.conn, staged["batch"]["batch_id"], 1)
        self.assertEqual(approved["created"], 1)

    def test_approval_creates_traceable_object_and_rollback_is_safe(self):
        staged = stage_import_bytes(
            self.conn, self.supplier_file(), "供应商资料.xls", "supplier_life", self.root, 1, "2026-07-14"
        )
        batch_id = staged["batch"]["batch_id"]
        result = approve_import(self.conn, batch_id, 2, True)
        self.assertEqual(result["created"], 1)
        obj = self.conn.execute("select * from living_objects where object_ref_id='V001'").fetchone()
        self.assertIsNotNone(obj)
        self.assertEqual(obj["object_type"], "supplier_life")
        self.assertEqual(
            self.conn.execute(
                "select count(*) from living_object_sources where life_id=? and source_id=?",
                (obj["life_id"], batch_id),
            ).fetchone()[0],
            5,
        )
        rolled_back = rollback_import(self.conn, batch_id, 2)
        self.assertEqual(rolled_back["rolled_back"], 1)
        self.assertIsNone(self.conn.execute("select 1 from living_objects where life_id=?", (obj["life_id"],)).fetchone())
        self.assertEqual(
            self.conn.execute("select status from life_import_batches where batch_id=?", (batch_id,)).fetchone()[0],
            "rolled_back",
        )
        self.assertTrue(Path(staged["batch"]["stored_path"]).is_file())

    def test_product_life_and_exact_brand_relationship(self):
        self.conn.execute(
            """insert into living_objects(
            life_id,object_type,object_ref_type,object_ref_id,display_name,identity_json,origin_json,state_json,
            future_json,status,version,created_at,updated_at) values(
            'LIFE-BRAND-KAILAS','brand_life','brand_life_profile','KAILAS','KAILAS','{}','{}','{}','{}','active',1,1,1)"""
        )
        data = utf16_tsv([
            ["物料编号", "物料描述", "制造商名称", "组名称", "存货量", "采购价", "会员价"],
            ["P001", "冲锋衣", "KAILAS", "服装", "12", "500", "899"],
        ])
        staged = stage_import_bytes(self.conn, data, "物料查询.xls", "product_life", self.root, 1)
        result = approve_import(self.conn, staged["batch"]["batch_id"], 1, True)
        self.assertEqual(result["created"], 1)
        product = self.conn.execute("select * from living_objects where object_type='product_life'").fetchone()
        self.assertIsNotNone(product)
        relation = self.conn.execute(
            "select * from living_relationships where from_life_id=? and to_life_id='LIFE-BRAND-KAILAS'",
            (product["life_id"],),
        ).fetchone()
        self.assertEqual(relation["relationship_type"], "belongs_to_brand")

    def test_permission_matrix_limits_sensitive_objects(self):
        self.assertTrue(life_object_allowed("boss", "supplier_life"))
        self.assertTrue(life_object_allowed("purchasing", "supplier_life"))
        self.assertFalse(life_object_allowed("employee", "supplier_life"))
        self.assertTrue(life_object_allowed("employee", "product_life"))
        self.assertTrue(life_object_allowed("store_manager", "people_life", {"store": "南山店"}, "南山店"))
        self.assertFalse(life_object_allowed("store_manager", "people_life", {"store": "振兴店"}, "南山店"))

    def test_portal_exposes_reviewed_import_routes(self):
        repo = Path(__file__).resolve().parents[1]
        portal = (repo / "portal_v2.py").read_text(encoding="utf-8")
        requirements = (repo / "requirements.txt").read_text(encoding="utf-8")
        for marker in (
            'path == "/admin/import"',
            'path == "/api/life-import"',
            'path == "/api/life-import/upload"',
            'path == "/api/life-import/mapping"',
            'path == "/api/life-import/approve"',
            'path == "/api/life-import/rollback"',
            "def life_import_center_page",
        ):
            self.assertIn(marker, portal)
        self.assertIn("openpyxl==3.1.5", requirements)
        self.assertIn("xlrd==2.0.1", requirements)

    def test_product_life_schema_migration_preserves_existing_objects(self):
        legacy = sqlite3.connect(":memory:")
        legacy.row_factory = sqlite3.Row
        legacy.execute(
            """create table living_objects(
            id integer primary key autoincrement,life_id text not null unique,
            object_type text not null check(object_type in ('store_life','people_life','brand_life','supplier_life','explorer_life')),
            object_ref_type text not null,object_ref_id text not null,display_name text not null,
            identity_json text not null default '{}',origin_json text not null default '{}',
            state_json text not null default '{}',future_json text not null default '{}',
            status text not null default 'active',version integer not null default 1,
            created_at integer not null,updated_at integer not null,
            unique(object_type,object_ref_type,object_ref_id))"""
        )
        legacy.execute(
            """insert into living_objects(
            life_id,object_type,object_ref_type,object_ref_id,display_name,created_at,updated_at)
            values('LIFE-OLD','supplier_life','sap_export','OLD-1','旧供应商',1,1)"""
        )
        ensure_living_enterprise_schema(legacy)
        self.assertEqual(legacy.execute("select display_name from living_objects").fetchone()[0], "旧供应商")
        sql = legacy.execute("select sql from sqlite_master where name='living_objects'").fetchone()[0]
        self.assertIn("product_life", sql)
        legacy.close()


if __name__ == "__main__":
    unittest.main()
