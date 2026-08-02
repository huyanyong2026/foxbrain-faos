from services.business.data_validation import ACTIVE_STORES, build_consistency_report, filter_inventory, reconcile_invoice_lines, store_code


def test_only_five_current_operating_units_are_accepted():
    assert list(ACTIVE_STORES.values()) == ["航苑店", "南山店", "振兴店", "金沙店", "网店"]
    assert store_code("成都金沙店") == "jinsha"
    assert store_code("武侯祠店") is None
    assert store_code("历史一店") is None


def test_effective_inventory_rule_and_history_sku_label():
    rows = [
        {"store": "南山店", "sku": "stock", "inventory": 1},
        {"store": "网店", "sku": "sale", "inventory": 0, "last_sale_date": "2026-01-01"},
        {"store": "金沙店", "sku": "purchase", "inventory": 0, "last_purchase_date": "2026-08-01"},
        {"store": "振兴店", "sku": "history", "inventory": 0, "last_sale_date": "2025-12-31"},
        {"store": "武侯祠店", "sku": "excluded-store", "inventory": 9},
    ]
    result = filter_inventory(rows)
    assert {row["sku"] for row in result["effective"]} == {"stock", "sale", "purchase"}
    assert result["history"] == [{"store": "振兴店", "sku": "history", "inventory": 0, "last_sale_date": "2025-12-31", "store_code": "zhenxing", "store_name": "振兴店", "classification": "HISTORY_SKU"}]


def test_full_chain_must_match_for_trusted_status():
    layers = {name: {"sales": 50, "inventory": 40, "stores": 5, "customers": 30} for name in ("sap_b1", "mirror", "data_core", "ceo_api", "dashboard")}
    assert build_consistency_report(layers)["status"] == "trusted"
    layers["dashboard"]["inventory"] = 39
    report = build_consistency_report(layers)
    assert report["status"] == "mismatch" and not report["checks"]["inventory"]["consistent"]


def test_online_aliases_are_active_and_invoice_line_difference_is_explained():
    assert store_code("网店") == store_code("线上店") == store_code("ONLINE STORE") == "online"
    result = reconcile_invoice_lines(
        [{"DocEntry": 1, "DocTotal": 402215, "CANCELED": "N"}, {"DocEntry": 2, "DocTotal": 99, "CANCELED": "Y"}],
        [{"DocEntry": 1, "LineTotal": 400000}, {"DocEntry": 2, "LineTotal": 99}],
    )
    assert result["oinv_document_total"] == 402215
    assert result["inv1_sales_line_total"] == 400000
    assert result["settlement_components"] == 2215
    assert result["orphan_or_cancelled_line_documents"] == ["2"] and result["read_only"]
