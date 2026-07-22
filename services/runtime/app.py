"""Read-only FoxBrain Runtime router for WeCom business questions.

The runtime is deliberately the only component that selects business data and
intelligence routes.  An LLM may phrase the evidence supplied here, but it is
never allowed to invent a business fact or initiate an operational action.
"""
from __future__ import annotations

import json
import os
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from urllib.request import Request, urlopen

from packages.vafox_foundation.http import json_response, service_app


ROLE_ROUTES = {
    "ceo": ("huyan-ceo-intelligence", ("Core Data", "Retail Brain", "Customer Brain"), "enterprise:read"),
    "store_manager": ("store-intelligence", ("Store", "Sales", "Customer"), "store:read"),
    "buyer": ("procurement-intelligence", ("Product", "Inventory"), "procurement:read"),
    "purchaser": ("procurement-intelligence", ("Product", "Inventory"), "procurement:read"),
    "employee": ("sales-intelligence", ("Product", "Customer"), "sales:read"),
}

ROLE_DOMAINS = {
    "ceo": ("sales", "inventory", "customers"),
    "buyer": ("products", "inventory"), "purchaser": ("products", "inventory"),
    "store_manager": ("stores", "sales", "customers"), "employee": ("products", "customers"),
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


class CoreEvidenceAdapter(EvidenceRepository):
    """Adapt governed Core Data domain responses into runtime citations.

    ``reader`` is injected by deployment (HTTP client, SDK, or test double).
    The adapter deliberately returns no evidence for an unavailable or malformed
    domain instead of substituting generated business facts.
    """
    def __init__(self, reader):
        self.reader = reader

    @classmethod
    def from_environment(cls):
        """Create the production reader only when an explicit core token exists."""
        base_url, token = os.getenv("CORE_DATA_URL", "").rstrip("/"), os.getenv("CORE_DATA_TOKEN", "")
        if not base_url or not token:
            return EvidenceRepository()

        def reader(domain, data_scope):
            headers = {"Authorization": "Bearer " + token}
            request = Request(base_url + "/api/v1/" + domain, headers=headers, method="GET")
            try:
                with urlopen(request, timeout=3) as response:
                    return json.loads(response.read())
            except (OSError, ValueError):
                return None
        return cls(reader)

    def collect(self, identity, route, sources, query):
        evidence = []
        for domain in ROLE_DOMAINS.get(identity.role, ()):
            payload = self.reader(domain, identity.data_scope)
            if not isinstance(payload, dict) or not isinstance(payload.get("data"), list):
                continue
            timestamp = payload.get("timestamp")
            version = payload.get("version")
            confidence = payload.get("confidence")
            if not (payload.get("source") and timestamp and version and isinstance(confidence, (int, float))):
                continue
            if not payload["data"]:
                continue
            evidence.append({"source": payload["source"], "citation": f"{payload['source']}@{timestamp}",
                             "summary": f"已验证 {domain} 数据（{len(payload['data'])} 条）。",
                             "timestamp": timestamp, "version": version, "confidence": confidence})
        return evidence


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
        citations.append({"source": item.get("source", "Business Evidence"), "citation": item["citation"], "summary": item["summary"],
                          "timestamp": item.get("timestamp", datetime.now(timezone.utc).isoformat()),
                          "version": item.get("version", "v1"), "confidence": item.get("confidence", 0.0)})
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
    router = router or RuntimeRouter(CoreEvidenceAdapter.from_environment())
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
