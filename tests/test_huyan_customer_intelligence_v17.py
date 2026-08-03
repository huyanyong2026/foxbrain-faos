from services.business.aggregation import customer_intelligence


def test_customer_intelligence_uses_customer360_facts_and_opportunity_contract():
    result = customer_intelligence(
        {"data_source": "Customer360 API", "updated_at": "2026-08-03T00:00:00Z", "customers": [
            {"customer_id": "C1", "customer_name": "授权客户甲", "status": "active", "value_segment": "VIP", "total_spend": 1200, "order_count": 3, "brand_preferences": ["KAILAS"], "category_preferences": [{"category": "鞋"}], "purchase_cycle": "45天", "purchase_trend": "上升"},
            {"customer_id": "C2", "customer_name": "授权客户乙", "value_segment": "流失风险", "total_spend": 300, "order_count": 1},
        ]},
        {"customer_opportunities": [{"customer_id": "C1", "customer": "授权客户甲", "type": "cross_sell", "reason": "Customer360原因", "evidence": "Customer360依据", "action": "人工确认", "owner": "负责人甲"}]},
    )
    assert result["overview"] == {"customer_count": 2, "active_customers": 1, "consumption_amount": 1500.0, "order_count": 4, "average_consumption": 375.0, "vip_count": 1}
    assert [row["name"] for row in result["value_segments"]] == ["VIP", "高价值", "成长", "正常", "流失风险"]
    assert result["purchase_behavior"]["brand_preferences"][0]["preference"] == "KAILAS"
    assert result["customer_opportunities"][0]["opportunity_type"] == "交叉销售"
    assert result["wecom"] == {"interface_reserved": True, "delivery_enabled": False}


def test_customer_intelligence_does_not_invent_unknown_opportunities():
    result = customer_intelligence({"customers": []}, {"customer_opportunities": [{"customer_id": "C1", "type": "unsupported"}]})
    assert result["customer_opportunities"] == []
