from services.business.aggregation import inventory_analysis


def test_inventory_analysis_enforces_effective_sku_scope_and_health():
    result = inventory_analysis(
        {"updated_at": "2026-08-03T00:00:00Z", "products": [
            {"sku": "NORMAL", "name": "冲锋衣", "brand": "KAILAS"},
            {"sku": "SLOW", "name": "背包", "brand": "VAFOX"},
            {"sku": "OUT", "name": "徒步鞋", "brand": "LOWA"},
            {"sku": "OLD-ZERO", "name": "旧款"},
            {"sku": "HISTORY", "name": "历史款", "status": "HISTORY SKU"},
        ]},
        {"sales": [
            {"sku": "NORMAL", "quantity": 10, "date": "2026-07-30"},
            {"sku": "OUT", "quantity": 5, "date": "2026-07-31"},
            {"sku": "OLD-ZERO", "quantity": 1, "date": "2025-12-01"},
        ]},
        {"inventory": [
            {"sku": "NORMAL", "quantity": 15, "unit_cost": 100, "store": "南山"},
            {"sku": "SLOW", "quantity": 4, "unit_cost": 200, "store": "网店"},
            {"sku": "OUT", "quantity": 0, "unit_cost": 120, "store": "南山"},
            {"sku": "OLD-ZERO", "quantity": 0, "unit_cost": 10, "store": "振兴"},
            {"sku": "HISTORY", "quantity": 8, "unit_cost": 10, "store": "振兴"},
        ]},
    )
    assert result["scope"]["dataset"] == "effective_skus"
    assert result["overview"]["effective_skus"] == 3
    assert {row["sku"] for row in result["items"]} == {"NORMAL", "SLOW", "OUT"}
    assert result["health"]["正常库存"][0]["sku"] == "NORMAL"
    assert result["health"]["滞销库存"][0]["sku"] == "SLOW"
    assert result["health"]["缺货风险"][0]["sku"] == "OUT"


def test_inventory_analysis_governs_untrusted_cost():
    result = inventory_analysis({"products": [{"sku": "A"}]}, {"sales": []}, {"inventory": [{"sku": "A", "quantity": 2}]})
    assert result["cost_status"] == "governing"
    assert result["cost_message"] == "成本数据治理中"
