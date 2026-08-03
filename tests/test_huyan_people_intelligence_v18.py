import io
import json

from services.business.aggregation import organization_analysis
from services.business.app import BusinessStore, create_app


def test_people_intelligence_never_allocates_unattributed_sales():
    members = {"data_source": "Data Core", "members": [{"employee_id": "E1", "name": "甲", "store_code": "nanshan"}, {"employee_id": "E2", "name": "乙"}]}
    sales = {"sales": [{"order_id": "O1", "employee_id": "E1", "amount": 100, "sku": "S1", "customer_id": "C1", "date": "2026-08-01"}, {"order_id": "O2", "amount": 90}]}
    result = organization_analysis(members, sales)
    assert result["overview"] == {"employee_count": 2, "selling_employee_count": 1, "sales_coverage_rate": .5, "order_count": 2, "attributed_sales": 100, "pending_order_count": 1, "pending_sales": 90}
    assert result["employees"][1]["store_name"] == "销售归属待补齐。"
    assert sum(row["sales_amount"] for row in result["employees"]) == 100
    assert result["attribution_policy"] == {"missing_label": "销售归属待补齐。", "average_allocation": False, "estimated_contribution": False}


def test_people_api_requires_live_core_and_ceo_scope():
    raw = b""; statuses = []
    environ = {"REQUEST_METHOD": "GET", "PATH_INFO": "/api/business/organization-analysis", "QUERY_STRING": "", "wsgi.input": io.BytesIO(raw), "CONTENT_LENGTH": "0", "HTTP_X_VAFOX_USER_ID": "u", "HTTP_X_VAFOX_ORGANIZATION_ID": "o", "HTTP_X_VAFOX_ROLE_SCOPE": "ceo", "HTTP_X_VAFOX_DATA_SCOPE": "ALL_DATA"}
    body = b"".join(create_app(BusinessStore())(environ, lambda status, _: statuses.append(status)))
    assert statuses[0].startswith("503") and json.loads(body) == {"error": "organization_analysis_data_unavailable"}
