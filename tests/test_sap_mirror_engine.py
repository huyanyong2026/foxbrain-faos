import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("mirror", ROOT / "scripts" / "sap_mirror_engine.py")
MIRROR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MIRROR)


class MirrorEngineTest(unittest.TestCase):
    def test_ddl_types_cover_sap_2008_types(self):
        self.assertEqual(MIRROR.ddl_type(("Code", "nvarchar", 40, 0, 0, 0)), "nvarchar(20)")
        self.assertEqual(MIRROR.ddl_type(("Amount", "numeric", 17, 19, 6, 0)), "numeric(19,6)")
        self.assertEqual(MIRROR.ddl_type(("Blob", "image", 16, 0, 0, 1)), "image")

    def test_primary_key_order_is_preferred(self):
        columns = [("DocEntry", "int", 4, 10, 0, 0), ("LineNum", "int", 4, 10, 0, 0)]
        self.assertEqual(MIRROR.order_expression(columns, ["DocEntry", "LineNum"]), "[DocEntry],[LineNum]")

    def test_composite_keyset_predicate(self):
        sql, params = MIRROR.keyset_predicate(["ItemCode", "PriceList"], ["A100", 3])
        self.assertEqual(sql, "([ItemCode]>%s) or ([ItemCode]=%s and [PriceList]>%s)")
        self.assertEqual(params, ["A100", "A100", 3])

    def test_live_growth_is_reconciled_against_ending_count(self):
        self.assertTrue(MIRROR.row_counts_reconciled(101, 101))
        self.assertFalse(MIRROR.row_counts_reconciled(101, 100))

    def test_missing_key_detection_preserves_source_order(self):
        class Cursor:
            def execute(self, sql, params):
                self.sql = sql
                self.params = params
            def fetchall(self):
                return [("A", 1), ("C", 1)]
        cursor = Cursor()
        missing = MIRROR.missing_keys_in_batch(
            cursor,
            "dbo",
            "OITW",
            ["ItemCode", "WhsCode"],
            [("A", 1), ("B", 1), ("C", 1)],
        )
        self.assertEqual(missing, [("B", 1)])
        self.assertEqual(cursor.params, ("A", 1, "B", 1, "C", 1))

    def test_target_key_index_uses_source_primary_key(self):
        class Connection:
            def commit(self):
                self.committed = True
        class Cursor:
            def __init__(self):
                self.calls = []
                self.connection = Connection()
            def execute(self, sql, params=None):
                self.calls.append((sql, params))
            def fetchone(self):
                return (0,)
        cursor = Cursor()
        MIRROR.ensure_target_key_index(
            cursor, "dbo", "OITW", ["ItemCode", "WhsCode"]
        )
        self.assertIn("create unique nonclustered index", cursor.calls[1][0])
        self.assertIn("[ItemCode],[WhsCode]", cursor.calls[1][0])

    def test_multi_row_insert_respects_parameter_limit(self):
        class Cursor:
            def __init__(self):
                self.calls = []
            def execute(self, sql, params):
                self.calls.append((sql, params))
        cursor = Cursor()
        rows = [tuple(range(15)) for _ in range(300)]
        MIRROR.insert_rows(cursor, "dbo", "ITM1", [f"c{i}" for i in range(15)], rows)
        self.assertEqual(len(cursor.calls), 3)
        self.assertTrue(all(len(params) <= 2000 for _, params in cursor.calls))

    def test_multi_row_insert_batches_wide_sap_tables(self):
        class Cursor:
            def __init__(self):
                self.calls = []
            def execute(self, sql, params):
                self.calls.append((sql, params))
        cursor = Cursor()
        rows = [tuple(range(160)) for _ in range(25)]
        MIRROR.insert_rows(cursor, "dbo", "OITW", [f"c{i}" for i in range(160)], rows)
        self.assertEqual(len(cursor.calls), 3)
        self.assertTrue(all(len(params) <= 2000 for _, params in cursor.calls))

    def test_binary_text_tables_are_explicit(self):
        self.assertEqual(MIRROR.BINARY_TEXT_TABLES, {"OCPC", "OFRM", "OHMM", "OULA"})

    def test_binary_text_expression_supports_legacy_lob_types(self):
        self.assertEqual(
            MIRROR.binary_text_expression("Notes", "ntext"),
            "convert(varbinary(max),convert(nvarchar(max),[Notes])) as [Notes]",
        )
        self.assertEqual(
            MIRROR.binary_text_expression("Body", "text"),
            "convert(varbinary(max),convert(varchar(max),[Body])) as [Body]",
        )
        self.assertEqual(
            MIRROR.binary_text_expression("Name", "nvarchar"),
            "convert(varbinary(max),[Name]) as [Name]",
        )

    def test_checkpoint_schema_is_persistent(self):
        with tempfile.TemporaryDirectory() as directory:
            state = MIRROR.init_state(Path(directory) / "state.db")
            state.execute("insert into progress values(?,?,?,?,?,?,?)", ("dbo.OITM", "running", 10, 0, 3, 1, ""))
            state.commit()
            self.assertEqual(state.execute("select copied_rows from progress where table_name='dbo.OITM'").fetchone()[0], 3)
            state.close()

    def test_incomplete_tables_are_processed_first(self):
        with tempfile.TemporaryDirectory() as directory:
            state = MIRROR.init_state(Path(directory) / "state.db")
            state.execute(
                "insert into progress values(?,?,?,?,?,?,?)",
                ("dbo.OITW", "running", 10, 0, 3, 1, ""),
            )
            state.commit()
            tables = [("dbo", "OITM"), ("dbo", "OINV"), ("dbo", "OITW")]
            self.assertEqual(
                MIRROR.prioritize_incomplete_tables(tables, state)[0],
                ("dbo", "OITW"),
            )
            state.close()


if __name__ == "__main__":
    unittest.main()
