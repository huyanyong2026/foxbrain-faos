"""Business Application Layer V1.

This boundary intentionally returns advice only.  It has no connector or
command for SAP/Core writes, ordering, marketing delivery, or procurement.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from urllib.parse import parse_qs
from wsgiref.simple_server import make_server

from packages.vafox_foundation.http import json_response, service_app
from services.memory.acl import auth_context

ADVISORY_NOTICE = "AI 仅提供查询、分析与建议；需由授权员工核实并人工执行。"
EMPLOYEE_ROLES = frozenset({"employee", "sales", "store_manager", "operation", "ceo", "admin"})
CEO_ROLES = frozenset({"ceo", "admin"})

KAILAS_BRAND = {
    "brand": "KAILAS", "positioning": "面向专业户外与山地活动的技术装备品牌",
    "customer": ["进阶徒步者", "高海拔旅行者", "重视防护与耐用性的户外用户"],
    "scenario": ["深圳徒步", "川西7天", "冈仁波齐"],
    "citation": {"source": "KAILAS Brand Profile V1", "locator": "#brand-profile"},
}
MONT_CARD = {
    "product": "MONT", "category": "冲锋衣", "technology": ["防水透湿面料", "防风结构", "耐候接缝处理"],
    "scenario": ["深圳徒步", "川西7天", "冈仁波齐"],
    "customer_profile": ["需要应对降雨和风寒的徒步者", "多日高海拔行程参与者"],
    "recommendation": "作为外层防护装备，按天气、强度和尺码与保暖层搭配。",
    "citation": [{"source": "KAILAS MONT Product Card V1", "locator": "#mont"}],
}
SCENARIOS = {
    "深圳周末徒步": {"equipment": ["MONT冲锋衣", "速干内层", "防滑徒步鞋", "饮水装备"], "reason": "应对短时降雨、闷热和湿滑路面。"},
    "深圳徒步": {"equipment": ["MONT冲锋衣", "速干内层", "防滑徒步鞋", "饮水装备"], "reason": "应对短时降雨、闷热和湿滑路面。"},
    "川西7天": {"equipment": ["MONT冲锋衣", "保暖中层", "排汗内层", "防水徒步鞋"], "reason": "多日行程温差大，外层防护应与保暖分层组合。"},
    "冈仁波齐": {"equipment": ["MONT冲锋衣", "高保暖中层", "排汗内层", "防晒与保温配件"], "reason": "高海拔环境需优先考虑防风、防水、保暖和分层。"},
}


def _now(): return datetime.now(timezone.utc).isoformat()
def _body(environ):
    try: return json.loads(environ["wsgi.input"].read(int(environ.get("CONTENT_LENGTH") or 0)) or b"{}")
    except (ValueError, TypeError): raise ValueError("invalid_json")
def _query(environ): return {k: v[-1] for k, v in parse_qs(environ.get("QUERY_STRING", "")).items()}


class BusinessStore:
    """Small deterministic read model with an append-only audit trail."""
    def __init__(self, core_client=None):
        self.core_client, self.audit_events = core_client, []

    def audit(self, context, action, detail=None):
        self.audit_events.append({"at": _now(), "action": action, "actor_id": context.owner_id,
                                  "organization_id": context.organization_id, "detail": detail or {}})

    def opportunities(self, context):
        items = [{"type": "customer", "title": "重点客户回访", "customer": "C1", "reason": "近期购买冲锋衣，可确认实际使用场景与搭配需求。"}]
        if "store_manager" in context.role_scopes:
            items.append({"type": "store", "title": "门店防雨装备关注", "store_id": context.department_id or "assigned-store", "reason": "请核实热销尺码与雨天陈列。"})
        return items


def create_app(store=None):
    store = store or BusinessStore()

    def context(environ, start_response, allowed):
        value = auth_context(environ)
        if not value: return None, (401, {"error": "authentication_required"})
        if not (value.role_scopes & allowed) and not value.is_admin:
            return None, (403, {"error": "permission_denied"})
        return value, None

    def tasks(environ, start_response):
        ctx, error = context(environ, start_response, EMPLOYEE_ROLES)
        if error: return json_response(start_response, *error)
        payload = {"items": [{"id": "task:follow-up-c1", "title": "跟进重点客户", "status": "suggested", "advisory_only": True}], "notice": ADVISORY_NOTICE}
        store.audit(ctx, "workspace_tasks_read"); return json_response(start_response, 200, payload)

    def opportunities(environ, start_response):
        ctx, error = context(environ, start_response, EMPLOYEE_ROLES)
        if error: return json_response(start_response, *error)
        payload = {"items": store.opportunities(ctx), "data_scope": {"department_id": ctx.department_id}, "notice": ADVISORY_NOTICE}
        store.audit(ctx, "workspace_opportunities_read"); return json_response(start_response, 200, payload)

    def advice(environ, start_response):
        ctx, error = context(environ, start_response, EMPLOYEE_ROLES)
        if error: return json_response(start_response, *error)
        try: request = _body(environ)
        except ValueError as error: return json_response(start_response, 400, {"error": str(error)})
        kind, prompt = str(request.get("type", "")).strip(), str(request.get("query", "")).strip()
        if kind not in {"product", "sales", "scenario", "customer"} or not prompt: return json_response(start_response, 400, {"error": "type_and_query_required"})
        if kind == "product": answer = {"product": MONT_CARD, "product_positioning": "多场景户外外层防护", "use_cases": MONT_CARD["scenario"], "customer_profile": MONT_CARD["customer_profile"], "bundle": "搭配排汗内层与按温度选择的保暖中层。", "citation": MONT_CARD["citation"]}
        elif kind == "sales": answer = {"need_analysis": "客户对价格的顾虑通常与耐用性、使用频率和场景匹配有关。", "value_explanation": "将防护、耐候与分层使用价值与客户的真实行程对应说明。", "sales_talk": "可以先确认您常去的路线和天气，再看这件外层能否减少额外防护装备的需求。", "recommendation": "先核实预算、尺码和实际库存后提供可选搭配。"}
        elif kind == "scenario":
            name = str(request.get("destination", prompt)).strip(); scenario = SCENARIOS.get(name)
            if not scenario: return json_response(start_response, 422, {"error": "unsupported_scenario", "supported": list(SCENARIOS)})
            answer = {"destination": name, "time": request.get("time"), "budget": request.get("budget"), "experience": request.get("experience"), **scenario, "citation": MONT_CARD["citation"]}
        else:
            if not ({"customers:read", "customer:read"} & ctx.role_scopes or ctx.is_admin): return json_response(start_response, 403, {"error": "customer_scope_required"})
            answer = {"customer": {"id": "C1", "name": "顾客"}, "purchase_history": ["KAILAS 冲锋衣"], "gear_profile": ["雨天徒步外层"], "data_scope": {"department_id": ctx.department_id}}
        answer.update({"advisory_only": True, "notice": ADVISORY_NOTICE})
        store.audit(ctx, "workspace_advice", {"type": kind}); return json_response(start_response, 200, answer)

    def dashboard(environ, start_response):
        ctx, error = context(environ, start_response, CEO_ROLES)
        if error: return json_response(start_response, *error)
        payload = {"sales_summary": "销售数据为只读摘要；请结合当日门店数据核实。", "inventory_alerts": ["关注防雨外层的尺码结构与门店可售状态。"], "product_opportunities": ["MONT可用于高海拔与雨天徒步场景讲解。"], "customer_opportunities": store.opportunities(ctx), "ai_recommendations": ["优先复核重点客户需求，再由员工决定后续动作。"], "read_only": True, "notice": ADVISORY_NOTICE}
        store.audit(ctx, "ceo_dashboard_read"); return json_response(start_response, 200, payload)

    def kailas(environ, start_response):
        ctx, error = context(environ, start_response, EMPLOYEE_ROLES)
        if error: return json_response(start_response, *error)
        product = _query(environ).get("product", "MONT").upper()
        if product != "MONT": return json_response(start_response, 404, {"error": "product_not_found"})
        payload = {"brand_profile": KAILAS_BRAND, "product_card": MONT_CARD, "scenario_mapping": SCENARIOS, "advisory_only": True, "notice": ADVISORY_NOTICE}
        store.audit(ctx, "kailas_product_read", {"product": product}); return json_response(start_response, 200, payload)

    def wechat(environ, start_response):
        ctx, error = context(environ, start_response, EMPLOYEE_ROLES)
        if error: return json_response(start_response, *error)
        try: message = str(_body(environ).get("message", "")).strip()
        except ValueError as error: return json_response(start_response, 400, {"error": str(error)})
        if not message: return json_response(start_response, 400, {"error": "message_required"})
        if "今日经营" in message:
            if not (ctx.role_scopes & CEO_ROLES or ctx.is_admin): return json_response(start_response, 403, {"error": "ceo_role_required"})
            reply = "今日经营摘要：请关注销售、库存和重点客户机会；所有数据为只读建议。"
        elif "关注什么" in message and "store_manager" in ctx.role_scopes: reply = "门店建议：核实销售节奏、雨天外层库存和重点客户回访。"
        else: reply = "重点客户机会：可回访近期购买冲锋衣的客户，确认实际场景与搭配需求。"
        store.audit(ctx, "wechat_message", {"message_type": "ceo" if "今日经营" in message else "employee"}); return json_response(start_response, 200, {"reply": reply, "identity": {"user_id": ctx.owner_id, "role_scopes": sorted(ctx.role_scopes)}, "audit_logged": True, "advisory_only": True, "notice": ADVISORY_NOTICE})

    routes = {("GET", "/api/workspace/tasks"): tasks, ("GET", "/api/workspace/opportunities"): opportunities, ("POST", "/api/workspace/advice"): advice, ("GET", "/api/ceo/dashboard"): dashboard, ("GET", "/api/kailas/product"): kailas, ("POST", "/api/wechat/message"): wechat}
    health = service_app("business")
    def app(environ, start_response):
        handler = routes.get((environ["REQUEST_METHOD"], environ["PATH_INFO"]))
        return handler(environ, start_response) if handler else health(environ, start_response)
    return app


app = create_app()
if __name__ == "__main__": make_server("0.0.0.0", 8080, app).serve_forever()
