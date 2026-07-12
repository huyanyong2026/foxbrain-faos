import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "scripts" / "sap_lab_analyzer.py"
SPEC = importlib.util.spec_from_file_location("sap_lab_analyzer", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class SapLabAnalyzerTest(unittest.TestCase):
    def test_table_classification_and_object_mapping(self):
        self.assertEqual(MODULE.classify_table("OITM"), "product")
        self.assertEqual(MODULE.classify_table("@CUSTOM"), "user_defined")
        mappings = MODULE.object_suggestions("OCRD")
        self.assertEqual({item["foxbrain_object"] for item in mappings}, {"supplier", "customer"})
        self.assertTrue(all(item["requires_human_confirmation"] for item in mappings))

    def test_hash_is_stable_and_sensitive(self):
        first = MODULE.stable_hash(["Code"], [(1,), (2,)])
        self.assertEqual(first, MODULE.stable_hash(["Code"], [(1,), (2,)]))
        self.assertNotEqual(first, MODULE.stable_hash(["Code"], [(2,), (1,)]))

    def test_checkpoint_schema(self):
        import tempfile
        with tempfile.TemporaryDirectory() as directory:
            state = MODULE.init_state(Path(directory) / "state.db")
            state.execute(
                "insert into table_progress values(?,?,?,?,?,?,?,?)",
                ("OITM", "completed", 10, 3, "abc", 1, 1, ""),
            )
            state.commit()
            result = state.execute(
                "select status from table_progress where table_name='OITM'"
            ).fetchone()[0]
            self.assertEqual(result, "completed")
            state.close()


if __name__ == "__main__":
    unittest.main()
