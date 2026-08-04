import io
import json

from services.business.app import BusinessStore, create_app
from services.business.supply_chain import supply_chain_intelligence


QUERY = {"date_from": "2026-08-01", "date_to": "2026-08-31", "supplier_id": None,
         "brand_id": None, "location_id": None, "page": 1, "page_size": 50}


def test_supply_chain_aggregates_only_governed_purchase_links():
    suppliers = {"status": "complete", "updated_at": "2026-08-04T00:00:00Z", "suppliers": [
        {"supplier_id": "S1", "supplier_name": "供应商一", "supplier_status": "active", "updated_at": "2026-08-04T00:00:00Z"}]}
    purchases = {"status": "complete", "updated_at": "2026-08-04T00:00:00Z", "purchases": [
        {"purchase_document_id": "PO1", "purchase_line_id": "L1", "supplier_id": "S1", "sku_id": "SKU1", "brand_id": "B1",
         "brand_name": "品牌一", "order_date": "2026-08-01", "ordered_quantity": 10, "ordered_amount": 100,
         "expected_delivery_date": "2026-08-03", "received_date": "2026-08-04", "received_quantity": 8,
         "document_status": "open", "updated_at": "2026-08-04T00:00:00Z"}]}
    inventory = {"status": "complete", "updated_at": "2026-08-04T00:00:00Z", "inventory": [
        {"sku_id": "SKU1", "brand_id": "B1", "on_hand_quantity": 5, "updated_at": "2026-08-04T00:00:00Z"}]}
    result = supply_chain_intelligence(suppliers, purchases, inventory, QUERY, "r1")
    assert result["overview"]["purchase_amount"] == 100
    assert result["overview"]["receipt_rate"] == .8
    assert result["supplier_performance"][0]["supplier_id"] == "S1"
    assert result["brand_supply_relationships"][0]["inventory_quantity"] == 5
    assert result["risks"][0]["risk_type"] == "late_delivery"
    assert result["ai_advice"] == {"status": "unavailable", "items": []}
    assert "customer_id" not in json.dumps(result)


def test_incomplete_purchase_contract_returns_syncing_without_business_output():
    result = supply_chain_intelligence({"status": "complete", "suppliers": []}, {"status": "syncing"}, {}, QUERY)
    assert result["data_status"]["message"] == "供应链数据同步中"
    assert result["overview"] is None and result["supplier_performance"] == [] and result["risks"] == []


def test_api_requires_dates_scope_and_live_core():
    base = {"REQUEST_METHOD": "GET", "PATH_INFO": "/api/business/supply-chain-intelligence", "wsgi.input": io.BytesIO(b""), "CONTENT_LENGTH": "0",
            "HTTP_X_VAFOX_USER_ID": "u", "HTTP_X_VAFOX_ORGANIZATION_ID": "o", "HTTP_X_VAFOX_ROLE_SCOPE": "ceo"}
    def call(environ):
        statuses = []; body = b"".join(create_app(BusinessStore())(environ, lambda status, _: statuses.append(status)))
        return statuses[0], json.loads(body)
    status, body = call({**base, "QUERY_STRING": "date_from=2026-08-01&date_to=2026-08-31", "HTTP_X_VAFOX_DATA_SCOPE": "STORE_DATA"})
    assert status.startswith("403") and body["error"] == "all_data_scope_required"
    status, body = call({**base, "QUERY_STRING": "", "HTTP_X_VAFOX_DATA_SCOPE": "ALL_DATA"})
    assert status.startswith("400") and body["error"] == "invalid_request"
    status, body = call({**base, "QUERY_STRING": "date_from=2026-08-01&date_to=2026-08-31", "HTTP_X_VAFOX_DATA_SCOPE": "ALL_DATA"})
    assert status.startswith("503") and body["message"] == "供应链数据同步中"
