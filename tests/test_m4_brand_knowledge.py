"""M4.2 Brand Knowledge: schema, import, ACL, retrieval, and 20 sales questions."""
import io
import json
import zipfile

import pytest

from services.knowledge.app import create_app
from services.knowledge.brand import BRAND_FIELDS, BrandKnowledgeStore
from services.memory.acl import AuthContext


def request(app, path, headers):
    status = []
    environ = {"REQUEST_METHOD": "GET", "PATH_INFO": path.split("?", 1)[0], "QUERY_STRING": path.partition("?")[2],
               "wsgi.input": io.BytesIO(), "CONTENT_LENGTH": "0", **headers}
    response = b"".join(app(environ, lambda value, _: status.append(value))).decode()
    return int(status[0].split()[0]), json.loads(response)


def headers(user="alice", org="org-a", department="sales"):
    return {"HTTP_X_VAFOX_USER_ID": user, "HTTP_X_VAFOX_ORGANIZATION_ID": org, "HTTP_X_VAFOX_DEPARTMENT_ID": department}


def test_brand_schema_exposes_all_required_fields_and_three_phase_one_brands():
    store = BrandKnowledgeStore()
    assert set(store.brands) == {"kailas", "mammut", "osprey"}
    assert set(store.brands["kailas"].payload()) == set(BRAND_FIELDS)
    assert store.brands["kailas"].source_traceability[0]["location"] == "brand:kailas"


def test_markdown_docx_import_generates_metadata_citation_and_acl(tmp_path):
    store = BrandKnowledgeStore(); context = AuthContext("org-a", "sales", "alice", frozenset())
    markdown = tmp_path / "kailas.md"; markdown.write_text("# KAILAS\n高海拔徒步装备说明", encoding="utf-8")
    result = store.import_document(markdown, "kailas", context, "department")
    assert result["metadata"]["content_sha256"] and result["citations"][0]["location"] == "line:1"
    assert result["acl"]["visibility"] == "department"
    docx = tmp_path / "mammut.docx"
    with zipfile.ZipFile(docx, "w") as archive:
        archive.writestr("word/document.xml", '<w:document xmlns:w="urn:w"><w:body><w:p><w:r><w:t>冰雪安全装备</w:t></w:r></w:p></w:body></w:document>')
    assert store.import_document(docx, "mammut", context)["citations"][0]["location"] == "paragraph:1"


def test_imported_brand_document_enforces_organization_and_department_acl(tmp_path):
    store = BrandKnowledgeStore(); source = tmp_path / "osprey.md"; source.write_text("背负系统试背调节", encoding="utf-8")
    store.import_document(source, "osprey", AuthContext("org-a", "sales", "alice", frozenset()), "department")
    assert all(item["citation"]["source"] != "osprey.md" for item in store.search("背负系统", AuthContext("org-a", "ops", "bob", frozenset())))
    assert all(item["citation"]["source"] != "osprey.md" for item in store.search("背负系统", AuthContext("org-b", "sales", "bob", frozenset())))
    assert any(item["citation"]["source"] == "osprey.md" for item in store.search("背负系统", AuthContext("org-a", "sales", "bob", frozenset())))


@pytest.mark.parametrize("path, expected_brand", [
    ("/api/brands/search?query=专业山地", "kailas"), ("/api/brands/search?query=瑞士", "mammut"),
    ("/api/brands/search?query=背负系统", "osprey"), ("/api/brands/search?query=攀岩", "kailas"),
    ("/api/brands/search?query=冰雪", "mammut"), ("/api/brands/search?query=旅行", "osprey"),
    ("/api/brands/search?query=越野跑", "kailas"), ("/api/brands/search?query=硬壳服装", "mammut"),
    ("/api/brands/search?query=水袋", "osprey"), ("/api/brands/search?query=分层穿衣", "kailas"),
    ("/api/brands/search?query=安全装备", "mammut"), ("/api/brands/search?query=躯干长度", "osprey"),
    ("/api/brands/recommend?scenario=高海拔登山", "kailas"), ("/api/brands/recommend?scenario=技术登山", "mammut"),
    ("/api/brands/recommend?scenario=多日徒步", "osprey"), ("/api/brands/search?query=跑山", "kailas"),
    ("/api/brands/search?query=雪地装备", "mammut"), ("/api/brands/search?query=容量", "osprey"),
    ("/api/brands/search?query=登山", "kailas"), ("/api/brands/search?query=收纳组织", "osprey"),
])
def test_twenty_brand_questions_cover_positioning_product_scenario_and_sales(path, expected_brand):
    app = create_app(memory_service=object(), retrieval_service=object(), brand_store=BrandKnowledgeStore())
    status, payload = request(app, path, headers())
    assert status == 200 and any(item["brand"]["brand_id"] == expected_brand for item in payload["items"])


def test_brand_compare_requires_auth_and_returns_comparison_fields():
    app = create_app(memory_service=object(), retrieval_service=object(), brand_store=BrandKnowledgeStore())
    assert request(app, "/api/brands/compare?brands=kailas,mammut", {})[0] == 401
    status, payload = request(app, "/api/brands/compare?brands=kailas,mammut", headers())
    assert status == 200 and len(payload["brands"]) == 2 and "sales_tips" in payload["comparison_fields"]
