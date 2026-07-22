"""Read-only FoxBrain Runtime router for WeCom business questions.

The runtime is deliberately the only component that selects business data and
intelligence routes.  An LLM may phrase the evidence supplied here, but it is
never allowed to invent a business fact or initiate an operational action.
"""
from __future__ import annotations

import json
import uuid
from dataclasses import dataclass

from packages.vafox_foundation.http import json_response, service_app


ROLE_ROUTES = {
    "ceo": ("huyan-ceo-intelligence", ("Core Data", "Retail Brain", "Customer Brain"), "enterprise:read"),
    "store_manager": ("store-intelligence", ("Retail Brain", "Store Data"), "store:read"),
    "buyer": ("procurement-intelligence", ("Product Intelligence", "Inventory", "Brand Knowledge"), "procurement:read"),
    "purchaser": ("procurement-intelligence", ("Product Intelligence", "Inventory", "Brand Knowledge"), "procurement:read"),
    "employee": ("sales-intelligence", ("Product Intelligence", "Customer Brain"), "sales:read"),
}


@dataclass(frozen=True)
class RuntimeIdentity:
    user_id: str
    wecom_user_id: str
    role: str
    permissions: frozenset[str]
    data_scope: object


class EvidenceRepository:
    """Read-only evidence seam for Core/Retail/Customer and related brains."""
    def collect(self, identity, route, sources, query):
        return []


class RuntimeRouter:
    def __init__(self, evidence=None):
        self.evidence = evidence or EvidenceRepository()

    def query(self, payload):
        required = ("user_id", "wecom_user_id", "role", "scope", "query")
        if not isinstance(payload, dict) or any(not str(payload.get(key, "")).strip() for key in required):
            raise ValueError("invalid_runtime_wecom_request")
        role = str(payload["role"]).lower()
        if role not in ROLE_ROUTES:
            raise PermissionError("unsupported_role")
        permissions, scope = _scope(payload["scope"])
        route, sources, required_permission = ROLE_ROUTES[role]
        if required_permission not in permissions:
            raise PermissionError("rbac_denied")
        identity = RuntimeIdentity(str(payload["user_id"]), str(payload["wecom_user_id"]), role, permissions, scope)
        evidence = self.evidence.collect(identity, route, sources, str(payload["query"]))
        return _business_response(route, sources, evidence)


def _scope(value):
    if isinstance(value, dict):
        permissions = value.get("permissions", value.get("permission", []))
        scope = value.get("data_scope", value.get("store_scope"))
    else:
        permissions, scope = value, None
    if isinstance(permissions, str): permissions = [permissions]
    return frozenset(permissions or []), scope


def _business_response(route, source_names, evidence):
    citations = []
    for item in evidence:
        if not isinstance(item, dict) or not item.get("citation") or not item.get("summary"):
            continue
        citations.append({"source": item.get("source", "Business Evidence"), "citation": item["citation"], "summary": item["summary"]})
    if citations:
        summary = "；".join(item["summary"] for item in citations)
        basis = "；".join(f"{item['source']}: {item['citation']}" for item in citations)
        risk = "请持续监测数据时效、范围与异常变化。"
        advice = "基于上述已验证数据安排人工复核后再决策。"
        confidence = "high"
    else:
        summary = "当前没有可验证的经营数据，不能生成经营事实。"
        basis = "未返回可引用的业务证据。"
        risk = "数据缺失；任何经营结论均需人工核实。"
        advice = "请先同步所需业务数据，再由 Runtime 重新分析。"
        confidence = "low"
    citation = {"route": route, "sources": list(source_names), "evidence": citations, "mode": "read_only"}
    answer = "\n".join((f"经营摘要：{summary}", f"数据依据：{basis}", f"风险：{risk}", f"AI建议：{advice}", f"Citation：{json.dumps(citation, ensure_ascii=False)}"))
    return {"answer": answer, "sources": list(source_names), "citation": citation, "confidence": confidence, "audit_id": str(uuid.uuid4())}


def create_app(router=None):
    router = router or RuntimeRouter()
    def wecom_query(environ, start_response):
        try:
            body = environ["wsgi.input"].read(int(environ.get("CONTENT_LENGTH") or 0))
            result = router.query(json.loads(body))
        except (json.JSONDecodeError, ValueError):
            return json_response(start_response, 400, {"error": "invalid_runtime_wecom_request"}), 400
        except PermissionError as error:
            return json_response(start_response, 403, {"error": str(error)}), 403
        return json_response(start_response, 200, result), 200
    return service_app("runtime", {("POST", "/api/runtime/wecom/query"): wecom_query})


app = create_app()
