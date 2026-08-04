"""V1.9 read-only supply-chain aggregation over governed Core contracts."""
from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime, timezone

SYNCING_MESSAGE = "供应链数据同步中"


def _rows(payload, *keys):
    if isinstance(payload, list):
        return payload
    if not isinstance(payload, dict):
        return []
    return next((payload[key] for key in keys if isinstance(payload.get(key), list)), [])


def _status(payload):
    if not isinstance(payload, dict):
        return "unavailable"
    return str(payload.get("status") or payload.get("data_status") or payload.get("completeness") or "").lower()


def _source(payload, name):
    return {"name": name, "status": _status(payload), "updated_at": payload.get("updated_at") if isinstance(payload, dict) else None}


def _number(value):
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ValueError("invalid numeric field")
    return float(value)


def _ratio(numerator, denominator):
    return round(numerator / denominator, 4) if denominator else None


def syncing_payload(suppliers=None, purchases=None, inventory=None, query=None, request_id=None):
    sources = [_source(payload, name) for payload, name in ((suppliers, "supplier_master"), (purchases, "purchase"), (inventory, "inventory")) if payload is not None]
    return {"version": "1.9", "read_only": True, "domain": "supply_chain", "query": query or {},
            "data_status": {"status": "syncing", "message": SYNCING_MESSAGE, "sources": sources,
                            "limitations": ["purchase_data_unavailable_or_incomplete"]},
            "overview": None, "supplier_performance": [], "brand_supply_relationships": [],
            "procurement_collaboration": [], "risks": [], "ai_advice": {"status": "unavailable", "items": []},
            "trace": {"request_id": request_id, "generated_at": datetime.now(timezone.utc).isoformat(),
                      "source_names": ["Supplier Master", "采购数据", "库存关联数据"]}}


def supply_chain_intelligence(supplier_payload, purchase_payload, inventory_payload, query, request_id=None):
    """Aggregate only explicit supplier, purchase and inventory identifiers."""
    suppliers = _rows(supplier_payload, "suppliers", "supplier_master", "rows", "data", "items")
    purchases = _rows(purchase_payload, "purchases", "purchase_lines", "rows", "data", "items")
    inventory = _rows(inventory_payload, "inventory", "rows", "data", "items")
    complete = {"ready", "complete"}
    if _status(purchase_payload) not in complete or _status(supplier_payload) not in complete:
        return syncing_payload(supplier_payload, purchase_payload, inventory_payload, query, request_id)

    directory = {}
    for row in suppliers:
        if not isinstance(row, dict) or any(row.get(key) in (None, "") for key in ("supplier_id", "supplier_name", "supplier_status", "updated_at")):
            return syncing_payload(supplier_payload, purchase_payload, inventory_payload, query, request_id)
        directory[str(row["supplier_id"])] = row

    required = ("purchase_document_id", "purchase_line_id", "supplier_id", "sku_id", "order_date",
                "ordered_quantity", "document_status", "updated_at")
    seen_lines, valid = set(), []
    for row in purchases:
        if not isinstance(row, dict) or any(row.get(key) in (None, "") for key in required):
            return syncing_payload(supplier_payload, purchase_payload, inventory_payload, query, request_id)
        line_id = str(row["purchase_line_id"])
        if line_id in seen_lines:
            continue
        seen_lines.add(line_id)
        if str(row["supplier_id"]) not in directory:
            return syncing_payload(supplier_payload, purchase_payload, inventory_payload, query, request_id)
        day = str(row["order_date"])[:10]
        if not query["date_from"] <= day <= query["date_to"]: continue
        if query.get("supplier_id") and str(row["supplier_id"]) != query["supplier_id"]: continue
        if query.get("brand_id") and str(row.get("brand_id") or "") != query["brand_id"]: continue
        _number(row["ordered_quantity"])
        valid.append(row)

    inventory_by_sku, inventory_brand = defaultdict(float), {}
    for row in inventory:
        if not isinstance(row, dict) or row.get("sku_id") in (None, "") or row.get("on_hand_quantity") is None: continue
        if query.get("location_id") and str(row.get("location_id") or "") != query["location_id"]: continue
        sku = str(row["sku_id"]); inventory_by_sku[sku] += _number(row["on_hand_quantity"])
        if row.get("brand_id") not in (None, ""): inventory_brand[sku] = str(row["brand_id"])

    amount_complete = all(row.get("ordered_amount") is not None for row in valid)
    receipt_complete = all(row.get("received_quantity") is not None for row in valid)
    delivery_rows = [row for row in valid if row.get("expected_delivery_date") and row.get("received_date")]
    supplier_facts = defaultdict(list); brand_facts = defaultdict(list)
    unmatched_inventory = unmatched_brand = 0
    for row in valid:
        supplier_facts[str(row["supplier_id"])].append(row)
        sku = str(row["sku_id"]); brand = str(row.get("brand_id") or inventory_brand.get(sku) or "")
        if sku not in inventory_by_sku: unmatched_inventory += 1
        if brand: brand_facts[brand].append(row)
        else: unmatched_brand += 1

    def metrics(rows):
        ordered = sum(_number(row["ordered_quantity"]) for row in rows)
        received = sum(_number(row["received_quantity"]) for row in rows) if all(row.get("received_quantity") is not None for row in rows) else None
        amounts = sum(_number(row["ordered_amount"]) for row in rows) if all(row.get("ordered_amount") is not None for row in rows) else None
        timed = [row for row in rows if row.get("expected_delivery_date") and row.get("received_date")]
        return ordered, received, amounts, _ratio(received, ordered) if received is not None else None, \
            _ratio(sum(str(row["received_date"])[:10] <= str(row["expected_delivery_date"])[:10] for row in timed), len(timed)), \
            sum(max(_number(row["ordered_quantity"]) - _number(row["received_quantity"]), 0) for row in rows) if all(row.get("received_quantity") is not None for row in rows) else None

    supplier_output = []
    for supplier_id, rows in supplier_facts.items():
        ordered, received, amount, receipt_rate, on_time, opened = metrics(rows); master = directory[supplier_id]
        supplier_output.append({"supplier_id": supplier_id, "supplier_name": master["supplier_name"], "supplier_status": master["supplier_status"],
            "purchase_order_count": len({str(row["purchase_document_id"]) for row in rows}), "purchase_quantity": ordered,
            "purchase_amount": amount, "received_quantity": received, "receipt_rate": receipt_rate, "on_time_rate": on_time,
            "open_quantity": opened, "brand_count": len({str(row.get("brand_id")) for row in rows if row.get("brand_id")}),
            "last_purchase_date": max(str(row["order_date"])[:10] for row in rows), "limitations": []})

    brand_output = []
    for brand_id, rows in brand_facts.items():
        supplier_ids = sorted({str(row["supplier_id"]) for row in rows}); ordered, _, amount, _, _, _ = metrics(rows)
        skus = {str(row["sku_id"]) for row in rows}
        brand_name = next((row.get("brand_name") for row in rows if row.get("brand_name")), None)
        limitations = [] if brand_name else ["brand_name_unavailable"]
        brand_output.append({"brand_id": brand_id, "brand_name": brand_name, "supplier_count": len(supplier_ids),
            "suppliers": [{"supplier_id": item, "supplier_name": directory[item]["supplier_name"]} for item in supplier_ids],
            "purchase_quantity": ordered, "purchase_amount": amount, "inventory_quantity": sum(inventory_by_sku[sku] for sku in skus),
            "last_purchase_date": max(str(row["order_date"])[:10] for row in rows), "limitations": limitations})

    collaboration, risks = [], []
    today = date.today().isoformat()
    for row in valid:
        supplier_id, sku = str(row["supplier_id"]), str(row["sku_id"]); brand_id = str(row.get("brand_id") or inventory_brand.get(sku) or "") or None
        received = _number(row["received_quantity"]) if row.get("received_quantity") is not None else None
        opened = max(_number(row["ordered_quantity"]) - received, 0) if received is not None else None
        collaboration.append({"purchase_document_ref": str(row["purchase_document_id"]), "supplier_id": supplier_id,
            "supplier_name": directory[supplier_id]["supplier_name"], "brand_id": brand_id, "brand_name": row.get("brand_name"), "sku_id": sku,
            "order_date": str(row["order_date"])[:10], "expected_delivery_date": row.get("expected_delivery_date"), "received_date": row.get("received_date"),
            "ordered_quantity": _number(row["ordered_quantity"]), "received_quantity": received, "open_quantity": opened,
            "document_status": row["document_status"], "inventory_quantity": inventory_by_sku.get(sku), "limitations": []})
        risk_type = None
        if row.get("received_date") and row.get("expected_delivery_date") and str(row["received_date"])[:10] > str(row["expected_delivery_date"])[:10]: risk_type = "late_delivery"
        elif row.get("expected_delivery_date") and str(row["expected_delivery_date"])[:10] < today and opened and str(row["document_status"]).lower() not in {"closed", "cancelled", "canceled"}: risk_type = "overdue_delivery"
        if risk_type:
            risks.append({"risk_id": f'{risk_type}:{row["purchase_line_id"]}', "risk_type": risk_type, "supplier_id": supplier_id,
                "brand_id": brand_id, "sku_id": sku, "purchase_document_ref": str(row["purchase_document_id"]),
                "conclusion": "采购交付日期事实需要人工复核", "evidence": [{"expected_delivery_date": row.get("expected_delivery_date"), "received_date": row.get("received_date"), "open_quantity": opened}],
                "source_names": ["purchase"], "limitations": []})

    ordered, received, amount, receipt_rate, on_time, opened = metrics(valid)
    limitations = []
    if not amount_complete: limitations.append("purchase_amount_incomplete")
    if not receipt_complete: limitations.append("received_quantity_incomplete")
    if valid and not delivery_rows: limitations.append("delivery_dates_incomplete")
    status = "partial" if limitations or unmatched_inventory or unmatched_brand else "ready"
    page, page_size = query["page"], query["page_size"]; total = len(collaboration); start = (page - 1) * page_size
    return {"version": "1.9", "read_only": True, "domain": "supply_chain", "query": {k: v for k, v in query.items() if k not in {"page", "page_size"}},
        "data_status": {"status": status, "message": None, "sources": [_source(supplier_payload, "supplier_master"), _source(purchase_payload, "purchase"), _source(inventory_payload, "inventory")], "limitations": limitations},
        "join_quality": {"status": "partial" if unmatched_inventory or unmatched_brand else "complete", "matched_purchase_lines": len(valid),
                         "unmatched_supplier_lines": 0, "unmatched_inventory_skus": unmatched_inventory, "unmatched_brand_lines": unmatched_brand},
        "overview": {"supplier_count": len(supplier_facts), "supplier_master_count": len(directory), "purchase_order_count": len({str(row["purchase_document_id"]) for row in valid}),
                     "purchase_line_count": len(valid), "purchase_quantity": ordered, "purchase_amount": amount, "received_quantity": received,
                     "receipt_rate": receipt_rate, "on_time_rate": on_time, "open_quantity": opened, "brand_count": len(brand_facts)},
        "supplier_performance": supplier_output, "brand_supply_relationships": brand_output,
        "procurement_collaboration": collaboration[start:start + page_size], "risks": risks,
        "ai_advice": {"status": "unavailable", "items": []}, "pagination": {"page": page, "page_size": page_size, "total_items": total},
        "trace": {"request_id": request_id, "generated_at": datetime.now(timezone.utc).isoformat(), "source_names": ["Supplier Master", "采购数据", "库存关联数据"]}}
