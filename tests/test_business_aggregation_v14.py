from services.business.aggregation import customer_analysis, member_analysis, sales_analysis, supplier_analysis


SALES = {"source": "Data Core", "timestamp": "2026-08-03T00:00:00Z", "rows": [
    {"order_id": "O1", "store_code": "nanshan", "employee_id": "E1", "customer_id": "C1", "amount": 120, "date": "2026-08-02"},
    {"order_id": "O2", "store_code": "online", "amount": 80, "date": "2026-08-03"},
]}


def test_sales_contract_has_summary_stores_and_trend():
    result = sales_analysis(SALES)
    assert result["summary"] == {"sales_amount": 200.0, "order_count": 2, "average_order_value": 100.0}
    assert len(result["stores"]) == 5 and result["trend_series"][-1]["value"] == 80.0


def test_member_coverage_keeps_unattributed_sales_pending():
    result = member_analysis({"members": [{"member_id": "E1", "name": "员工一"}]}, SALES)
    assert result["members"][0]["sales_amount"] == 120.0
    assert result["summary"]["coverage_rate"] == .5 and result["summary"]["pending_rows"] == 1


def test_customer_value_and_opportunity_are_derived_from_sales():
    result = customer_analysis({"customers": [{"customer_id": "C1", "name": "客户一"}]}, SALES)
    assert result["customers"][0] == {"customer_id": "C1", "customer_name": "客户一", "consumption_amount": 120.0, "purchase_count": 1, "value_segment": "high_value", "opportunity": "priority_retention"}


def test_supplier_domain_whitelists_only_supply_chain_fields():
    result = supplier_analysis({"suppliers": [{"supplier_id": "S1", "supplier_name": "供应商一", "purchase_amount": 99, "customer_id": "must-not-cross-domain"}]})
    assert result["domain"] == "supply_chain" and "customer_id" not in result["suppliers"][0]
