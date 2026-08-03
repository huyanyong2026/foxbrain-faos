import io
import json

from services.business.app import BusinessStore, create_app


def call(app, method, path, roles="employee", body=None, department="north"):
    raw = json.dumps(body or {}).encode()
    result = []
    output = b"".join(app({"REQUEST_METHOD": method, "PATH_INFO": path, "QUERY_STRING": "", "wsgi.input": io.BytesIO(raw), "CONTENT_LENGTH": str(len(raw)), "CONTENT_TYPE": "application/json", "HTTP_X_VAFOX_USER_ID": "u-1", "HTTP_X_VAFOX_ORGANIZATION_ID": "org-1", "HTTP_X_VAFOX_DEPARTMENT_ID": department, "HTTP_X_VAFOX_ROLE_SCOPE": roles}, lambda status, _: result.append(status)))
    return int(result[0].split()[0]), json.loads(output)


def test_employee_workspace_product_sales_and_scenario_advice():
    app = create_app()
    status, product = call(app, "POST", "/api/workspace/advice", body={"type": "product", "query": "MONT适合什么客户？"})
    assert status == 200 and product["citation"] and product["advisory_only"]
    status, sales = call(app, "POST", "/api/workspace/advice", body={"type": "sales", "query": "客户觉得冲锋衣贵怎么办？"})
    assert status == 200 and "sales_talk" in sales
    status, scenario = call(app, "POST", "/api/workspace/advice", body={"type": "scenario", "query": "川西7天", "destination": "川西7天", "budget": 5000, "experience": "进阶"})
    assert status == 200 and scenario["equipment"] and scenario["citation"]


def test_customer_permission_and_data_scope():
    app = create_app()
    assert call(app, "POST", "/api/workspace/advice", body={"type": "customer", "query": "C1"})[0] == 403
    status, response = call(app, "POST", "/api/workspace/advice", roles="employee,customers:read", body={"type": "customer", "query": "C1"}, department="nanshan")
    assert status == 200 and response["data_scope"]["department_id"] == "nanshan"


def test_ceo_wechat_kailas_and_audit():
    store = BusinessStore(); app = create_app(store)
    assert call(app, "GET", "/api/ceo/dashboard")[0] == 403
    assert call(app, "GET", "/api/ceo/dashboard", roles="ceo")[0] == 200
    status, kailas = call(app, "GET", "/api/kailas/product")
    assert status == 200 and kailas["brand_profile"]["brand"] == "KAILAS" and kailas["product_card"]["product"] == "MONT"
    status, wechat = call(app, "POST", "/api/wechat/message", roles="store_manager", body={"message": "南山店今天关注什么？"})
    assert status == 200 and wechat["audit_logged"] and "门店建议" in wechat["reply"]
    assert {event["action"] for event in store.audit_events} >= {"ceo_dashboard_read", "kailas_product_read", "wechat_message"}


def test_ceo_correction_routes_include_active_online_sales_and_daily_report():
    app = create_app()
    for path in ("/api/ceo/overview", "/api/ceo/business"):
        status, payload = call(app, "GET", path, roles="ceo")
        assert status == 200 and payload["trust_status"] == "CEO_Dashboard_Data_Trusted_Complete"
        assert any(item["id"] == "online" for item in payload["operating_stores"])
    status, stores = call(app, "GET", "/api/ceo/stores", roles="ceo")
    online = next(item for item in stores["items"] if item["id"] == "online")
    assert status == 200 and stores["includes_online_store"] and online["operating_status"] == "ACTIVE" and online["sales_amount"] > 0
    status, report = call(app, "GET", "/api/ceo/daily-report", roles="ceo")
    assert status == 200 and report["business"]["sales_summary"]["amount"] >= online["sales_amount"]
    business = report["business"]
    assert business["version"] == "V6.1.11.3"
    assert business["cost_governance"][0]["brand"] == "KAILAS"
    assert business["employee_attribution"] == {"sales_rows": 5, "attributed_rows": 4, "pending_rows": 1}
    assert business["customer360"]["fusion_status"] == "pending_authorized_wecom_binding"
    assert business["suppliers"]["write_enabled"] is False


def test_ceo_today_uses_only_production_contract_and_has_no_snapshot_fallback():
    assert call(create_app(), "GET", "/api/ceo/today", roles="ceo") == (503, {"error": "ceo_data_unavailable"})

    class CoreClient:
        def get_ceo_today(self):
            return {
                "sales": 10, "orders": 2, "effective_skus": 8,
                "customer_opportunities": [{"title": "客户 A", "reason": "待回访", "supplier": "不得透传"}],
                "operating_stores": [
                    {"store_code": "nanshan", "store_name": "南山", "status": "营业"},
                    {"store_code": "wuhouci", "store_name": "武侯祠", "status": "历史"},
                ],
                "top_brands": [{"brand_name": "KAILAS", "brand_code": "K", "sales": 10}],
                "risks": [], "ai_summary": "摘要", "ai_recommendations": [],
                "data_source": "Data Core", "updated_at": "2026-08-03T00:00:00Z", "confidence": 0.99,
                "freshness_status": "fresh",
                "sales_change_analysis": [{"dimension": "store", "name": "南山", "change": 8,
                                           "reasons": ["订单增长"], "internal_note": "不得透传"}],
                "customer_actions": [{"customer_name": "客户 A", "action": "回访", "reason": "近期购买",
                                      "phone": "不得透传"}],
            }

    status, payload = call(create_app(BusinessStore(core_client=CoreClient())), "GET", "/api/ceo/today", roles="ceo")
    assert status == 200
    assert payload["sales"] / payload["orders"] == 5
    assert payload["operating_stores"] == [{"store_code": "nanshan", "store_name": "南山", "status": "营业"}]
    assert payload["top_brands"] == [{"brand_name": "KAILAS", "sales": 10}]
    assert payload["customer_opportunities"] == [{"title": "客户 A", "reason": "待回访"}]
    assert payload["freshness_status"] == "fresh"
    assert payload["sales_change_analysis"] == [{"dimension": "store", "name": "南山", "change": 8,
                                                  "reasons": ["订单增长"]}]
    assert payload["customer_actions"] == [{"customer_name": "客户 A", "action": "回访", "reason": "近期购买"}]
