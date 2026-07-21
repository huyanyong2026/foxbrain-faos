import io
import json

from services.knowledge.app import create_app
from services.knowledge.product_intelligence import ProductIntelligenceStore


def headers(role="product_manager"):
    return {"HTTP_X_VAFOX_USER_ID": "pm-1", "HTTP_X_VAFOX_ORGANIZATION_ID": "org-kailas",
            "HTTP_X_VAFOX_DEPARTMENT_ID": "product", "HTTP_X_VAFOX_ROLE_SCOPE": role}


def call(app, method, path, headers_=None, body=b"", content_type="application/json"):
    result = []
    response = b"".join(app({"REQUEST_METHOD": method, "PATH_INFO": path, "QUERY_STRING": "", "wsgi.input": io.BytesIO(body),
                              "CONTENT_LENGTH": str(len(body)), "CONTENT_TYPE": content_type, **(headers_ or {})}, lambda status, _: result.append(status)))
    return int(result[0].split()[0]), json.loads(response)


def multipart(filename, content):
    boundary = "pip-test"
    body = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{filename}\"\r\nContent-Type: text/markdown\r\n\r\n".encode() + content +
            f"\r\n--{boundary}\r\nContent-Disposition: form-data; name=\"brand_id\"\r\n\r\nkailas\r\n--{boundary}--\r\n".encode())
    return body, f"multipart/form-data; boundary={boundary}"


def test_upload_processing_review_publish_search_and_readonly_recommendation():
    store = ProductIntelligenceStore()
    app = create_app(memory_service=object(), retrieval_service=object(), product_store=store)
    body, content_type = multipart("mont.md", b"brand: kailas\nmodel: MONT\nseries: MONT\ncategory: shell\nscenario: hiking")
    status, uploaded = call(app, "POST", "/api/product-assets/upload", headers(), body, content_type)
    assert status == 202 and uploaded["review_status"] == "Review" and uploaded["content_sha256"]
    asset_id = uploaded["asset_id"]
    status, asset = call(app, "GET", f"/api/product-assets/{asset_id}", headers())
    assert status == 200 and {entity["entity_type"] for entity in asset["entities"]} == {"Brand Entity", "Product Entity", "Scenario Entity"}
    status, review = call(app, "POST", f"/api/product-assets/{asset_id}/review", headers(), b'{"decision":"approved"}')
    assert status == 200 and review["review_status"] == "Published"
    product_id = next(iter(store.cards))
    status, card = call(app, "GET", f"/api/product-intelligence/{product_id}", headers())
    assert status == 200 and card["model"] == "MONT" and card["citation"][0]["locator"] and card["advisory_only_requires_human_approval"]
    status, search = call(app, "GET", "/api/product-intelligence/search", headers())
    assert status == 400
    status, recommendation = call(app, "POST", "/api/product-intelligence/recommend", headers(), b'{"scenario":"hiking","need":"MONT"}')
    assert status == 200 and recommendation["advisory_only_requires_human_approval"] and recommendation["inventory"]["status"] == "not_connected_read_only_mvp"
    assert [event["action"] for event in store.audit_events] == ["asset_uploaded", "asset_processed", "asset_published_after_human_review"]


def test_upload_role_acl_and_unpublished_content_are_not_exposed():
    store = ProductIntelligenceStore(); app = create_app(memory_service=object(), retrieval_service=object(), product_store=store)
    body, content_type = multipart("mont.md", b"brand: kailas\nmodel: MONT")
    assert call(app, "POST", "/api/product-assets/upload", headers("operation"), body, content_type)[0] == 202
    assert call(app, "POST", "/api/product-assets/upload", headers("sales"), body, content_type)[0] == 403
    assert call(app, "GET", "/api/product-intelligence/search", headers(), b"", "")[0] == 400


def test_explicit_sales_fields_create_versioned_cited_sales_knowledge():
    store = ProductIntelligenceStore(); app = create_app(memory_service=object(), retrieval_service=object(), product_store=store)
    source = (b"brand: kailas\nmodel: MONT\nscenario: hiking\ncustomer_type: beginner\n"
              b"customer_need: stay dry\ndiscovery_questions: Where will you hike?\n"
              b"recommendation_logic: Recommend a shell for rain\nproduct_bundle: MONT + rain pants\n"
              b"sales_script: This shell keeps you dry.\nobjection_handling: Explain the waterproof rating\n"
              b"cross_sell: Add rain pants")
    body, content_type = multipart("sales.md", source)
    status, uploaded = call(app, "POST", "/api/product-assets/upload", headers(), body, content_type)
    assert status == 202
    _, asset = call(app, "GET", f"/api/product-assets/{uploaded['asset_id']}", headers())
    sales = next(entity for entity in asset["entities"] if entity["entity_type"] == "SalesKnowledgeEntity")
    assert set(sales) == {"entity_type", "knowledge_id", "scenario", "customer_type", "customer_need", "discovery_questions", "recommendation_logic", "product_bundle", "sales_script", "objection_handling", "cross_sell", "citation", "version", "confidence"}
    assert sales["customer_type"] == "beginner" and sales["citation"]["asset_id"] == uploaded["asset_id"]
    assert sales["version"] == "1" and sales["confidence"]["score"] == 0.4
    assert call(app, "POST", f"/api/product-assets/{uploaded['asset_id']}/review", headers(), b'{"decision":"approved"}')[0] == 200
    card = store.cards[next(iter(store.cards))]
    assert card["sales_knowledge"] == [sales]
