"""Read-only transformations for Huyan's business analysis contracts."""
from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime, timezone

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


def organization_analysis(members_payload, sales_payload):
    """Aggregate only explicitly attributed Core sales; never estimate contribution."""
    members = _rows(members_payload, "members", "employees", "rows", "data", "items")
    sales = _rows(sales_payload, "sales", "rows", "data", "items")
    directory = {}
    for row in members:
        if not isinstance(row, dict): continue
        employee_id = str(row.get("employee_id") or row.get("member_id") or row.get("id") or "").strip()
        if employee_id: directory[employee_id] = row
    facts = defaultdict(lambda: {"sales": 0.0, "orders": set(), "products": set(), "customers": set(), "dates": defaultdict(float)})
    pending_sales, pending_orders, all_orders = 0.0, set(), set()
    for index, row in enumerate(sales):
        if not isinstance(row, dict): continue
        employee_id = str(row.get("employee_id") or row.get("member_id") or "").strip()
        amount = _number(row.get("sales_amount", row.get("amount", row.get("sales"))))
        order = str(row.get("order_id") or row.get("document_id") or f"row:{index}"); all_orders.add(order)
        if not employee_id or employee_id not in directory:
            pending_sales += amount; pending_orders.add(order); continue
        fact = facts[employee_id]; fact["sales"] += amount; fact["orders"].add(order)
        product = str(row.get("sku") or row.get("sku_code") or row.get("product_id") or "").strip()
        customer = str(row.get("customer_id") or row.get("card_code") or "").strip()
        day = str(row.get("date") or row.get("document_date") or "")[:10]
        if product: fact["products"].add(product)
        if customer: fact["customers"].add(customer)
        if day: fact["dates"][day] += amount
    employee_rows = []
    for employee_id, row in directory.items():
        fact = facts[employee_id]; order_count = len(fact["orders"])
        store_code = str(row.get("store_code") or row.get("department_code") or "").strip().lower()
        store_name = row.get("store_name") or STORE_NAMES.get(store_code)
        series = [{"date": day, "value": round(value, 2)} for day, value in sorted(fact["dates"].items())]
        employee_rows.append({"employee_id": employee_id, "employee": row.get("display_name") or row.get("name") or "待补齐", "store_code": store_code or None,
            "store_name": store_name or "销售归属待补齐。", "attribution_status": "complete" if store_name else "pending", "sales_amount": round(fact["sales"], 2),
            "order_count": order_count, "average_order_value": round(fact["sales"] / order_count, 2) if order_count else 0, "trend_series": series,
            "capability": {"sales": {"sales_amount": round(fact["sales"], 2), "order_count": order_count}, "product": {"distinct_products": len(fact["products"])}, "customer": {"distinct_customers": len(fact["customers"])}}})
    teams = []
    for code, name in STORE_NAMES.items():
        team = [item for item in employee_rows if item["store_code"] == code]; team_sales = round(sum(item["sales_amount"] for item in team), 2); daily = defaultdict(float)
        for item in team:
            for point in item["trend_series"]: daily[point["date"]] += point["value"]
        teams.append({"store_code": code, "team": name, "employee_count": len(team), "team_sales": team_sales, "sales_per_employee": round(team_sales / len(team), 2) if team else None, "trend_series": [{"date": day, "value": round(value, 2)} for day, value in sorted(daily.items())]})
    attributed_sales = round(sum(item["sales_amount"] for item in employee_rows), 2); active = sum(item["order_count"] > 0 for item in employee_rows)
    advice = {"conclusion": "员工销售归属仍有待补齐记录。" if pending_orders else "当前销售记录均已关联员工。", "evidence": [f"已归属销售 {attributed_sales:.2f}，待归属销售 {pending_sales:.2f}。", f"有销售员工 {active}/{len(employee_rows)}。"], "recommendation": ["优先补齐销售单据的员工与门店归属。"] if pending_orders else ["持续维护员工与销售单据的稳定标识关联。"]}
    return {**_meta(members_payload, sales_payload), "overview": {"employee_count": len(employee_rows), "selling_employee_count": active, "sales_coverage_rate": round((len(all_orders) - len(pending_orders)) / len(all_orders), 4) if all_orders else 0, "order_count": len(all_orders), "attributed_sales": attributed_sales, "pending_order_count": len(pending_orders), "pending_sales": round(pending_sales, 2)}, "employees": employee_rows, "teams": teams, "growth_advice": advice, "attribution_policy": {"missing_label": "销售归属待补齐。", "average_allocation": False, "estimated_contribution": False}}


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


def customer_intelligence(customer360_payload, opportunities_payload):
    """Normalize live Customer360 rows without synthesizing customers or opportunities."""
    customers = _rows(customer360_payload, "customers", "profiles", "rows", "data", "items")
    opportunities = _rows(opportunities_payload, "customer_opportunities", "opportunities", "rows", "data", "items")
    segment_names = ("VIP", "高价值", "成长", "正常", "流失风险")
    type_names = {"repurchase": "复购", "repeat_purchase": "复购", "复购": "复购", "upgrade": "升级", "升级": "升级", "recall": "召回", "win_back": "召回", "召回": "召回", "cross_sell": "交叉销售", "交叉销售": "交叉销售"}
    segments = {name: [] for name in segment_names}
    brand_preferences, category_preferences, cycles, trends = [], [], [], []
    customer_ids, active, vip, total_spend, order_count = set(), set(), set(), 0.0, 0
    for row in customers:
        if not isinstance(row, dict): continue
        customer_id = str(row.get("customer_id") or row.get("id") or row.get("card_code") or "").strip()
        if not customer_id: continue
        customer_ids.add(customer_id)
        name = row.get("customer_name") or row.get("display_name") or row.get("name") or "授权客户"
        amount = _number(row.get("consumption_amount", row.get("total_spend"))); orders = int(_number(row.get("order_count", row.get("purchase_count"))))
        total_spend += amount; order_count += orders
        if row.get("active") is True or str(row.get("status", "")).lower() == "active": active.add(customer_id)
        segment = str(row.get("value_segment") or row.get("segment") or "").strip()
        if segment in segments:
            segments[segment].append({"customer_id": customer_id, "customer_name": name, "consumption_amount": amount, "order_count": orders})
            if segment == "VIP": vip.add(customer_id)
        for source, target, keys in (("brand_preferences", brand_preferences, ("brand", "name")), ("category_preferences", category_preferences, ("category", "name"))):
            values = row.get(source)
            if isinstance(values, list):
                for value in values:
                    label = next((value.get(key) for key in keys if isinstance(value, dict) and value.get(key)), None) if isinstance(value, dict) else value
                    if label: target.append({"customer_id": customer_id, "customer_name": name, "preference": str(label)})
        if row.get("purchase_cycle") is not None: cycles.append({"customer_id": customer_id, "customer_name": name, "purchase_cycle": row["purchase_cycle"]})
        if row.get("purchase_trend") is not None: trends.append({"customer_id": customer_id, "customer_name": name, "purchase_trend": row["purchase_trend"]})
    normalized = []
    for row in opportunities:
        if not isinstance(row, dict): continue
        opportunity_type = type_names.get(str(row.get("opportunity_type") or row.get("type") or "").strip()); customer_id = str(row.get("customer_id") or "").strip()
        if not opportunity_type or not customer_id: continue
        normalized.append({"customer_id": customer_id, "customer": row.get("customer") or row.get("customer_name") or "授权客户", "opportunity_type": opportunity_type, "reason": row.get("reason"), "evidence": row.get("evidence"), "recommended_action": row.get("recommended_action") or row.get("action"), "owner": row.get("owner") or row.get("assignee")})
    summary = customer360_payload.get("summary", {}) if isinstance(customer360_payload, dict) else {}
    value = lambda key, fallback: _number(summary[key]) if key in summary else fallback
    return {**_meta(customer360_payload, opportunities_payload), "overview": {"customer_count": int(value("customer_count", len(customer_ids))), "active_customers": int(value("active_customers", len(active))), "consumption_amount": value("consumption_amount", round(total_spend, 2)), "order_count": int(value("order_count", order_count)), "average_consumption": value("average_consumption", round(total_spend / order_count, 2) if order_count else 0), "vip_count": int(value("vip_count", len(vip)))}, "value_segments": [{"name": name, "count": len(segments[name]), "customers": segments[name]} for name in segment_names], "purchase_behavior": {"brand_preferences": brand_preferences, "category_preferences": category_preferences, "purchase_cycles": cycles, "purchase_trends": trends}, "customer_opportunities": normalized, "wecom": {"interface_reserved": True, "delivery_enabled": False}, "read_only": True}


def supplier_analysis(payload):
    allowed = ("supplier_id", "supplier_code", "supplier_name", "name", "purchase_amount", "purchase_count", "delivery_status", "inventory_status")
    items = [{key: row[key] for key in allowed if key in row} for row in _rows(payload, "suppliers", "rows", "data", "items") if isinstance(row, dict)]
    return {**_meta(payload), "domain": "supply_chain", "summary": {"supplier_count": len(items)}, "suppliers": items}


def product_analysis(products_payload, sales_payload, inventory_payload):
    """Aggregate the product view from live Core rows without local fallbacks."""
    products = _rows(products_payload, "products", "rows", "data", "items")
    sales = _rows(sales_payload, "sales", "rows", "data", "items")
    inventory = _rows(inventory_payload, "inventory", "rows", "data", "items")
    catalog = {}
    for row in products:
        if not isinstance(row, dict): continue
        sku = str(row.get("sku") or row.get("sku_code") or row.get("product_id") or row.get("id") or "").strip()
        if sku: catalog[sku] = row
    sold, previous, stock, stock_value = defaultdict(float), defaultdict(float), defaultdict(float), defaultdict(float)
    cost_trusted = bool(inventory)
    for row in sales:
        if not isinstance(row, dict): continue
        sku = str(row.get("sku") or row.get("sku_code") or row.get("product_id") or "").strip()
        amount = _number(row.get("sales_amount", row.get("amount", row.get("sales"))))
        target = previous if str(row.get("period") or row.get("trend_period") or "current").lower() in {"previous", "prior", "last_period"} else sold
        target[sku] += amount
    for row in inventory:
        if not isinstance(row, dict): continue
        sku = str(row.get("sku") or row.get("sku_code") or row.get("product_id") or "").strip()
        quantity = _number(row.get("quantity", row.get("on_hand", row.get("inventory_qty"))))
        stock[sku] += quantity
        value, cost = row.get("inventory_amount", row.get("stock_amount")), row.get("unit_cost", row.get("cost"))
        if isinstance(value, (int, float)) and not isinstance(value, bool): stock_value[sku] += float(value)
        elif isinstance(cost, (int, float)) and not isinstance(cost, bool) and cost >= 0: stock_value[sku] += quantity * float(cost)
        else: cost_trusted = False
    sku_rows = []
    for sku in sorted(set(catalog) | set(sold) | set(stock)):
        item, current, prior = catalog.get(sku, {}), sold[sku], previous[sku]
        risk = "缺货风险" if current > 0 and stock[sku] <= 0 else "滞销风险" if current <= 0 and stock[sku] > 0 else "正常"
        sku_rows.append({"sku": sku, "product_name": item.get("product_name") or item.get("name") or sku,
                         "brand_name": item.get("brand_name") or item.get("brand") or "待补齐", "category_name": item.get("category_name") or item.get("category") or "待补齐",
                         "sales_amount": round(current, 2), "inventory_quantity": round(stock[sku], 2), "movement_status": "动销" if current > 0 else "未动销",
                         "risk_status": risk, "trend": round((current - prior) / prior * 100, 2) if prior else None})
    total_sales, brands, categories = sum(sold.values()), {}, {}
    for item in sku_rows:
        brand = brands.setdefault(item["brand_name"], {"brand_name": item["brand_name"], "sales_amount": 0.0, "sku_count": 0, "inventory_amount": 0.0, "moving": 0})
        brand["sales_amount"] += item["sales_amount"]; brand["sku_count"] += 1; brand["inventory_amount"] += stock_value[item["sku"]]; brand["moving"] += item["movement_status"] == "动销"
        category = categories.setdefault(item["category_name"], {"category_name": item["category_name"], "sales_amount": 0.0, "inventory_quantity": 0.0, "previous": 0.0})
        category["sales_amount"] += item["sales_amount"]; category["inventory_quantity"] += item["inventory_quantity"]; category["previous"] += previous[item["sku"]]
    brand_rows = [{**{key: value for key, value in row.items() if key != "moving"}, "sales_share": round(row["sales_amount"] / total_sales, 4) if total_sales else 0, "movement_status": "动销" if row["moving"] else "未动销"} for row in brands.values()]
    category_rows = [{"category_name": row["category_name"], "sales_amount": round(row["sales_amount"], 2), "sales_share": round(row["sales_amount"] / total_sales, 4) if total_sales else 0,
                      "trend": round((row["sales_amount"] - row["previous"]) / row["previous"] * 100, 2) if row["previous"] else None, "inventory_quantity": round(row["inventory_quantity"], 2)} for row in categories.values()]
    risks = [row for row in sku_rows if row["risk_status"] != "正常"]
    advice = [{"conclusion": row["risk_status"], "evidence": f'{row["product_name"]}：销售 {row["sales_amount"]}，库存 {row["inventory_quantity"]}，趋势 {row["trend"] if row["trend"] is not None else "待补齐"}',
               "recommendation": "核实补货与到货节奏" if row["risk_status"] == "缺货风险" else "暂停追加并制定去化方案"} for row in risks]
    return {**_meta(products_payload, sales_payload, inventory_payload), "cost_status": "trusted" if cost_trusted else "governing", "cost_message": None if cost_trusted else "成本数据治理中。",
            "brands": brand_rows, "categories": category_rows, "skus": {"hot": sorted(sku_rows, key=lambda row: row["sales_amount"], reverse=True), "risk": risks, "items": sku_rows}, "procurement_recommendations": advice}


def inventory_analysis(products_payload, sales_payload, inventory_payload):
    """Build V1.6 inventory intelligence exclusively from current Core rows."""
    products = _rows(products_payload, "products", "rows", "data", "items")
    sales = _rows(sales_payload, "sales", "rows", "data", "items")
    inventory = _rows(inventory_payload, "inventory", "rows", "data", "items")
    catalog = {}
    for row in products:
        if not isinstance(row, dict): continue
        sku = str(row.get("sku") or row.get("sku_code") or row.get("product_id") or row.get("id") or "").strip()
        if sku: catalog[sku] = row
    sold, previous, last_sale = defaultdict(float), defaultdict(float), {}
    for row in sales:
        if not isinstance(row, dict): continue
        sku = str(row.get("sku") or row.get("sku_code") or row.get("product_id") or "").strip()
        if not sku: continue
        quantity = _number(row.get("quantity", row.get("units", row.get("sales_quantity"))))
        target = previous if str(row.get("period") or row.get("trend_period") or "current").lower() in {"previous", "prior", "last_period"} else sold
        target[sku] += quantity
        raw_date = str(row.get("date") or row.get("document_date") or row.get("sale_date") or "")[:10]
        if raw_date and raw_date > last_sale.get(sku, ""): last_sale[sku] = raw_date
    stock, values, stores_by_sku = defaultdict(float), defaultdict(float), defaultdict(lambda: defaultdict(float))
    cost_trusted = bool(inventory)
    for row in inventory:
        if not isinstance(row, dict): continue
        sku = str(row.get("sku") or row.get("sku_code") or row.get("product_id") or "").strip()
        if not sku: continue
        quantity = _number(row.get("quantity", row.get("on_hand", row.get("inventory_qty"))))
        stock[sku] += quantity
        store = str(row.get("store_name") or row.get("store_code") or row.get("store") or "待补齐")
        stores_by_sku[sku][store] += quantity
        amount, cost = row.get("inventory_amount", row.get("stock_amount")), row.get("unit_cost", row.get("cost"))
        if isinstance(amount, (int, float)) and not isinstance(amount, bool): values[sku] += float(amount)
        elif isinstance(cost, (int, float)) and not isinstance(cost, bool) and cost >= 0: values[sku] += quantity * float(cost)
        else: cost_trusted = False
    source_meta = _meta(products_payload, sales_payload, inventory_payload)
    try: as_of = date.fromisoformat(str(source_meta["updated_at"])[:10])
    except ValueError: as_of = datetime.now(timezone.utc).date()
    effective = []
    for sku in sorted(set(catalog) | set(stock) | set(sold)):
        item, quantity = catalog.get(sku, {}), stock[sku]
        marker = " ".join(str(item.get(key, "")) for key in ("status", "sku_status", "label", "tags")).upper()
        if "HISTORY SKU" in marker or "HISTORY_SKU" in marker: continue
        if quantity <= 0 and (not last_sale.get(sku) or last_sale[sku] < "2026-01-01"): continue
        recent, prior = sold[sku], previous[sku]
        coverage = quantity / recent * 30 if recent > 0 else None
        if quantity <= 0 and recent > 0: health, risk, advice = "缺货风险", "高", "核实在途与安全库存，人工确认补货。"
        elif quantity > 0 and recent <= 0: health, risk, advice = "滞销库存", "高", "暂停追加，制定调拨、陈列或去化方案。"
        elif coverage is not None and coverage > 90: health, risk, advice = "高库存", "中", "控制采购并复核销售节奏。"
        else: health, risk, advice = "正常库存", "低", "保持监控，按销售速度滚动复核。"
        age = (as_of - date.fromisoformat(last_sale[sku])).days if last_sale.get(sku) else None
        effective.append({"sku": sku, "product_name": item.get("product_name") or item.get("name") or sku, "brand_name": item.get("brand_name") or item.get("brand") or "待补齐", "inventory_amount": round(values[sku], 2), "inventory_quantity": round(quantity, 2), "last_sale_date": last_sale.get(sku), "inventory_age_days": age, "health_status": health, "risk_level": risk, "recommendation": advice, "sales_velocity": round(recent, 2), "trend": round((recent - prior) / prior * 100, 2) if prior else None})
    total_quantity = sum(row["inventory_quantity"] for row in effective)
    brand_quantity, store_quantity = defaultdict(float), defaultdict(float)
    effective_skus = {row["sku"] for row in effective}
    for row in effective: brand_quantity[row["brand_name"]] += row["inventory_quantity"]
    for sku in effective_skus:
        for store, quantity in stores_by_sku[sku].items(): store_quantity[store] += quantity
    def structure(values):
        return [{"name": name, "quantity": round(quantity, 2), "share": round(quantity / total_quantity, 4) if total_quantity else 0} for name, quantity in sorted(values.items(), key=lambda pair: pair[1], reverse=True)]
    slow = sorted((row for row in effective if row["health_status"] == "滞销库存"), key=lambda row: row["inventory_amount"], reverse=True)
    recommendations = [{"conclusion": row["health_status"], "evidence": f'{row["product_name"]}：销售速度 {row["sales_velocity"]}，库存 {row["inventory_quantity"]}，趋势 {row["trend"] if row["trend"] is not None else "待补齐"}', "recommendation": row["recommendation"]} for row in effective if row["health_status"] != "正常库存"]
    return {**source_meta, "scope": {"dataset": "effective_skus", "excluded": ["HISTORY SKU", "2026年前零库存无经营商品"]}, "cost_status": "trusted" if cost_trusted else "governing", "cost_message": None if cost_trusted else "成本数据治理中", "overview": {"inventory_amount": round(sum(row["inventory_amount"] for row in effective), 2), "effective_skus": len(effective), "inventory_quantity": round(total_quantity, 2), "brand_structure": structure(brand_quantity), "store_structure": structure(store_quantity)}, "health": {name: [row for row in effective if row["health_status"] == name] for name in ("正常库存", "高库存", "滞销库存", "缺货风险")}, "items": effective, "slow_moving": slow, "replenishment_recommendations": recommendations}
