import io
import json

from services.business.app import BusinessStore, create_app


def call(app, method, path, roles="employee,customers:read,store_manager", department="nanshan", body=None):
    raw = json.dumps(body or {}).encode(); result = []
    response = b"".join(app({"REQUEST_METHOD": method, "PATH_INFO": path.split("?", 1)[0], "QUERY_STRING": path.split("?", 1)[1] if "?" in path else "", "wsgi.input": io.BytesIO(raw), "CONTENT_LENGTH": str(len(raw)), "CONTENT_TYPE": "application/json", "HTTP_X_VAFOX_USER_ID": "manager-1", "HTTP_X_VAFOX_ORGANIZATION_ID": "org-1", "HTTP_X_VAFOX_DEPARTMENT_ID": department, "HTTP_X_VAFOX_ROLE_SCOPE": roles}, lambda status, _: result.append(status)))
    return int(result[0].split()[0]), json.loads(response)


def test_customer_profile_purchase_equipment_and_data_scope():
    store = BusinessStore(); app = create_app(store)
    status, profile = call(app, "GET", "/api/customer/profile/C1")
    assert status == 200 and profile["profile"]["customer_id"] == "C1" and profile["purchase_history"][0]["brand"] == "KAILAS"
    status, equipment = call(app, "GET", "/api/customer/equipment/C1")
    assert status == 200 and {item["type"] for item in equipment["opportunities"]} == {"equipment_upgrade", "activity", "repurchase"}
    assert call(app, "GET", "/api/customer/profile/C1", department="hangyuan")[0] == 403
    assert {event["action"] for event in store.audit_events} >= {"customer_profile_read", "customer_equipment_read"}


def test_retail_dashboard_alert_feedback_wechat_and_permissions():
    store = BusinessStore(); app = create_app(store)
    status, insight = call(app, "GET", "/api/retail/store-insight?store=nanshan")
    # Query string is intentionally passed through gateway in production; default scope remains nanshan in direct WSGI test.
    assert status == 200 and insight["sales_insight"]["brand_contribution"] and insight["read_only"]
    status, alerts = call(app, "GET", "/api/retail/inventory-alerts")
    assert status == 200 and alerts["inventory_mutation_allowed"] is False
    status, dashboard = call(app, "GET", "/api/store/dashboard")
    assert status == 200 and {"sales_summary", "product_opportunities", "inventory_alerts", "customer_opportunities", "ai_recommendations"} <= dashboard.keys()
    assert call(app, "POST", "/api/store/feedback", body={"feedback": "请增加雨天陈列提示"})[0] == 202
    assert call(app, "GET", "/api/wechat/store-report")[1]["report_type"] == "store_manager_daily"
    assert call(app, "GET", "/api/store/dashboard", roles="employee,customers:read")[0] == 403
    assert {event["action"] for event in store.audit_events} >= {"retail_store_insight_read", "retail_inventory_alerts_read", "store_dashboard_read", "store_feedback_submitted", "wechat_store_report_generated"}
