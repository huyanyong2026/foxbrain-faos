"""Read-only transformations for Huyan's business analysis contracts."""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone

STORE_NAMES = {"zhenxing": "振兴", "nanshan": "南山", "hangyuan": "航苑", "jinsha": "金沙", "online": "网店"}


def _number(value):
    return float(value) if isinstance(value, (int, float)) and not isinstance(value, bool) else 0.0


def _rows(payload, *keys):
    if isinstance(payload, list): return payload
    if not isinstance(payload, dict): return []
    return next((payload[key] for key in keys if isinstance(payload.get(key), list)), [])


def _meta(*payloads):
    source = next((item for item in payloads if isinstance(item, dict)), {})
    return {"data_source": source.get("data_source") or source.get("source") or "Data Core",
            "updated_at": source.get("updated_at") or source.get("timestamp") or datetime.now(timezone.utc).isoformat(),
            "freshness_status": source.get("freshness_status") or "source_reported", "read_only": True}


def sales_analysis(payload):
    rows = _rows(payload, "sales", "rows", "data", "items")
    by_store, by_date, all_orders = defaultdict(lambda: {"sales": 0.0, "orders": set()}), defaultdict(float), set()
    total = 0.0
    for index, row in enumerate(rows):
        if not isinstance(row, dict): continue
        amount = _number(row.get("sales_amount", row.get("amount", row.get("sales"))))
        order = str(row.get("order_id") or row.get("document_id") or f"row:{index}")
        store, date = str(row.get("store_code") or row.get("store") or "").strip().lower(), str(row.get("date") or row.get("document_date") or "")[:10]
        total += amount; all_orders.add(order)
        if store in STORE_NAMES: by_store[store]["sales"] += amount; by_store[store]["orders"].add(order)
        if date: by_date[date] += amount
    stores = [{"store_code": code, "store_name": name, "sales_amount": round(by_store[code]["sales"], 2), "order_count": len(by_store[code]["orders"]), "status": "complete" if code in by_store else "pending"} for code, name in STORE_NAMES.items()]
    return {**_meta(payload), "summary": {"sales_amount": round(total, 2), "order_count": len(all_orders), "average_order_value": round(total / len(all_orders), 2) if all_orders else 0}, "stores": stores, "trend_series": [{"date": date, "value": round(value, 2)} for date, value in sorted(by_date.items())]}


def member_analysis(members_payload, sales_payload):
    members, sales = _rows(members_payload, "members", "rows", "data", "items"), _rows(sales_payload, "sales", "rows", "data", "items")
    totals, orders = defaultdict(float), defaultdict(set)
    for index, row in enumerate(sales):
        if not isinstance(row, dict): continue
        member_id = str(row.get("member_id") or row.get("employee_id") or "").strip()
        if member_id:
            totals[member_id] += _number(row.get("sales_amount", row.get("amount", row.get("sales")))); orders[member_id].add(str(row.get("order_id") or f"row:{index}"))
    items, known = [], set()
    for row in members:
        if not isinstance(row, dict): continue
        member_id = str(row.get("member_id") or row.get("employee_id") or row.get("id") or "").strip()
        if not member_id: continue
        known.add(member_id); items.append({"member_id": member_id, "display_name": row.get("display_name") or row.get("name") or "待补齐", "store_name": row.get("store_name") or "待补齐", "sales_amount": round(totals[member_id], 2), "order_count": len(orders[member_id]), "completion_status": "complete" if member_id in totals else "pending_sales"})
    matched = sum(isinstance(row, dict) and str(row.get("member_id") or row.get("employee_id") or "").strip() in known for row in sales)
    return {**_meta(members_payload, sales_payload), "summary": {"sales_rows": len(sales), "covered_rows": matched, "coverage_rate": round(matched / len(sales), 4) if sales else 0, "pending_rows": len(sales) - matched}, "members": items}


def customer_analysis(customers_payload, sales_payload):
    customers, sales = _rows(customers_payload, "customers", "members", "rows", "data", "items"), _rows(sales_payload, "sales", "rows", "data", "items")
    spend, purchases = defaultdict(float), defaultdict(set)
    for index, row in enumerate(sales):
        if not isinstance(row, dict): continue
        customer_id = str(row.get("customer_id") or row.get("card_code") or "").strip()
        if customer_id: spend[customer_id] += _number(row.get("sales_amount", row.get("amount", row.get("sales")))); purchases[customer_id].add(str(row.get("order_id") or f"row:{index}"))
    ranked = sorted(spend.values()); high = ranked[max(0, int(len(ranked) * .75) - 1)] if ranked else 0; items = []
    for row in customers:
        if not isinstance(row, dict): continue
        customer_id = str(row.get("customer_id") or row.get("id") or row.get("card_code") or "").strip()
        if not customer_id: continue
        amount, count = round(spend[customer_id], 2), len(purchases[customer_id]); segment = "high_value" if amount and amount >= high else "growth" if count else "pending"
        items.append({"customer_id": customer_id, "customer_name": row.get("display_name") or row.get("name") or "授权客户", "consumption_amount": amount, "purchase_count": count, "value_segment": segment, "opportunity": "priority_retention" if segment == "high_value" else "repeat_purchase" if count else "profile_completion"})
    return {**_meta(customers_payload, sales_payload), "summary": {"customer_count": len(items), "consumption_amount": round(sum(item["consumption_amount"] for item in items), 2)}, "customers": items}


def supplier_analysis(payload):
    allowed = ("supplier_id", "supplier_code", "supplier_name", "name", "purchase_amount", "purchase_count", "delivery_status", "inventory_status")
    items = [{key: row[key] for key in allowed if key in row} for row in _rows(payload, "suppliers", "rows", "data", "items") if isinstance(row, dict)]
    return {**_meta(payload), "domain": "supply_chain", "summary": {"supplier_count": len(items)}, "suppliers": items}
