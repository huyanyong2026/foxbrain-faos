"""Business Activation V2 store AI manager.

Deterministic AI Store Manager services for BA-V2.0-D.  The module consumes
existing Core/SAP-derived facts, composes store intelligence, creates
approval-ready execution tasks, and never mutates SAP logic or duplicates
business data.
"""

from __future__ import annotations

import math
import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone

BA_V2_STORE_VERSION = "BA-V2.0-D"
CORE_SOURCE = "core.vafox.com"
AI_SOURCE = "ai.vafox.com"
HUYAN_SOURCE = "huyan.vafox.com"
WECOM_SOURCE = "wecom.vafox.com"
WORKFLOW_SOURCE = "core.vafox.com/store-workflow"


@dataclass(frozen=True)
class StoreAIContext:
    user_id: str
    roles: tuple[str, ...]
    permissions: tuple[str, ...]
    store_codes: tuple[str, ...] = ()
    region_codes: tuple[str, ...] = ()

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


def _store_code(row: dict) -> str:
    return str(row.get("store_code") or row.get("store") or "")


def _store_name(row: dict) -> str:
    return str(row.get("store_name") or row.get("store") or _store_code(row))


def _product(row: dict) -> str:
    return str(row.get("product_name") or row.get("product") or row.get("sku") or "")


def _brand(row: dict) -> str:
    return str(row.get("brand") or row.get("brand_name") or "Other")


_CHUANXI_EQUIPMENT_ROLES = (
    ("shell", "防风防雨层", ("冲锋衣", "硬壳", "shell", "jacket")),
    ("hiking_boots", "徒步鞋", ("徒步鞋", "登山鞋", "hiking", "boot", "shoe")),
    ("backpack", "背包", ("背包", "backpack", "pack")),
)


def _catalog_sku(product: dict) -> str:
    return str(product.get("sku") or product.get("sku_code") or product.get("product_id") or "").strip()


def _catalog_name(product: dict) -> str:
    return str(product.get("product_name") or product.get("name") or "").strip()


def _available_inventory(inventory_domain: list[dict]) -> dict[str, dict]:
    """Return sellable inventory by SKU, keeping only a real inventory record."""
    records = {}
    for row in inventory_domain:
        sku = _catalog_sku(row)
        if not sku:
            continue
        available = _number(row.get("available_qty"))
        if "available_qty" not in row:
            available = _number(row.get("inventory_qty")) - _number(row.get("committed_qty"))
        existing = records.get(sku)
        if existing is None or available > existing["available_qty"]:
            records[sku] = {
                "available_qty": max(0, available),
                "store_code": row.get("store_code") or row.get("store") or "",
                "updated_at": row.get("updated_at") or row.get("update_time") or "",
                "source": row.get("source") or CORE_SOURCE,
            }
    return records


def _matches_equipment_role(product: dict, keywords: tuple[str, ...]) -> bool:
    text = " ".join(str(product.get(key) or "") for key in ("category", "category_name", "tags", "product_name", "name")).lower()
    return any(keyword.lower() in text for keyword in keywords)


def recommend_wecom_sales_equipment(
    customer_request: str,
    product_domain: list[dict],
    inventory_domain: list[dict],
    brand_knowledge: list[dict] | None = None,
) -> dict:
    """Build a grounded WeCom equipment recommendation from the three VAFOX domains.

    A recommendation is emitted only when its SKU exists in Product Domain and has
    a positive, matching sellable quantity in Inventory Domain.  This deliberately
    prevents the assistant from inventing products, prices, or stock positions.
    """
    request = str(customer_request or "").strip()
    normalized = request.lower()
    budget = 0.0
    for token in normalized.replace("￥", "¥").split():
        candidate = token.replace("¥", "").replace(",", "")
        if candidate.isdigit():
            budget = max(budget, float(candidate))
    # Support natural phrasing such as “预算10000” without requiring whitespace.
    match = re.search(r"(?:预算|¥|￥)\s*(\d+(?:\.\d+)?)", request)
    if match:
        budget = float(match.group(1))

    is_chuanxi = "川西" in request
    requested_brand = "KAILAS" if "kailas" in normalized or "凯乐石" in request else ""
    inventory = _available_inventory(inventory_domain)
    brand_rules = {str(item.get("brand") or item.get("brand_name") or "").upper(): item for item in (brand_knowledge or [])}
    roles = _CHUANXI_EQUIPMENT_ROLES if is_chuanxi else ()
    chosen, missing = [], []
    used_skus: set[str] = set()

    for role, label, keywords in roles:
        candidates = []
        for product in product_domain:
            sku, name = _catalog_sku(product), _catalog_name(product)
            stock = inventory.get(sku)
            if not sku or not name or sku in used_skus or not stock or stock["available_qty"] <= 0:
                continue
            if not _matches_equipment_role(product, keywords):
                continue
            price = _number(product.get("price") or product.get("retail_price"))
            brand = _brand(product)
            if requested_brand and brand.upper() != requested_brand:
                continue
            candidates.append((0 if brand.upper() == "KAILAS" else 1, price, sku, product, stock))
        if not candidates:
            missing.append(label)
            continue
        _, price, sku, product, stock = sorted(candidates, key=lambda item: item[:3])[0]
        if budget and sum(item["price"] for item in chosen) + price > budget:
            missing.append(f"{label}（超出预算）")
            continue
        used_skus.add(sku)
        chosen.append({
            "role": role,
            "role_label": label,
            "sku": sku,
            "product_name": _catalog_name(product),
            "brand": _brand(product),
            "price": round(price, 2),
            "inventory": stock,
            "brand_knowledge": brand_rules.get(_brand(product).upper(), {}),
        })

    total = round(sum(item["price"] for item in chosen), 2)
    no_match = not chosen
    reason = "未在 VAFOX 商品与库存数据中找到可售的匹配商品。" if no_match else ""
    scenario = "川西高海拔、多变天气的 7 天行程；优先防风防雨、稳定行走与负重能力。" if is_chuanxi else "未识别到可执行的户外场景，请补充目的地、天数和活动强度。"
    return {
        "channel": "WeCom AI",
        "customer_scenario_analysis": {"request": request, "analysis": scenario, "budget": budget or None},
        "recommended_equipment": chosen,
        "combination_amount": total,
        "current_inventory": [{"sku": item["sku"], **item["inventory"]} for item in chosen],
        "sales_advice": "先确认尺码、脚型与是否已有保暖层；库存紧张的 SKU 请先为客户锁定。" if chosen else "请勿以替代名称下单；补齐商品或库存数据后再推荐。",
        "cross_sell_opportunities": ["袜子、雨罩与保温水具可在试穿后连带推荐。"] if chosen else [],
        "missing_equipment": missing,
        "no_match": no_match,
        "no_match_reason": reason,
        "domains_consulted": ["Product Domain", "Inventory Domain", "Brand Knowledge"],
        "source": WECOM_SOURCE,
    }


def authorize_store_ai(context: StoreAIContext, permission: str, store_code: str | None = None, region_code: str | None = None) -> dict:
    allowed = context.can(permission)
    reason = "permission granted" if allowed else f"missing permission: {permission}"
    if allowed and "ceo" in context.roles:
        reason = "CEO all-store scope granted"
    elif allowed and store_code and ("store_manager" in context.roles or "employee" in context.roles):
        allowed = store_code in context.store_codes
        reason = "own store granted" if allowed else "own store only"
    elif allowed and region_code and "regional_manager" in context.roles:
        allowed = region_code in context.region_codes
        reason = "assigned region granted" if allowed else "assigned region only"
    event = {"actor_id": context.user_id, "action": "store_ai_permission_check", "permission": permission, "resource_store": store_code, "decision": "allowed" if allowed else "denied", "reason": reason, "occurred_at": _now_iso(), "source": AI_SOURCE}
    if not allowed:
        raise PermissionError(reason)
    return event


def _visible_facts(facts: list[dict], context: StoreAIContext) -> list[dict]:
    if "ceo" in context.roles or context.can("*"):
        return facts
    if context.store_codes:
        return [row for row in facts if _store_code(row) in context.store_codes]
    return []


def sales_intelligence(facts: list[dict], store_code: str) -> dict:
    rows = [row for row in facts if _store_code(row) == store_code]
    sales = sum(_number(row.get("sales_amount_30d")) for row in rows)
    previous_units = sum(_number(row.get("sales_prev_30d")) for row in rows)
    current_units = sum(_number(row.get("sales_30d")) for row in rows)
    brand_sales = defaultdict(float)
    product_trends = []
    for row in rows:
        brand_sales[_brand(row)] += _number(row.get("sales_amount_30d"))
        previous = _number(row.get("sales_prev_30d"))
        current = _number(row.get("sales_30d"))
        growth = current - previous
        if growth > 0:
            product_trends.append({"product": _product(row), "brand": _brand(row), "growth_units": growth, "recommendation": "increase exposure", "source": CORE_SOURCE})
    top_brand = max(brand_sales.items(), key=lambda item: item[1])[0] if brand_sales else "N/A"
    opportunity = product_trends[0] if product_trends else {"product": top_brand, "recommendation": "maintain core product display", "source": CORE_SOURCE}
    return {"store_code": store_code, "sales_amount_30d": round(sales, 2), "unit_trend": round(current_units - previous_units, 2), "top_brand": top_brand, "product_trends": sorted(product_trends, key=lambda item: -item["growth_units"]), "sales_opportunity": opportunity, "source": AI_SOURCE}


def inventory_assistant(facts: list[dict], store_code: str) -> dict:
    alerts = []
    for row in [item for item in facts if _store_code(item) == store_code]:
        stock = _number(row.get("inventory_qty")) + _number(row.get("incoming_qty"))
        sales = _number(row.get("sales_30d"))
        daily = sales / 30 if sales > 0 else 0
        stock_days = 999 if daily == 0 else stock / daily
        if stock_days < 10:
            alerts.append({"type": "low_stock", "product": _product(row), "brand": _brand(row), "risk": "inventory low", "recommendation": "request transfer or replenishment", "priority": "high", "source": CORE_SOURCE})
        elif _number(row.get("aging_days")) >= 180 or (stock > 8 and sales <= 1):
            alerts.append({"type": "slow_inventory", "product": _product(row), "brand": _brand(row), "risk": "slow inventory", "recommendation": "transfer, promote, or improve display", "priority": "normal", "source": CORE_SOURCE})
    return {"store_code": store_code, "alerts": alerts, "source": AI_SOURCE}


def store_health_score(facts: list[dict], store_code: str) -> dict:
    rows = [row for row in facts if _store_code(row) == store_code]
    if not rows:
        return {"store_code": store_code, "store": store_code, "health": 0, "details": {"sales": 0, "inventory": 0, "product": 0, "execution": 0, "customer_experience": 0}, "source": AI_SOURCE}
    sales = sales_intelligence(facts, store_code)
    inventory = inventory_assistant(facts, store_code)
    tasks = [row for row in rows if row.get("task_status")]
    completed = sum(1 for row in tasks if str(row.get("task_status")).lower() == "done")
    sales_score = max(0, min(100, 88 + sales["unit_trend"] * 2))
    inventory_score = max(0, 100 - len(inventory["alerts"]) * 7)
    product_score = max(0, min(100, 82 + len(sales["product_trends"]) * 4))
    execution_score = round((completed / len(tasks)) * 100, 1) if tasks else 91
    cx_score = max(0, min(100, 90 + sum(_number(row.get("customer_satisfaction_delta")) for row in rows)))
    details = {"sales": round(sales_score, 1), "inventory": round(inventory_score, 1), "product": round(product_score, 1), "execution": execution_score, "customer_experience": round(cx_score, 1)}
    health = round(sum(details.values()) / len(details))
    return {"store_code": store_code, "store": _store_name(rows[0]), "health": health, "details": details, "source": AI_SOURCE}


def store_daily_briefing(facts: list[dict], store_code: str) -> dict:
    health = store_health_score(facts, store_code)
    sales = sales_intelligence(facts, store_code)
    inventory = inventory_assistant(facts, store_code)
    risk = inventory["alerts"][0] if inventory["alerts"] else {"risk": "normal", "recommendation": "continue monitoring"}
    opportunity = sales["sales_opportunity"]
    actions = [risk.get("recommendation", "check inventory"), opportunity.get("recommendation", "improve display")]
    return {"store_code": store_code, "store_status": "Good" if health["health"] >= 85 else "Attention", "sales_summary": sales, "inventory_risk": risk, "opportunity": opportunity, "todays_actions": actions, "health": health, "source": AI_SOURCE}


def ai_task_center_for_store(facts: list[dict], store_code: str, owner: str = "store_manager") -> list[dict]:
    tasks = []
    for alert in inventory_assistant(facts, store_code)["alerts"]:
        tasks.append({"task": f"Resolve {alert['type']} for {alert['product']}", "owner": owner, "priority": alert["priority"], "deadline": "today" if alert["priority"] == "high" else "this_week", "status": "pending", "trigger": alert["risk"], "source": WORKFLOW_SOURCE})
    opportunity = sales_intelligence(facts, store_code)["sales_opportunity"]
    if opportunity.get("product"):
        tasks.append({"task": f"Improve display and recommendation for {opportunity['product']}", "owner": owner, "priority": "normal", "deadline": "today", "status": "pending", "trigger": "sales opportunity", "source": WORKFLOW_SOURCE})
    return tasks


def visual_merchandising_ai(photo_metadata: dict, store_code: str) -> dict:
    brand = photo_metadata.get("brand") or "KAILAS"
    missing = photo_metadata.get("missing_products") or []
    recommendation = "Improve front display position" if photo_metadata.get("front_exposure_score", 0) < 80 else "Maintain display and verify product completeness"
    return {"store_code": store_code, "photo_id": photo_metadata.get("photo_id"), "display_analysis": "foundation_ready", "brand_exposure_analysis": {brand: photo_metadata.get("front_exposure_score", 0)}, "missing_product_detection": missing, "display_recommendation": recommendation, "source": AI_SOURCE}


def store_ai_assistant_v2(question: str, facts: list[dict], context: StoreAIContext, store_code: str) -> dict:
    authorize_store_ai(context, "store_ai.read", store_code=store_code)
    q = question.lower()
    if "recommend" in q or "推荐" in question or "商品" in question:
        answer = sales_intelligence(facts, store_code)["sales_opportunity"]
        agents = ["Store Agent", "Commerce Agent", "Supply Agent"]
    elif "inventory" in q or "库存" in question:
        answer = inventory_assistant(facts, store_code)
        agents = ["Store Agent", "Supply Agent"]
    else:
        answer = store_daily_briefing(facts, store_code)
        agents = ["Store Agent", "Supply Agent", "Commerce Agent"]
    return {"question": question, "answer": answer, "auto_selected_agents": agents, "manual_agent_selection": False, "source": AI_SOURCE}


def store_employee_ai_assistant(question: str, facts: list[dict], context: StoreAIContext, store_code: str) -> dict:
    authorize_store_ai(context, "store_employee_ai.read", store_code=store_code)
    return {"channel": "WeCom AI", "question": question, "answer": {"product_knowledge": "Use Core product and brand facts", "usage_scenario": "match customer activity, weather, and terrain", "sales_suggestion": sales_intelligence(facts, store_code)["sales_opportunity"]}, "source": WECOM_SOURCE}


def ceo_store_intelligence_overview(facts: list[dict], context: StoreAIContext) -> dict:
    authorize_store_ai(context, "huyan.store_ai.read")
    stores = sorted({_store_code(row) for row in _visible_facts(facts, context) if _store_code(row)})
    health = [store_health_score(facts, store) for store in stores]
    briefings = [store_daily_briefing(facts, store) for store in stores]
    return {"view": "Store Intelligence Overview", "all_stores_health_score": health, "top_risks": [b["inventory_risk"] for b in briefings if b["inventory_risk"].get("risk") != "normal"][:5], "top_opportunities": [b["opportunity"] for b in briefings][:5], "ai_recommendations": [action for b in briefings for action in b["todays_actions"]][:10], "source": HUYAN_SOURCE}


def agent_collaboration_flow(event: str, facts: list[dict], store_code: str) -> dict:
    return {"event": event, "flow": ["Store Agent", "Commerce Agent", "Supply Agent", "Customer Agent", "Growth Agent"], "purchase_recommendation": inventory_assistant(facts, store_code)["alerts"][:3], "source": AI_SOURCE}
