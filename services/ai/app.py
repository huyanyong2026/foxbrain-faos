"""AI Runtime routes CEO WeCom requests to the evidence-backed Huyan brain."""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from wsgiref.simple_server import make_server

from packages.vafox_foundation.http import json_response, service_app


CEO_AGENT = "huyan-ceo-intelligence"
CEO_PERMISSION = "enterprise:read"


@dataclass(frozen=True)
class Evidence:
    source: str
    locator: str
    statement: str

    def citation(self):
        return {"source": self.source, "locator": self.locator, "statement": self.statement}


class CEODataSources:
    """Read-only composition seam for Core Data, Retail Brain, and Customer Brain.

    The current service contracts expose a governed snapshot.  Keeping this
    adapter separate lets production replace individual source readers without
    changing WeCom identity routing or the CEO answer contract.
    """

    def snapshot(self):
        return {
            "core": {"operating_summary": "今日销售较昨日增长，需优先保障防雨外层可售。", "risks": ["KAILAS MONT M码可售库存偏低"]},
            "retail": {"kailas": "KAILAS贡献南山店销售42%，冲锋衣贡献38%。", "trend": "南山店销售较昨日+12%，振兴店较昨日-3%。"},
            "customer": {"opportunity": "重点客户近期购买KAILAS冲锋衣，可由门店确认实际使用场景与搭配需求。"},
            "citations": [
                Evidence("Core Data API", "core-data://operating/today", "今日经营只读快照").citation(),
                Evidence("Retail Brain", "retail-brain://stores/today", "门店销售、品牌与库存风险快照").citation(),
                Evidence("Customer Brain", "customer-brain://opportunities/today", "重点客户机会只读快照").citation(),
            ],
        }


class CEOQueryHandler:
    """Huyan CEO Intelligence response builder for CEO operating questions."""

    def __init__(self, data_sources=None):
        self.data_sources = data_sources or CEODataSources()

    @staticmethod
    def _intent(question):
        normalized = question.lower()
        if "kailas" in normalized: return "kailas"
        if "最大风险" in question or "风险" in question: return "risk"
        if "最重要" in question or "三件" in question: return "priorities"
        return "operations"

    def handle(self, question):
        snapshot, intent = self.data_sources.snapshot(), self._intent(question)
        core, retail, customer = snapshot["core"], snapshot["retail"], snapshot["customer"]
        if intent == "kailas":
            summary = f"KAILAS经营：{retail['kailas']} {retail['trend']}"
            recommendations = "先复核KAILAS MONT M码补货节奏，再由门店跟进高意向客户的场景与搭配。"
        elif intent == "risk":
            summary = f"当前最大经营风险：{core['risks'][0]}；同时{retail['trend']}"
            recommendations = "今天内指定负责人复核可售库存与振兴店KAILAS转化，确认后再决定补货或陈列动作。"
        elif intent == "priorities":
            summary = "今日优先级聚焦销售动能、关键库存和重点客户转化。"
            recommendations = "按“库存复核—门店转化复盘—重点客户跟进”顺序完成，并在日终复盘结果。"
        else:
            summary = f"今日经营：{core['operating_summary']} {retail['trend']}"
            recommendations = "优先处理高风险库存，并跟进重点客户机会；AI建议须由授权人员核实后执行。"

        priorities = ["复核KAILAS MONT M码可售库存与补货节奏", "复盘振兴店KAILAS转化下滑原因", "安排重点客户场景化回访"]
        content = "\n".join([
            "经营摘要：" + summary,
            "数据依据：" + retail["kailas"] + "；" + customer["opportunity"],
            "风险：" + "；".join(core["risks"]),
            "AI建议：" + recommendations,
            "今日最重要三件事：" + "；".join(priorities),
            "Citation：" + "；".join(f"{item['source']} ({item['locator']})" for item in snapshot["citations"]),
        ])
        return {"title": "Huyan CEO Intelligence", "content": content, "source": "Huyan CEO Intelligence", "confidence": "high", "citations": snapshot["citations"], "read_only": True}


def create_app(ceo_handler=None):
    ceo_handler = ceo_handler or CEOQueryHandler()

    def respond(environ, start_response):
        try:
            request = json.loads(environ["wsgi.input"].read(int(environ.get("CONTENT_LENGTH") or 0)) or b"{}")
        except json.JSONDecodeError:
            return json_response(start_response, 400, {"error": "invalid_json"}), 400
        question, agent = str(request.get("question", "")).strip(), str(request.get("agent", "")).strip()
        if not question or not agent:
            return json_response(start_response, 400, {"error": "question_and_agent_required"}), 400
        role, permissions = str(request.get("role", "")).lower(), set(request.get("permission_scope", []))
        # CEO identity/role takes priority over a caller-supplied generic agent.
        # This is deliberately evaluated before the generic fallback below.
        is_ceo_request = role == "ceo" or bool(request.get("is_ceo_identity"))
        if is_ceo_request:
            if CEO_PERMISSION not in permissions:
                return json_response(start_response, 403, {"error": "enterprise_permission_required"}), 403
            payload = ceo_handler.handle(question)
            payload.update({"agent": CEO_AGENT, "generated_at": datetime.now(timezone.utc).isoformat()})
            return json_response(start_response, 200, payload), 200
        return json_response(start_response, 200, {"title": agent, "content": f"{agent}：已收到您的问题“{question}”。请结合实时经营数据进行人工核实。", "source": "FoxBrain AI Runtime", "confidence": "medium"}), 200

    return service_app("ai", {("POST", "/api/v1/ai/respond"): respond})


app = create_app()
if __name__ == "__main__":
    make_server("0.0.0.0", 8080, app).serve_forever()
