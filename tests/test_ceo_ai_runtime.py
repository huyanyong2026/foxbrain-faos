import io
import json

from services.ai.app import create_app


def call(payload):
    result = []
    body = json.dumps(payload).encode()
    output = b"".join(create_app()({"REQUEST_METHOD": "POST", "PATH_INFO": "/api/v1/ai/respond", "wsgi.input": io.BytesIO(body), "CONTENT_LENGTH": str(len(body))}, lambda status, headers: result.append(status)))
    return int(result[0].split()[0]), json.loads(output)


def test_ceo_runtime_uses_huyan_intelligence_for_supported_operating_questions():
    status, payload = call({"question": "KAILAS经营情况？", "agent": "huyan-ai", "role": "ceo", "permission_scope": ["enterprise:read"]})
    assert status == 200
    assert payload["agent"] == "huyan-ceo-intelligence"
    assert "KAILAS经营" in payload["content"]
    assert {citation["source"] for citation in payload["citations"]} == {"Core Data API", "Retail Brain", "Customer Brain"}


def test_ceo_runtime_only_reports_permission_error_when_enterprise_access_is_missing():
    status, payload = call({"question": "当前最大风险？", "agent": "huyan-ai", "role": "ceo", "permission_scope": []})
    assert (status, payload) == (403, {"error": "enterprise_permission_required"})


def test_ceo_role_overrides_a_generic_agent_and_never_uses_fallback():
    status, payload = call({"question": "当前最大风险？", "agent": "sales-ai", "role": "ceo", "permission_scope": ["enterprise:read"]})
    assert status == 200
    assert payload["agent"] == "huyan-ceo-intelligence"
    for section in ("经营摘要", "数据依据", "风险", "AI建议", "Citation"):
        assert section in payload["content"]
