import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
SPEC = importlib.util.spec_from_file_location(
    "mapping_validator", ROOT / "scripts" / "validate_sap_object_mapping.py"
)
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


class SapObjectMappingTest(unittest.TestCase):
    def setUp(self):
        self.mapping = json.loads(
            (ROOT / "config" / "sap_business_object_mappings.json").read_text(encoding="utf-8")
        )

    def test_safety_and_confirmation(self):
        self.assertFalse(self.mapping["safety"]["sap_writes_allowed"])
        self.assertFalse(self.mapping["safety"]["auto_create_objects"])
        self.assertEqual(len(self.mapping["confirmed_mappings"]), 25)

    def test_priority_objects_are_complete(self):
        self.assertEqual(
            set(self.mapping["objects"]), {"product", "brand", "store", "customer", "supplier"}
        )
        for definition in self.mapping["objects"].values():
            self.assertTrue(definition["sources"])
            self.assertTrue(definition["field_mapping"])
            self.assertTrue(definition["business_meaning"])
            self.assertTrue(definition["relationships"])
            self.assertTrue(definition["ai_query_fields"])


if __name__ == "__main__":
    unittest.main()
