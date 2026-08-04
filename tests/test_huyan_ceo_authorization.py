from services.gateway.huyan_authorization import business_authorization


HUYAN_CEO = {"portal": "huyan.vafox.com", "role": "VAFOX_CEO", "data_scope": "ALL_DATA"}


def test_huyan_ceo_maps_only_on_aligned_business_endpoints():
    for name in ("sales", "member", "customer"):
        roles, scope = business_authorization(HUYAN_CEO, f"/api/business/{name}-analysis")
        assert "ceo" in roles
        assert scope == "ALL_DATA"


def test_mapping_rejects_wrong_portal_role_or_scope():
    path = "/api/business/sales-analysis"
    for claims in ({**HUYAN_CEO, "portal": "ai.vafox.com"}, {**HUYAN_CEO, "roles": ["employee"]}, {**HUYAN_CEO, "data_scope": "STORE_DATA"}):
        assert "ceo" not in business_authorization(claims, path)[0]


def test_supplier_endpoint_stays_outside_huyan_mapping():
    roles, scope = business_authorization(HUYAN_CEO, "/api/business/supplier-analysis")
    assert roles == ["VAFOX_CEO"]
    assert scope == "ALL_DATA"


def test_supply_chain_intelligence_is_mapped_for_huyan_ceo_all_data():
    roles, scope = business_authorization(HUYAN_CEO, "/api/business/supply-chain-intelligence")
    assert "ceo" in roles and scope == "ALL_DATA"


def test_ai_advisor_inherits_huyan_ceo_all_data_authorization():
    roles, scope = business_authorization(HUYAN_CEO, "/api/ceo/ai-advisor")
    assert "VAFOX_CEO" in roles and "ceo" in roles and scope == "ALL_DATA"
