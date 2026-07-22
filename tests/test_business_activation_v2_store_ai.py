import unittest

from foxbrain_os.business_activation_v2_store_ai import (
    StoreAIContext,
    agent_collaboration_flow,
    ai_task_center_for_store,
    authorize_store_ai,
    ceo_store_intelligence_overview,
    inventory_assistant,
    recommend_wecom_sales_equipment,
    sales_intelligence,
    store_ai_assistant_v2,
    store_daily_briefing,
    store_employee_ai_assistant,
    store_health_score,
    visual_merchandising_ai,
)


FACTS = [
    {"store_code": "nanshan", "store_name": "Nanshan", "sku": "OSPREY-26", "product_name": "Osprey 26L Pack", "brand": "Osprey", "inventory_qty": 1, "incoming_qty": 0, "sales_30d": 12, "sales_prev_30d": 5, "sales_90d": 30, "aging_days": 5, "sales_amount_30d": 7200, "task_status": "done"},
    {"store_code": "nanshan", "store_name": "Nanshan", "sku": "SHOE-HIKE", "product_name": "Hiking Footwear", "brand": "LOWA", "inventory_qty": 9, "incoming_qty": 1, "sales_30d": 18, "sales_prev_30d": 8, "sales_90d": 42, "aging_days": 15, "sales_amount_30d": 18000, "task_status": "open"},
    {"store_code": "zhenxing", "store_name": "Zhenxing", "sku": "KAILAS-VEST", "product_name": "KAILAS Vest", "brand": "KAILAS", "inventory_qty": 20, "incoming_qty": 0, "sales_30d": 1, "sales_prev_30d": 2, "sales_90d": 3, "aging_days": 220, "sales_amount_30d": 900},
]


class BusinessActivationV2StoreAITests(unittest.TestCase):
    PRODUCT_DOMAIN = [
        {"sku": "KAILAS-GTX-JKT", "product_name": "KAILAS GTX 冲锋衣", "brand": "KAILAS", "category": "冲锋衣", "price": 2999},
        {"sku": "KAILAS-HIKE-BOOT", "product_name": "KAILAS 徒步鞋", "brand": "KAILAS", "category": "徒步鞋", "price": 1899},
        {"sku": "OSPREY-38", "product_name": "Osprey 38L 背包", "brand": "Osprey", "category": "背包", "price": 1599},
        {"sku": "GHOST-SHELL", "product_name": "不存在于库存的冲锋衣", "brand": "KAILAS", "category": "冲锋衣", "price": 100},
    ]
    INVENTORY_DOMAIN = [
        {"sku": "KAILAS-GTX-JKT", "available_qty": 3, "store_code": "nanshan", "updated_at": "2026-07-22T09:00:00Z"},
        {"sku": "KAILAS-HIKE-BOOT", "available_qty": 2, "store_code": "nanshan", "updated_at": "2026-07-22T09:00:00Z"},
        {"sku": "OSPREY-38", "available_qty": 4, "store_code": "nanshan", "updated_at": "2026-07-22T09:00:00Z"},
    ]

    def test_chuanxi_sales_recommendation_is_grounded_in_product_inventory_and_brand_domains(self):
        response = recommend_wecom_sales_equipment(
            "川西7天 预算10000 KAILAS",
            self.PRODUCT_DOMAIN,
            self.INVENTORY_DOMAIN,
            [{"brand": "KAILAS", "positioning": "高海拔徒步装备"}],
        )
        self.assertIn("川西", response["customer_scenario_analysis"]["analysis"])
        self.assertEqual(response["domains_consulted"], ["Product Domain", "Inventory Domain", "Brand Knowledge"])
        self.assertEqual([item["sku"] for item in response["recommended_equipment"]], ["KAILAS-GTX-JKT", "KAILAS-HIKE-BOOT"])
        self.assertNotIn("GHOST-SHELL", [item["sku"] for item in response["recommended_equipment"]])
        self.assertTrue(all(item["inventory"]["available_qty"] > 0 for item in response["recommended_equipment"]))
        self.assertEqual(response["combination_amount"], 4898)
        self.assertTrue(response["sales_advice"])
        self.assertTrue(response["cross_sell_opportunities"])

    def test_inventory_match_and_price_boundary_do_not_create_or_over_budget_products(self):
        response = recommend_wecom_sales_equipment("川西7天 预算3000", self.PRODUCT_DOMAIN, self.INVENTORY_DOMAIN)
        self.assertLessEqual(response["combination_amount"], 3000)
        self.assertIn("徒步鞋（超出预算）", response["missing_equipment"])
        no_match = recommend_wecom_sales_equipment("川西7天", [{"sku": "NO-STOCK", "product_name": "无库存冲锋衣", "category": "冲锋衣", "price": 999}], [])
        self.assertTrue(no_match["no_match"])
        self.assertIn("未在 VAFOX 商品与库存数据中", no_match["no_match_reason"])

    def test_daily_briefing_health_sales_inventory_and_tasks(self):
        briefing = store_daily_briefing(FACTS, "nanshan")
        self.assertEqual(briefing["store_status"], "Good")
        self.assertIn("sales_summary", briefing)
        self.assertEqual(briefing["inventory_risk"]["type"], "low_stock")
        self.assertGreaterEqual(briefing["health"]["health"], 85)

        health = store_health_score(FACTS, "nanshan")
        self.assertIn("customer_experience", health["details"])
        sales = sales_intelligence(FACTS, "nanshan")
        self.assertEqual(sales["top_brand"], "LOWA")
        inventory = inventory_assistant(FACTS, "nanshan")
        self.assertTrue(any(alert["type"] == "low_stock" for alert in inventory["alerts"]))
        tasks = ai_task_center_for_store(FACTS, "nanshan", "amy")
        self.assertTrue(any(task["owner"] == "amy" for task in tasks))

    def test_assistant_wecom_ceo_visual_collaboration_and_security(self):
        manager = StoreAIContext("mgr", ("store_manager",), ("store_ai.read", "store_employee_ai.read"), store_codes=("nanshan",))
        answer = store_ai_assistant_v2("今天南山店重点关注什么？", FACTS, manager, "nanshan")
        self.assertFalse(answer["manual_agent_selection"])
        self.assertIn("Supply Agent", answer["auto_selected_agents"])
        employee = store_employee_ai_assistant("Scarpa和LOWA区别？", FACTS, manager, "nanshan")
        self.assertEqual(employee["channel"], "WeCom AI")
        with self.assertRaises(PermissionError):
            authorize_store_ai(manager, "store_ai.read", store_code="zhenxing")

        ceo = StoreAIContext("ceo", ("ceo",), ("*",))
        overview = ceo_store_intelligence_overview(FACTS, ceo)
        self.assertEqual(overview["view"], "Store Intelligence Overview")
        visual = visual_merchandising_ai({"photo_id": "p1", "brand": "KAILAS", "front_exposure_score": 60}, "nanshan")
        self.assertIn("Improve", visual["display_recommendation"])
        flow = agent_collaboration_flow("Customer demand increase", FACTS, "nanshan")
        self.assertIn("Commerce Agent", flow["flow"])


if __name__ == "__main__":
    unittest.main()
