import unittest

from foxbrain_os.business_activation_v2_supply_chain import (
    SupplyChainContext,
    ai_task_workflow,
    authorize_supply_chain,
    brand_intelligence,
    demand_forecast,
    huyan_command_center,
    inventory_transfer_suggestions,
    purchase_planning,
    supplier_alerts,
    supply_chain_agent_v2,
)

FACTS = [
    {"store_code": "nanshan", "store_name": "Nanshan Store", "sku": "KAILAS-GTX", "product_name": "KAILAS GTX Jacket", "brand": "KAILAS", "inventory_qty": 3, "incoming_qty": 0, "sales_30d": 15, "sales_prev_30d": 6, "sales_90d": 25, "unit_cost": 500, "sales_amount_30d": 15000, "gross_margin_30d": 6000, "season_factor": 1.1, "supplier_lead_time_days": 21, "safety_stock": 4},
    {"store_code": "zhenxing", "store_name": "Zhenxing Store", "sku": "OSPREY-PACK", "product_name": "Osprey Backpack", "brand": "Osprey", "inventory_qty": 24, "incoming_qty": 0, "sales_30d": 2, "sales_prev_30d": 5, "sales_90d": 8, "unit_cost": 300, "sales_amount_30d": 2000, "gross_margin_30d": 600},
    {"store_code": "nanshan", "store_name": "Nanshan Store", "sku": "OSPREY-PACK", "product_name": "Osprey Backpack", "brand": "Osprey", "inventory_qty": 1, "incoming_qty": 0, "sales_30d": 14, "sales_prev_30d": 7, "sales_90d": 34, "unit_cost": 300, "sales_amount_30d": 9000, "gross_margin_30d": 3500},
]


class BusinessActivationV2SupplyChainTests(unittest.TestCase):
    def test_demand_forecast_outputs_product_store_confidence_and_reason(self):
        forecast = demand_forecast(FACTS)
        kailas = next(item for item in forecast if item["sku"] == "KAILAS-GTX")
        self.assertEqual(kailas["product"], "KAILAS GTX Jacket")
        self.assertEqual(kailas["store"], "Nanshan Store")
        self.assertGreater(kailas["expected_demand"], 15)
        self.assertGreaterEqual(kailas["confidence_score"], 0.7)
        self.assertIn("season", kailas["reason"])

    def test_purchase_planning_is_predictive_and_human_approved(self):
        plans = purchase_planning(FACTS)
        self.assertEqual(plans[0]["brand"], "KAILAS")
        self.assertEqual(plans[0]["purchase_timing"], "order_now")
        self.assertTrue(plans[0]["requires_human_approval"])

    def test_inventory_transfer_between_stores(self):
        transfers = inventory_transfer_suggestions(FACTS)
        osprey = transfers[0]
        self.assertEqual(osprey["from_store"], "Zhenxing Store")
        self.assertEqual(osprey["to_store"], "Nanshan Store")
        self.assertEqual(osprey["product"], "Osprey Backpack")
        self.assertGreater(osprey["quantity"], 0)

    def test_brand_supplier_agent_huyan_workflow_and_security(self):
        brand = brand_intelligence(FACTS)
        self.assertIn("KAILAS", brand)
        supplier = SupplyChainContext("sup1", ("supplier",), ("supplier.brand.read",), brand_scope=("Osprey",))
        alerts = supplier_alerts(FACTS, supplier)
        self.assertTrue(all(alert["brand"] == "Osprey" for alert in alerts))
        with self.assertRaises(PermissionError):
            authorize_supply_chain(supplier, "supplier.brand.read", brand="KAILAS")

        ceo = SupplyChainContext("ceo", ("ceo",), ("*",))
        agent = supply_chain_agent_v2("What should we purchase next month?", FACTS, ceo)
        self.assertEqual(agent["agent"], "Supply Chain Agent V2")
        center = huyan_command_center(FACTS, ceo)
        self.assertIn("Demand Forecast".lower().replace(" ", "_"), center)
        tasks = ai_task_workflow(FACTS)
        self.assertTrue(any(task["task"] == "Notify procurement" for task in tasks))


if __name__ == "__main__":
    unittest.main()
