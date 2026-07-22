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
