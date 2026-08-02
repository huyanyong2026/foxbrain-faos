"""Read-only CEO data validation rules for VAFOX V6.1.10.1.

The rules operate on copies of Mirror/Data Core records. This module contains
no SAP writer, migration, or Data Core schema definition.
"""
from __future__ import annotations

from collections import Counter
from datetime import date, datetime

ACTIVE_STORES = {"hangyuan": "航苑店", "nanshan": "南山店", "zhenxing": "振兴店", "jinsha": "金沙店", "online": "网店"}
STORE_ALIASES = {**{code: code for code in ACTIVE_STORES}, **{name: code for code, name in ACTIVE_STORES.items()}, "成都金沙店": "jinsha"}
VALID_ACTIVITY_FROM = date(2026, 1, 1)


def store_code(value):
    """Return an active operating-unit code; historical stores return None."""
    text = str(value or "").strip()
    return STORE_ALIASES.get(text.lower()) or STORE_ALIASES.get(text)


def _on_or_after_2026(value):
    if not value:
        return False
    if isinstance(value, datetime):
        value = value.date()
    if isinstance(value, date):
        return value >= VALID_ACTIVITY_FROM
    try:
        return date.fromisoformat(str(value)[:10]) >= VALID_ACTIVITY_FROM
    except ValueError:
        return False


def classify_inventory(record):
    quantity = float(record.get("inventory", record.get("quantity", 0)) or 0)
    active = quantity > 0 or _on_or_after_2026(record.get("last_sale_date")) or _on_or_after_2026(record.get("last_purchase_date"))
    return "ACTIVE_SKU" if active else "HISTORY_SKU"


def filter_inventory(records):
    """Apply the five-store boundary and effective-inventory rule."""
    effective, history = [], []
    for source in records:
        record = dict(source)
        code = store_code(record.get("store_code") or record.get("store"))
        if not code:
            continue
        record.update(store_code=code, store_name=ACTIVE_STORES[code], classification=classify_inventory(record))
        (effective if record["classification"] == "ACTIVE_SKU" else history).append(record)
    return {"effective": effective, "history": history}


def build_consistency_report(layer_counts):
    """Compare SAP→Mirror→Data Core→CEO API→Dashboard aggregate counts."""
    layers = ("sap_b1", "mirror", "data_core", "ceo_api", "dashboard")
    domains = ("sales", "inventory", "stores", "customers")
    checks = {}
    for domain in domains:
        values = [int(layer_counts.get(layer, {}).get(domain, 0)) for layer in layers]
        checks[domain] = {"counts": dict(zip(layers, values)), "consistent": len(set(values)) == 1}
    return {"chain": list(layers), "checks": checks, "status": "trusted" if all(item["consistent"] for item in checks.values()) else "mismatch"}


def top_brands(sales, limit=3):
    totals = Counter()
    for row in sales:
        if store_code(row.get("store_code") or row.get("store")):
            totals[str(row.get("brand") or "未分类")] += float(row.get("amount", 0) or 0)
    return [{"brand": brand, "sales": amount} for brand, amount in totals.most_common(limit)]
