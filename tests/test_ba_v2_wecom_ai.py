import unittest

from apps.ai.identity import (
    EMPLOYEE_AI_ROLE_CAPABILITIES,
    WECOM_IDENTITY_TYPES,
    compose_employee_ai_response,
    create_ai_task_from_signal,
    map_wecom_identity,
    role_capabilities,
)


EVIDENCE = [{
    "source_layer": "core",
    "source_type": "core.vafox.com",
    "source_id": "INV-NANSHAN-OSPREY-26L",
    "source_ref": "https://core.vafox.com/inventory/INV-NANSHAN-OSPREY-26L",
    "statement": "南山店 Osprey 26L 库存来自 Core 企业数据只读结果",
}]


class BusinessActivationV2WeComAITest(unittest.TestCase):
    def test_wecom_identity_types_cover_required_roles(self):
        self.assertEqual(set(WECOM_IDENTITY_TYPES), {"employee", "store_manager", "purchaser", "ceo"})
        self.assertIn("basic_inventory", EMPLOYEE_AI_ROLE_CAPABILITIES["employee"]["access"])
        self.assertIn("purchase_recommendation", EMPLOYEE_AI_ROLE_CAPABILITIES["purchaser"]["access"])

    def test_wecom_user_maps_to_foxbrain_identity_permissions_and_scope(self):
        mapping = map_wecom_identity("zhangsan", 101, ["store_manager"], store_id=7)
        self.assertEqual(mapping["identity_type"], "store_manager")
        self.assertIn("store.read", mapping["permissions"])
        self.assertEqual(mapping["data_scopes"], [{"type": "store", "value": "7"}])

    def test_role_intelligence_merges_employee_workspace_capabilities(self):
        caps = role_capabilities(["employee", "purchaser"])
        self.assertIn("product", caps["access"])
        self.assertIn("forecast", caps["access"])
        self.assertIn("supply_chain", caps["agents"])
        self.assertEqual(caps["scope"], "company_supply_chain")

    def test_employee_ai_response_preserves_core_source_and_update_time(self):
        mapping = map_wecom_identity("lisi", 102, ["employee"])
        response = compose_employee_ai_response(
            "南山店 Osprey 26L库存？",
            mapping,
            {
                "product": "Osprey 26L",
                "store": "南山店",
                "inventory": "现货 8 件，可售 7 件",
                "data_source": "core.vafox.com",
                "update_time": "2026-07-16T09:30:00Z",
            },
        )
        self.assertEqual(response["action_policy"], "assistant_recommendation_only")
        self.assertEqual(response["data_source"], "core.vafox.com")
        self.assertEqual(response["update_time"], "2026-07-16T09:30:00Z")

    def test_task_assistant_creates_approval_gated_task_from_ai_signal(self):
        task = create_ai_task_from_signal({
            "title": "Check Nanshan inventory",
            "description": "AI detected Osprey 26L inventory mismatch.",
            "source_id": "SIG-1",
            "source_ref": "https://ai.vafox.com/signals/SIG-1",
            "evidence": EVIDENCE,
        })
        self.assertEqual(task["status"], "pending_approval")
        self.assertEqual(task["assignee_role"], "store_manager")
        self.assertEqual(task["evidence"][0]["source_type"], "core.vafox.com")


if __name__ == "__main__":
    unittest.main()
