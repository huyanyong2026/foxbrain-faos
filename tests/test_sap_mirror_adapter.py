from apps.core_api.sap_mirror_adapter import SAPMirrorAdapter
from services.runtime.app import CoreEvidenceAdapter, RuntimeRouter


def test_sap_mirror_adapter_projects_all_required_domains_with_evidence():
    objects = {
        "products": [{"id": "P1", "name": "Jacket"}],
        "customers": [{"id": "C1", "name": "Customer"}],
        "suppliers": [{"id": "S1", "name": "Supplier"}],
        "stores": [{"id": "NS", "name": "Nanshan"}],
    }
    adapter = SAPMirrorAdapter(
        lambda _sql, _params: [{"sku": "P1", "store_id": "NS", "quantity": 4, "risk": "normal"}],
        lambda name, *_args: {"items": objects[name]},
        lambda: "2026-07-22T00:00:00+00:00",
        lambda _stores, _limit: {"data": [{"order_id": "SO1", "store": "NS", "sku": "P1"}]},
    )
    for domain, identifier in (("product", "product_id"), ("sales", "order_id"), ("inventory", "quantity"), ("customer", "customer_id"), ("supplier", "supplier_id")):
        payload = adapter.read(domain)
        assert payload["mode"] == "read_only"
        assert payload["source"] == "sap_mirror"
        assert {"timestamp", "confidence"} <= set(payload)
        assert identifier in payload["data"][0]


def test_sap_mirror_evidence_flows_from_core_api_contract_to_runtime():
    adapter = SAPMirrorAdapter(
        lambda _sql, _params: [], lambda *_args: {"items": []},
        lambda: "2026-07-22T00:00:00+00:00",
        lambda _stores, _limit: {"data": [{"order_id": "SO1", "store": "NS", "sku": "P1"}]},
    )
    response = RuntimeRouter(CoreEvidenceAdapter(lambda domain, _scope: adapter.read(domain))).query({
        "user_id": "u", "wecom_user_id": "wx", "role": "ceo",
        "scope": {"permissions": ["enterprise:read"]}, "query": "今天销售情况？",
    })
    evidence = response["citation"]["evidence"]
    assert len(evidence) == 1
    assert evidence[0]["source"] == "sap_mirror"
    assert {"timestamp", "confidence"} <= set(evidence[0])
