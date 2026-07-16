from datetime import date

from foxbrain_os.ai_os_v5 import (
    build_ai_os_v5_contract,
    build_ai_response,
    build_ceo_today_homepage,
    build_data_activity_flow,
    create_autonomous_task,
    link_cross_system_context,
    route_identity,
    route_intent,
    run_automation,
)


def test_gateway_identity_routing_is_automatic_v5():
    assert route_identity("CEO")["workspace"] == "CEO AI Command Center"
    assert route_identity("Procurement")["workspace"] == "Supply Intelligence Workspace"
    assert route_identity("unknown")["destination"] == "ai.vafox.com"
    assert route_identity("Supplier")["manual_system_selection_required"] is False


def test_ai_router_v5_selects_agents_data_and_objects_without_configuration():
    profit = route_intent("Why profit decreased?")
    assert profit["manual_agent_selection_required"] is False
    assert "Finance Agent" in profit["required_agents"]
    assert "Commerce Agent" in profit["required_agents"]

    inventory = route_intent("Inventory risk?")
    assert inventory["business_objects"] == ["Inventory"]
    assert "Supply Agent" in inventory["required_agents"]
    assert "Forecast Engine" in inventory["required_agents"]

    store = route_intent("Store problem?")
    assert "Store Agent" in store["required_agents"]
    assert "Customer Agent" in store["required_agents"]


def test_ai_response_standard_contains_required_sections():
    response = build_ai_response("Which brand has opportunity?")
    for section in ("conclusion", "reason", "data_source", "recommendation", "next_action"):
        assert section in response
    assert response["route"]["manual_data_mapping_required"] is False


def test_autonomous_task_generation_requires_human_approval():
    task = create_autonomous_task("Inventory risk?", owner="procurement", today=date(2026, 7, 16))
    assert task["task_id"] == "v5-inventory-20260716"
    assert task["owner"] == "procurement"
    assert task["priority"] == "high"
    assert task["status"] == "pending_human_approval"
    assert task["deadline"] == "2026-07-18"
    assert task["approval_required"] is True


def test_core_data_activity_and_cross_system_linking_preserve_truth_layers():
    flow = build_data_activity_flow("sales_change")
    assert flow["flow"] == ["SAP", "Core", "AI", "Decision", "Action"]
    assert flow["sap_truth_preserved"] is True

    linked = link_cross_system_context("Nanshan store")
    assert linked["linked_systems"] == ["Gateway", "Huyan", "AI", "Core"]
    assert linked["manual_user_mapping_required"] is False
    assert linked["truth_layer"] == "SAP"


def test_automation_converts_events_to_approval_ready_actions():
    automation = run_automation("inventory_change", owner="procurement", today=date(2026, 7, 16))
    assert automation["event_detected"] == "inventory_change"
    assert automation["task_creation"]["status"] == "pending_human_approval"
    assert automation["notification"]["status"] == "ready_for_approval"
    assert automation["learning"] == "memory_learning_after_feedback"


def test_ceo_homepage_and_contract_acceptance_pass():
    homepage = build_ceo_today_homepage()
    assert homepage["enterprise_health_score"] == 92
    assert "Review item 2" in homepage["recommended_actions"]

    contract = build_ai_os_v5_contract()
    assert contract["guardrails"]["sap_business_logic_modified"] is False
    assert contract["guardrails"]["duplicate_business_truth_created"] is False
    assert all(value == "PASS" for value in contract["acceptance"].values())
