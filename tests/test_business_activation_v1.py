import unittest

from foxbrain_os.business_activation_v1 import (
    BusinessActivationContext,
    ceo_dashboard,
    daily_ceo_briefing,
    export_report_csv,
    inventory_health_score,
    overstock_intelligence,
    replenishment_recommendations,
    risk_radar,
    store_ai_assistant,
    store_dashboard,
    supply_chain_dashboard,
    wecom_ai_query,
)


FACTS = [
    {"store_code": "nanshan", "store_name": "Nanshan", "sku": "KAILAS-GTX", "product_name": "KAILAS GTX Jacket", "brand": "KAILAS", "inventory_qty": 3, "incoming_qty": 0, "sales_30d": 15, "sales_prev_30d": 6, "sales_90d": 25, "aging_days": 20, "unit_cost": 500, "sales_amount_30d": 15000, "gross_margin_30d": 6000},
    {"store_code": "nanshan", "store_name": "Nanshan", "sku": "OSPREY-OLD", "product_name": "Osprey Old Pack", "brand": "Osprey", "inventory_qty": 20, "incoming_qty": 0, "sales_30d": 0, "sales_prev_30d": 1, "sales_90d": 1, "aging_days": 300, "unit_cost": 300, "sales_amount_30d": 500, "gross_margin_30d": 100},
    {"store_code": "hangyuan", "store_name": "Hangyuan", "sku": "OSPREY-FAST", "product_name": "Osprey Fast Pack", "brand": "Osprey", "inventory_qty": 10, "incoming_qty": 2, "sales_30d": 12, "sales_prev_30d": 20, "sales_90d": 50, "aging_days": 10, "unit_cost": 250, "sales_amount_30d": 8000, "gross_margin_30d": 3000},
]


class BusinessActivationV1Tests(unittest.TestCase):
    def test_supply_chain_replenishment_and_overstock(self):
        repl = replenishment_recommendations(FACTS)
        self.assertEqual(repl[0]["product"], "KAILAS GTX Jacket")
        self.assertEqual(repl[0]["suggested_quantity"], 12)
        overstock = overstock_intelligence(FACTS)
        self.assertEqual(overstock[0]["recommendation"], "clearance")

    def test_inventory_health_and_dashboard(self):
        health = inventory_health_score(FACTS)
        nanshan = next(item for item in health if item["store_code"] == "nanshan")
        self.assertEqual(nanshan["risk"], {"low_stock": 1, "overstock": 1})
        dashboard = supply_chain_dashboard(FACTS)
        self.assertIn("replenishment_tasks", dashboard)
        self.assertIn("brand_status", dashboard)

    def test_ceo_command_center_outputs(self):
        dashboard = ceo_dashboard(FACTS)
        self.assertEqual(dashboard["sales"], 23500)
        brief = daily_ceo_briefing(FACTS)
        self.assertTrue(brief["requires_human_approval"])
        radar = risk_radar(FACTS)
        self.assertGreaterEqual(radar["inventory_risk"], 2)

    def test_wecom_respects_store_scope(self):
        context = BusinessActivationContext("u1", ("store_manager",), ("knowledge.read",), "store", ("nanshan",))
        answer = wecom_ai_query("Nanshan Osprey inventory?", FACTS, context)
        self.assertEqual({row["store"] for row in answer["results"]}, {"Nanshan"})
        no_perm = BusinessActivationContext("u2", ("employee",), tuple(), "self", tuple())
        with self.assertRaises(PermissionError):
            wecom_ai_query("inventory", FACTS, no_perm)

    def test_store_center_and_export(self):
        dashboard = store_dashboard(FACTS, "nanshan")
        self.assertEqual(dashboard["inventory_health"]["store_code"], "nanshan")
        assistant = store_ai_assistant("What should Nanshan store focus today?", FACTS, "nanshan")
        self.assertIn("recommended_actions", assistant)
        csv_text = export_report_csv(dashboard["tasks"], "Inventory health report")
        self.assertIn("Inventory health report", csv_text)


if __name__ == "__main__":
    unittest.main()
