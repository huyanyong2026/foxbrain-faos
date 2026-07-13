import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from foxbrain_os.brand_life_engine import (
    LIFE_DIMENSIONS,
    brand_life_payload,
    can_read_brand_knowledge,
    classify_brand_document,
    register_brand_document,
    seed_kailas,
)


class BrandLifeEngineTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.conn = sqlite3.connect(Path(self.temp.name) / "brand.db")
        self.conn.row_factory = sqlite3.Row
        self.brand_id = seed_kailas(self.conn)

    def tearDown(self):
        self.conn.close()
        self.temp.cleanup()

    def test_model_has_ten_life_dimensions(self):
        self.assertEqual(len(LIFE_DIMENSIONS), 10)
        payload = brand_life_payload(self.conn, "KAILAS", "admin")
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["dimensions"], list(LIFE_DIMENSIONS))

    def test_salary_document_gets_four_categories_and_cards(self):
        text = "KAILAS品牌 加盟终端 门店员工薪酬福利 岗位晋升 培训考核标准"
        categories = classify_brand_document("KAILAS终端薪酬福利.pdf", text)
        self.assertEqual(
            {item["category"] for item in categories},
            {"brand_life", "people_life", "store_life", "training_knowledge"},
        )
        source = Path(self.temp.name) / "KAILAS.pdf"
        source.write_bytes(b"test-pdf-evidence")
        result = register_brand_document(
            self.conn, self.brand_id, source.name, str(source), text, confidentiality="sensitive"
        )
        self.conn.commit()
        self.assertTrue(result["ok"])
        self.assertGreater(result["cards"], 0)
        self.assertEqual(
            self.conn.execute("select count(*) from brand_vault_item_categories").fetchone()[0], 4
        )

    def test_sensitive_knowledge_is_owner_only(self):
        self.assertFalse(can_read_brand_knowledge("employee", "sensitive"))
        self.assertTrue(can_read_brand_knowledge("employee", "public"))
        self.assertTrue(can_read_brand_knowledge("boss", "sensitive"))

    def test_duplicate_file_is_not_silently_reimported(self):
        source = Path(self.temp.name) / "same.pdf"
        source.write_bytes(b"same")
        first = register_brand_document(self.conn, self.brand_id, source.name, str(source), "KAILAS品牌")
        second = register_brand_document(self.conn, self.brand_id, source.name, str(source), "KAILAS品牌")
        self.assertFalse(first["duplicate"])
        self.assertTrue(second["duplicate"])
        self.assertEqual(self.conn.execute("select count(*) from brand_knowledge_vault_items").fetchone()[0], 1)


if __name__ == "__main__":
    unittest.main()
