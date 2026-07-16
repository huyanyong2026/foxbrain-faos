"""Business Activation V2 advanced supply-chain intelligence.

Deterministic engines for demand forecast, predictive purchase planning,
store transfers, brand intelligence, supplier collaboration, Huyan command
center, and workflow tasks.  The module consumes existing Core/SAP-derived
facts supplied by callers and never creates or mutates an inventory database.
"""

from __future__ import annotations

import math
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone

BA_V2_VERSION = "BA-V2.0-A"
CORE_SOURCE = "core.vafox.com"
AI_SOURCE = "ai.vafox.com"
HUYAN_SOURCE = "huyan.vafox.com"
WORKFLOW_SOURCE = "core.vafox.com/workflow"
SUPPORTED_BRANDS = ("Osprey", "Mammut", "KAILAS", "Deuter", "BD")


@dataclass(frozen=True)
class SupplyChainContext:
    user_id: str
    roles: tuple[str, ...]
    permissions: tuple[str, ...]
    store_codes: tuple[str, ...] = ()
    brand_scope: tuple[str, ...] = ()

    def can(self, permission: str) -> bool:
        return "*" in self.permissions or permission in self.permissions


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _number(value) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def _ceil(value: float) -> int:
    return int(math.ceil(max(0, value)))


def _row_brand(row: dict) -> str:
    return str(row.get("brand") or row.get("brand_name") or "Other")


def _row_store(row: dict) -> str:
    return str(row.get("store_code") or row.get("store") or "")


def _row_store_name(row: dict) -> str:
    return str(row.get("store_name") or row.get("store") or _row_store(row))


def _row_product(row: dict) -> str:
    return str(row.get("product_name") or row.get("product") or row.get("sku") or "")


def _trend(row: dict) -> float:
    current = _number(row.get("sales_30d"))
    previous = _number(row.get("sales_prev_30d"))
    if previous <= 0:
        return 1.0 if current <= 0 else 1.25
    return max(0.5, min(2.0, current / previous))


def demand_forecast(facts: list[dict], period_days: int = 30) -> list[dict]:
    """Forecast product/store demand from Core facts with confidence/reason."""
    forecasts = []
    for row in facts:
        sales_30 = _number(row.get("sales_30d"))
        sales_90 = _number(row.get("sales_90d"))
        base_daily = sales_30 / 30 if sales_30 > 0 else sales_90 / 90
        trend = _trend(row)
        seasonal = _number(row.get("season_factor")) or 1.0
        promo = _number(row.get("promotion_factor")) or 1.0
        customer = _number(row.get("customer_trend_factor")) or 1.0
        expected = _ceil(base_daily * period_days * trend * seasonal * promo * customer)
        confidence = round(min(0.95, max(0.5, 0.62 + min(sales_90, 90) / 300 + (0.08 if sales_30 > 0 else 0))), 2)
        reason_bits = ["historical sales", "inventory", "product", "brand", "store"]
        if seasonal != 1.0:
            reason_bits.append("season")
        if promo != 1.0:
            reason_bits.append("promotion")
        if customer != 1.0:
            reason_bits.append("customer trend")
        forecasts.append({
            "product": _row_product(row),
            "sku": row.get("sku"),
            "brand": _row_brand(row),
            "store": _row_store_name(row),
            "store_code": _row_store(row),
            "time_period_days": period_days,
            "expected_demand": expected,
            "confidence_score": confidence,
            "reason": " + ".join(reason_bits),
            "source": CORE_SOURCE,
            "engine": "AI Demand Forecast Engine",
        })
    return sorted(forecasts, key=lambda item: (-item["expected_demand"], item["brand"], item["product"]))


def purchase_planning(facts: list[dict], forecasts: list[dict] | None = None) -> list[dict]:
    forecasts = forecasts or demand_forecast(facts)
    by_key = {(f["store_code"], f.get("sku")): f for f in forecasts}
    plans = []
    for row in facts:
        forecast = by_key.get((_row_store(row), row.get("sku")))
        expected = _number(forecast["expected_demand"]) if forecast else 0
        stock = _number(row.get("inventory_qty")) + _number(row.get("incoming_qty"))
        safety = _number(row.get("safety_stock")) or max(2, expected * 0.2)
        gap = expected + safety - stock
        if gap <= 0:
            continue
        lead_time = _ceil(_number(row.get("supplier_lead_time_days")) or _number(row.get("lead_time_days")) or 14)
        timing = "order_now" if stock <= safety or lead_time >= 14 else "order_within_7_days"
        plans.append({
            "brand": _row_brand(row),
            "product": _row_product(row),
            "sku": row.get("sku"),
            "store": _row_store_name(row),
            "quantity": _ceil(gap),
            "purchase_timing": timing,
            "supplier_lead_time_days": lead_time,
            "reason": "Expected demand growth + inventory risk + safety stock",
            "requires_human_approval": True,
            "source": AI_SOURCE,
        })
    return sorted(plans, key=lambda item: (item["purchase_timing"] != "order_now", -item["quantity"]))


def inventory_transfer_suggestions(facts: list[dict], forecasts: list[dict] | None = None) -> list[dict]:
    forecasts = forecasts or demand_forecast(facts)
    demand = {(f["store_code"], f.get("sku")): _number(f["expected_demand"]) for f in forecasts}
    groups = defaultdict(list)
    for row in facts:
        groups[row.get("sku")].append(row)
    suggestions = []
    for sku, rows in groups.items():
        surplus = []
        shortage = []
        for row in rows:
            needed = demand.get((_row_store(row), sku), 0)
            stock = _number(row.get("inventory_qty"))
            delta = stock - needed
            (surplus if delta > 3 else shortage if delta < -2 else []).append((row, abs(delta)))
        for dst, need in shortage:
            for src, extra in surplus:
                if _row_store(src) == _row_store(dst):
                    continue
                qty = _ceil(min(need, extra))
                if qty <= 0:
                    continue
                suggestions.append({
                    "from_store": _row_store_name(src),
                    "to_store": _row_store_name(dst),
                    "product": _row_product(dst),
                    "sku": sku,
                    "quantity": qty,
                    "reason": "Sales speed and forecast demand difference between stores",
                    "requires_human_approval": True,
                    "source": AI_SOURCE,
                })
                break
    return suggestions


def brand_intelligence(facts: list[dict], forecasts: list[dict] | None = None) -> dict:
    forecasts = forecasts or demand_forecast(facts)
    forecast_by_brand = defaultdict(float)
    for item in forecasts:
        forecast_by_brand[item["brand"]] += _number(item["expected_demand"])
    result = {}
    for row in facts:
        brand = _row_brand(row)
        bucket = result.setdefault(brand, {"sales": 0.0, "margin": 0.0, "inventory": 0.0, "turnover": 0.0, "forecast": 0, "risk": "normal", "ai_recommendation": "keep monitoring"})
        bucket["sales"] += _number(row.get("sales_amount_30d"))
        bucket["margin"] += _number(row.get("gross_margin_30d"))
        bucket["inventory"] += _number(row.get("inventory_qty")) * _number(row.get("unit_cost"))
    for brand, bucket in result.items():
        bucket["forecast"] = _ceil(forecast_by_brand[brand])
        bucket["turnover"] = round(bucket["sales"] / bucket["inventory"], 2) if bucket["inventory"] else 0
        bucket["risk"] = "shortage" if bucket["forecast"] > bucket["turnover"] * 30 and bucket["turnover"] > 0 else "overstock" if bucket["turnover"] < 0.2 and bucket["inventory"] > 0 else "normal"
        bucket["ai_recommendation"] = "increase order" if bucket["risk"] == "shortage" else "transfer or promotion" if bucket["risk"] == "overstock" else "keep monitoring"
    for brand in SUPPORTED_BRANDS:
        result.setdefault(brand, {"sales": 0.0, "margin": 0.0, "inventory": 0.0, "turnover": 0.0, "forecast": 0, "risk": "normal", "ai_recommendation": "no current Core facts"})
    return result


def supplier_alerts(facts: list[dict], context: SupplyChainContext | None = None) -> list[dict]:
    allowed_brands = set(context.brand_scope) if context and "supplier" in context.roles else None
    alerts = []
    for plan in purchase_planning(facts):
        if allowed_brands is not None and plan["brand"] not in allowed_brands:
            continue
        days = max(1, _ceil(_number(plan.get("supplier_lead_time_days")) / 2))
        alerts.append({"brand": plan["brand"], "product": plan["product"], "alert": f"Expected shortage in {days} days", "recommendation": "Prepare replenishment", "replenishment_request": plan, "source": AI_SOURCE})
    return alerts


def authorize_supply_chain(context: SupplyChainContext, permission: str, brand: str | None = None, store_code: str | None = None) -> dict:
    allowed = context.can(permission)
    reason = "permission granted" if allowed else f"missing permission: {permission}"
    if allowed and brand and "supplier" in context.roles:
        allowed = brand in context.brand_scope
        reason = "supplier own brand granted" if allowed else "supplier own brand only"
    if allowed and store_code and "store_manager" in context.roles:
        allowed = store_code in context.store_codes
        reason = "store scope granted" if allowed else "own store only"
    event = {"actor_id": context.user_id, "action": "permission_check", "permission": permission, "decision": "allowed" if allowed else "denied", "reason": reason, "occurred_at": _now_iso()}
    if not allowed:
        raise PermissionError(reason)
    return event


def supply_chain_agent_v2(question: str, facts: list[dict], context: SupplyChainContext) -> dict:
    authorize_supply_chain(context, "supply_chain.read")
    q = question.lower()
    if "purchase" in q or "order" in q:
        answer = purchase_planning(facts)[:10]
    elif "brand" in q and "risk" in q:
        answer = sorted(brand_intelligence(facts).items(), key=lambda item: item[1]["risk"] != "shortage")
    else:
        answer = {"forecast": demand_forecast(facts)[:5], "transfers": inventory_transfer_suggestions(facts)[:5]}
    return {"agent": "Supply Chain Agent V2", "question": question, "answer": answer, "based_on": ["Forecast", "Inventory", "Brand", "Season"], "source": AI_SOURCE}


def huyan_command_center(facts: list[dict], context: SupplyChainContext) -> dict:
    authorize_supply_chain(context, "huyan.supply_chain.read")
    forecasts = demand_forecast(facts)
    return {"view": "Supply Chain Command Center", "audience": "CEO", "demand_forecast": forecasts, "purchase_plan": purchase_planning(facts, forecasts), "inventory_risk": inventory_transfer_suggestions(facts, forecasts), "brand_health": brand_intelligence(facts, forecasts), "supplier_status": supplier_alerts(facts), "source": HUYAN_SOURCE}


def ai_task_workflow(facts: list[dict]) -> list[dict]:
    tasks = []
    for plan in purchase_planning(facts):
        tasks.append({"event": "AI detects shortage", "task": "Notify procurement", "supplier_collaboration": plan["brand"], "track_result": "pending", "learning": "capture approved quantity and actual demand", "payload": plan, "source": WORKFLOW_SOURCE})
    for transfer in inventory_transfer_suggestions(facts):
        tasks.append({"event": "AI detects store imbalance", "task": "Create transfer approval", "supplier_collaboration": None, "track_result": "pending", "learning": "capture transfer outcome", "payload": transfer, "source": WORKFLOW_SOURCE})
    return tasks
