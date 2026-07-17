from apps.ai.ceo_strategy import build_ceo_strategy_snapshot


def test_ceo_strategy_snapshot_covers_ba_v2_0_b_modules():
    snapshot = build_ceo_strategy_snapshot(
        {"pending_runs": 1, "pending_tasks": 1},
        latest_batch={"status": "completed"},
        replenishment_summary=[{"urgent_skus": 3, "suggested_units": 120}],
        approved_runs=2,
        memories=4,
    )

    assert snapshot["enterprise_health_score"] > 0
    assert set(snapshot["dimensions"]) == {"Sales", "Margin", "Inventory", "Supply Chain", "Store Performance", "Customer"}
    assert {item["area"] for item in snapshot["briefing"]["what_happened"]} == set(snapshot["dimensions"])
    assert snapshot["briefing"]["why_happened"]
    assert all({"priority", "action", "expected_impact"}.issubset(item) for item in snapshot["briefing"]["what_should_do_next"])
    assert all({"risk", "level", "probability", "reason", "recommendation"}.issubset(item) for item in snapshot["risks"])
    assert all({"opportunity", "reason", "recommended_action"}.issubset(item) for item in snapshot["opportunities"])
    assert {"problem", "analysis", "options", "recommendation", "expected_result"}.issubset(snapshot["decision_center"])
    assert {"sales", "margin", "inventory", "risk", "roi"}.issubset(snapshot["simulation"]["expected"])
    assert snapshot["memory"]["records"] == 4
    assert {"Supply Agent", "Finance Agent", "Store Agent", "Growth Agent"}.issubset(snapshot["agents"])
