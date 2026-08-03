from services.business.aggregation import product_analysis


def test_product_analysis_uses_live_rows_and_never_exposes_brand_code():
    result = product_analysis(
        {"products": [{"sku": "A", "name": "冲锋衣", "brand_name": "KAILAS", "brand_code": "K", "category": "服装"}]},
        {"sales": [{"sku": "A", "amount": 100, "period": "current"}, {"sku": "A", "amount": 80, "period": "previous"}]},
        {"inventory": [{"sku": "A", "quantity": 2, "unit_cost": 30}]},
    )
    assert result["brands"][0] == {"brand_name": "KAILAS", "sales_amount": 100.0, "sku_count": 1, "inventory_amount": 60.0, "sales_share": 1.0, "movement_status": "动销"}
    assert "brand_code" not in str(result)
    assert result["categories"][0]["trend"] == 25.0


def test_untrusted_cost_is_governed_instead_of_inferred():
    result = product_analysis({"products": [{"sku": "A"}]}, {"sales": []}, {"inventory": [{"sku": "A", "quantity": 2}]})
    assert result["cost_status"] == "governing"
    assert result["cost_message"] == "成本数据治理中。"
