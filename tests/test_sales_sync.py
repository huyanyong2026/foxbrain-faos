from apps.core_api.sales_adapter import SalesDomainAdapter


def test_sap_sales_sync_adapter_reads_orders_and_lines_as_read_only_facts():
    calls = []

    def query(sql, params):
        calls.append((sql, params))
        return [{"order_id": "SO-1", "store": "NS", "sku": "A1", "quantity": 2,
                 "amount": 1998, "margin": 800, "date": "2026-07-22"}]

    payload = SalesDomainAdapter(query, lambda: "2026-07-22T00:00:00+00:00").read(limit=10)

    assert "sap_sales_orders" in calls[0][0] and "sap_sales_order_lines" in calls[0][0]
    assert calls[0][1] == (10,)
    assert payload["data"] == [{"order_id": "SO-1", "store": "NS", "sku": "A1", "quantity": 2,
                                "amount": 1998, "margin": 800, "date": "2026-07-22"}]
    assert {"source", "timestamp", "version", "confidence"} <= set(payload)


def test_sales_sync_adapter_enforces_store_scope_after_reading_mirror_projection():
    adapter = SalesDomainAdapter(lambda _sql, _params: [
        {"order_id": "1", "store": "NS", "sku": "A", "quantity": 1, "amount": 1, "margin": 1, "date": "2026-07-22"},
        {"order_id": "2", "store": "ZX", "sku": "B", "quantity": 1, "amount": 1, "margin": 1, "date": "2026-07-22"},
    ], lambda: "now")
    assert [row["order_id"] for row in adapter.read(store_ids={"NS"})["data"]] == ["1"]
