import io
import json

from services.runtime.app import CoreEvidenceAdapter, EvidenceRepository, RuntimeRouter, create_app


class Evidence(EvidenceRepository):
    def collect(self, identity, route, sources, query):
        return [{"source": "Core Data", "citation": "core:daily:1", "summary": "已验证今日销售快照"}]


def request(app, payload):
    result = []
    output = b"".join(app({"REQUEST_METHOD": "POST", "PATH_INFO": "/api/runtime/wecom/query", "wsgi.input": io.BytesIO(json.dumps(payload).encode()), "CONTENT_LENGTH": str(len(json.dumps(payload).encode()))}, lambda status, headers: result.append(status)))
    return int(result[0].split()[0]), json.loads(output)


def test_ceo_runtime_routes_evidence_and_required_business_sections():
    status, response = request(create_app(RuntimeRouter(Evidence())), {"user_id": "u", "wecom_user_id": "wx", "role": "ceo", "scope": {"permissions": ["enterprise:read"]}, "query": "今日经营情况？"})
    assert status == 200 and response["citation"]["route"] == "huyan-ceo-intelligence"
    assert response["sources"] == ["Core Data", "Retail Brain", "Customer Brain"]
    assert all(section in response["answer"] for section in ("经营摘要", "数据依据", "风险", "AI建议", "Citation"))


def test_role_routes_and_missing_evidence_never_create_facts():
    payload = {"user_id": "u", "wecom_user_id": "wx", "role": "buyer", "scope": {"permissions": ["procurement:read"]}, "query": "需要采购什么？"}
    status, response = request(create_app(), payload)
    assert status == 200 and response["citation"]["route"] == "procurement-intelligence"
    assert "没有可验证的经营数据" in response["answer"] and response["confidence"] == "low"


def test_core_evidence_adapter_uses_role_domains_and_preserves_evidence_metadata():
    calls = []
    def reader(domain, scope):
        calls.append((domain, scope))
        return {"data": [{"id": "verified"}], "source": "core." + domain,
                "timestamp": "2026-07-14T00:00:00+00:00", "version": "v1", "confidence": .95}
    router = RuntimeRouter(CoreEvidenceAdapter(reader))
    cases = [
        ("ceo", ["enterprise:read"], ("sales", "inventory", "customers"), "今天公司最重要三件事？"),
        ("buyer", ["procurement:read"], ("products", "inventory"), "KAILAS MONT目前经营情况？"),
        ("store_manager", ["store:read"], ("stores", "sales", "customers"), "南山店今天重点是什么？"),
    ]
    for role, permissions, domains, query in cases:
        calls.clear()
        response = router.query({"user_id": "u", "wecom_user_id": "wx", "role": role,
                                 "scope": {"permissions": permissions, "data_scope": "NS"}, "query": query})
        assert tuple(domain for domain, _ in calls) == domains
        assert all({"source", "timestamp", "version", "confidence"} <= set(item) for item in response["citation"]["evidence"])
        assert all(section in response["answer"] for section in ("经营摘要", "数据依据", "风险", "AI建议", "Citation"))
