"""M4.2 Brand Knowledge: schema, import, ACL, retrieval, and 24 sales questions."""
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


@pytest.mark.parametrize("category, path, expected_brand", [
    # 品牌定位
    ("positioning", "/api/brands/search?query=专业山地", "kailas"),
    ("positioning", "/api/brands/search?query=瑞士", "mammut"),
    ("positioning", "/api/brands/search?query=背负系统", "osprey"),
    # 用户画像
    ("user", "/api/brands/search?query=徒步爱好者", "kailas"),
    ("user", "/api/brands/search?query=重视安全性能", "mammut"),
    ("user", "/api/brands/search?query=背负舒适度", "osprey"),
    # 产品线
    ("product", "/api/brands/search?query=跑山", "kailas"),
    ("product", "/api/brands/search?query=硬壳服装", "mammut"),
    ("product", "/api/brands/search?query=水袋", "osprey"),
    ("product", "/api/brands/search?query=雪地装备", "mammut"),
    # 使用场景
    ("scenario", "/api/brands/search?query=高海拔登山", "kailas"),
    ("scenario", "/api/brands/search?query=冰雪", "mammut"),
    ("scenario", "/api/brands/search?query=多日露营", "osprey"),
    ("scenario", "/api/brands/search?query=旅行", "osprey"),
    # 竞品比较（按品牌过滤，避免只验证共享竞品词）
    ("competition", "/api/brands/search?query=MAMMUT&brand_id=kailas", "kailas"),
    ("competition", "/api/brands/search?query=KAILAS&brand_id=mammut", "mammut"),
    ("competition", "/api/brands/search?query=DEUTER&brand_id=osprey", "osprey"),
    # 销售建议
    ("sales", "/api/brands/search?query=分层穿衣", "kailas"),
    ("sales", "/api/brands/search?query=暴露环境", "mammut"),
    ("sales", "/api/brands/search?query=躯干长度", "osprey"),
    ("sales", "/api/brands/search?query=试背调节", "osprey"),
    # 场景推荐
    ("recommendation", "/api/brands/recommend?scenario=高海拔登山", "kailas"),
    ("recommendation", "/api/brands/recommend?scenario=技术登山", "mammut"),
    ("recommendation", "/api/brands/recommend?scenario=多日徒步", "osprey"),
])
def test_twenty_four_brand_questions_cover_required_sales_dimensions(category, path, expected_brand):
    app = create_app(memory_service=object(), retrieval_service=object(), brand_store=BrandKnowledgeStore())
    status, payload = request(app, path, headers())
    assert status == 200, category
    matched = [item for item in payload["items"] if item["brand"]["brand_id"] == expected_brand]
    assert matched, category
    assert all(item["citation"].get("source") and item["citation"].get("location") for item in matched)


def test_brand_compare_requires_auth_and_returns_comparison_fields():
    app = create_app(memory_service=object(), retrieval_service=object(), brand_store=BrandKnowledgeStore())
    assert request(app, "/api/brands/compare?brands=kailas,mammut", {})[0] == 401
    status, payload = request(app, "/api/brands/compare?brands=kailas,mammut", headers())
    assert status == 200 and len(payload["brands"]) == 2 and "sales_tips" in payload["comparison_fields"]


@pytest.mark.parametrize("brand_ids", ["kailas,mammut", "kailas,osprey", "mammut,osprey"])
def test_brand_comparison_returns_traceable_records_for_each_pair(brand_ids):
    app = create_app(memory_service=object(), retrieval_service=object(), brand_store=BrandKnowledgeStore())
    status, payload = request(app, f"/api/brands/compare?brands={brand_ids}", headers())
    assert status == 200
    assert {brand["brand_id"] for brand in payload["brands"]} == set(brand_ids.split(","))
    assert all(brand["source_traceability"][0]["location"] == f"brand:{brand['brand_id']}" for brand in payload["brands"])
