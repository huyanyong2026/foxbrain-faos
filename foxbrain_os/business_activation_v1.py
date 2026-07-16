"""Business Activation V1 application layer.

Deterministic daily-operation services built on top of Core facts and AI
recommendations.  The module intentionally does not mutate SAP/Core data: it
turns supplied Enterprise Data Core snapshots into approval-ready work items,
dashboards, WeCom answers, exports, and audit events.
"""

from __future__ import annotations

import csv
import io
import math
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone


BA_VERSION = "BA-V1.0"
CORE_SOURCE = "core.vafox.com"
AI_SOURCE = "ai.vafox.com"
GATEWAY_SOURCE = "gateway.vafox.com"
HUYAN_SOURCE = "huyan.vafox.com"


@dataclass(frozen=True)
class AuditEvent:
    actor_id: str
    action: str
    resource: str
    decision: str
    reason: str
    occurred_at: str


@dataclass(frozen=True)
class BusinessActivationContext:
    user_id: str
    roles: tuple[str, ...]
    permissions: tuple[str, ...]
    data_scope: str = "self"
    store_codes: tuple[str, ...] = ()

    def can(self, permission: str) -> bool:
        return "*" in self.permissions or permission in self.permissions


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _number(value) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def _int(value) -> int:
    return int(math.ceil(max(0, _number(value))))


def check_permission(context: BusinessActivationContext, permission: str, resource_store: str | None = None) -> AuditEvent:
    allowed = context.can(permission)
    reason = "permission granted"
    if allowed and context.data_scope == "store" and resource_store:
        allowed = resource_store in context.store_codes
        reason = "store scope granted" if allowed else "store scope denied"
    elif not allowed:
        reason = "missing permission: {}".format(permission)
    return AuditEvent(context.user_id, "permission_check", resource_store or permission, "allowed" if allowed else "denied", reason, _now_iso())


def require_permission(context: BusinessActivationContext, permission: str, resource_store: str | None = None) -> AuditEvent:
    event = check_permission(context, permission, resource_store)
    if event.decision != "allowed":
        raise PermissionError(event.reason)
    return event


def replenishment_recommendations(facts: list[dict]) -> list[dict]:
    results = []
    for row in facts:
        sales_30 = _number(row.get("sales_30d"))
        previous_30 = _number(row.get("sales_prev_30d"))
        stock = _number(row.get("inventory_qty"))
        incoming = _number(row.get("incoming_qty"))
        daily = sales_30 / 30 if sales_30 > 0 else 0
        target = math.ceil(daily * 30)
        suggested = _int(target - stock - incoming)
        stock_days = None if daily == 0 else round(stock / daily, 1)
        priority = "high" if suggested > 0 and (stock_days is None or stock_days < 7 or sales_30 > previous_30 * 1.2) else "normal"
        reason = "Sales increase + inventory decline" if sales_30 > previous_30 and suggested > 0 else "Target 30-day coverage from Core sales/inventory facts"
        if suggested > 0:
            results.append({
                "product": row.get("product_name") or row.get("sku"),
                "sku": row.get("sku"),
                "brand": row.get("brand"),
                "store": row.get("store_name") or row.get("store_code"),
                "store_code": row.get("store_code"),
                "suggested_quantity": suggested,
                "priority": priority,
                "reason": reason,
                "source": CORE_SOURCE,
                "requires_human_approval": True,
            })
    return sorted(results, key=lambda item: (item["priority"] != "high", item["store"], item["product"]))


def overstock_intelligence(facts: list[dict]) -> list[dict]:
    results = []
    for row in facts:
        stock = _number(row.get("inventory_qty"))
        sales_90 = _number(row.get("sales_90d"))
        aging = _int(row.get("aging_days"))
        value = round(stock * _number(row.get("unit_cost")), 2)
        if stock <= 0:
            continue
        if aging >= 180 or (sales_90 <= 1 and value >= 1000):
            action = "clearance" if aging >= 270 else "promotion"
        elif sales_90 <= 3 and value >= 500:
            action = "transfer"
        else:
            action = "keep"
        if action != "keep":
            results.append({
                "product": row.get("product_name") or row.get("sku"),
                "sku": row.get("sku"),
                "brand": row.get("brand"),
                "store": row.get("store_name") or row.get("store_code"),
                "store_code": row.get("store_code"),
                "inventory_value": value,
                "aging_days": aging,
                "recommendation": action,
                "reason": "Slow movement, aging stock, and inventory value from Core facts",
                "source": CORE_SOURCE,
                "requires_human_approval": True,
            })
    return sorted(results, key=lambda item: (item["recommendation"], -item["inventory_value"]))


def inventory_health_score(facts: list[dict]) -> list[dict]:
    by_store = defaultdict(list)
    for row in facts:
        by_store[(row.get("store_code"), row.get("store_name") or row.get("store_code"))].append(row)
    scores = []
    for (store_code, store_name), rows in by_store.items():
        replenishment = replenishment_recommendations(rows)
        overstock = overstock_intelligence(rows)
        low_stock = len(replenishment)
        overstock_count = len(overstock)
        score = max(0, min(100, 100 - low_stock * 4 - overstock_count * 2))
        scores.append({
            "store_code": store_code,
            "store": store_name,
            "health": score,
            "risk": {"low_stock": low_stock, "overstock": overstock_count},
            "source": CORE_SOURCE,
        })
    return sorted(scores, key=lambda item: item["store"])


def supply_chain_dashboard(facts: list[dict]) -> dict:
    replenishment = replenishment_recommendations(facts)
    overstock = overstock_intelligence(facts)
    health = inventory_health_score(facts)
    brand_status = defaultdict(lambda: {"replenishment_tasks": 0, "overstock_items": 0})
    for item in replenishment:
        brand_status[item.get("brand") or "unassigned"]["replenishment_tasks"] += 1
    for item in overstock:
        brand_status[item.get("brand") or "unassigned"]["overstock_items"] += 1
    return {"version": BA_VERSION, "source": CORE_SOURCE, "replenishment_tasks": replenishment, "inventory_risks": health, "overstock": overstock, "brand_status": dict(brand_status)}


def ceo_dashboard(facts: list[dict]) -> dict:
    sales = sum(_number(row.get("sales_amount_30d")) for row in facts)
    gross_margin = sum(_number(row.get("gross_margin_30d")) for row in facts)
    inventory = sum(_number(row.get("inventory_qty")) * _number(row.get("unit_cost")) for row in facts)
    supply_chain = supply_chain_dashboard(facts)
    return {"source": HUYAN_SOURCE, "data_source": CORE_SOURCE, "sales": round(sales, 2), "gross_margin": round(gross_margin, 2), "inventory_value": round(inventory, 2), "supply_chain": supply_chain, "ai_recommendations": supply_chain["replenishment_tasks"][:5] + supply_chain["overstock"][:5]}


def daily_ceo_briefing(facts: list[dict]) -> dict:
    dashboard = ceo_dashboard(facts)
    top = dashboard["ai_recommendations"][:3]
    what = "Sales {:.2f}, gross margin {:.2f}, inventory {:.2f}".format(dashboard["sales"], dashboard["gross_margin"], dashboard["inventory_value"])
    why = "Derived from Core sales, inventory, store, product, and brand facts; AI layer ranks exceptions."
    return {"source": AI_SOURCE, "evidence_source": CORE_SOURCE, "what_happened_today": what, "why_happened": why, "recommended_actions": top, "requires_human_approval": True}


def risk_radar(facts: list[dict]) -> dict:
    health = inventory_health_score(facts)
    return {"sales_risk": sum(1 for row in facts if _number(row.get("sales_30d")) < _number(row.get("sales_prev_30d")) * 0.7), "inventory_risk": sum(item["risk"]["low_stock"] + item["risk"]["overstock"] for item in health), "supply_risk": len(replenishment_recommendations(facts)), "store_risk": sum(1 for item in health if item["health"] < 80), "source": CORE_SOURCE}


def decision_center(problem: str, facts: list[dict]) -> dict:
    brief = daily_ceo_briefing(facts)
    return {"problem": problem, "reason": brief["why_happened"], "recommendation": brief["recommended_actions"], "action": "pending_human_approval", "source": AI_SOURCE}


def store_dashboard(facts: list[dict], store_code: str) -> dict:
    store_facts = [row for row in facts if row.get("store_code") == store_code]
    sales = sum(_number(row.get("sales_amount_30d")) for row in store_facts)
    health = inventory_health_score(store_facts)[0] if store_facts else {"store_code": store_code, "health": 0, "risk": {"low_stock": 0, "overstock": 0}}
    tasks = replenishment_recommendations(store_facts)[:10] + overstock_intelligence(store_facts)[:10]
    return {"store_code": store_code, "sales": round(sales, 2), "inventory_health": health, "tasks": tasks, "ai_suggestions": tasks[:5], "source": CORE_SOURCE}


def store_ai_assistant(question: str, facts: list[dict], store_code: str) -> dict:
    dashboard = store_dashboard(facts, store_code)
    return {"question": question, "answer": ["Review low-stock and overstock risks", "Follow top replenishment/transfer tasks", "Escalate actions needing approval"], "inventory_risks": dashboard["inventory_health"]["risk"], "recommended_actions": dashboard["ai_suggestions"], "source": AI_SOURCE}


def wecom_ai_query(question: str, facts: list[dict], context: BusinessActivationContext) -> dict:
    require_permission(context, "knowledge.read")
    q = question.lower()
    visible = facts if context.data_scope == "company" else [row for row in facts if row.get("store_code") in context.store_codes]
    matched = [row for row in visible if str(row.get("product_name") or "").lower() in q or str(row.get("brand") or "").lower() in q or str(row.get("store_name") or "").lower() in q]
    if not matched:
        matched = visible[:5]
    return {"question": question, "data_source": CORE_SOURCE, "permission_scope": context.data_scope, "results": [{"product": row.get("product_name"), "inventory": row.get("inventory_qty"), "store": row.get("store_name"), "brand": row.get("brand")} for row in matched[:10]]}


def export_report_csv(rows: list[dict], report_name: str) -> str:
    fields = sorted({key for row in rows for key in row.keys()}) or ["empty"]
    stream = io.StringIO()
    writer = csv.DictWriter(stream, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)
    return "# {}\n{}".format(report_name, stream.getvalue())
