from datetime import date

from foxbrain_os.ai_os_v6 import (
    AI_OS_V6_VERSION,
    audit_links,
    build_ai_os_v6_contract,
    build_business_event_flow,
    build_ceo_today_center,
    build_core_digital_twin,
    create_ai_task,
    health_check_payload,
    release_guard,
    route_ai_question,
    route_identity,
)


def test_gateway_v6_routes_roles_without_manual_application_selection():
    assert route_identity("CEO")["destination"] == "huyan.vafox.com"
    assert route_identity("Procurement")["workspace"] == "Supply AI"
    assert route_identity("Store Manager")["workspace"] == "Store AI"
    assert route_identity("unknown")["destination"] == "ai.vafox.com"
    assert route_identity("Supplier")["manual_application_selection"] is False


def test_universal_ai_conversation_replaces_manual_analysis_controls():
    risk = route_ai_question("分析企业最大风险")
    assert risk["version"] == AI_OS_V6_VERSION
    assert "Risk Agent" in risk["selected_agents"]
    assert "Core Enterprise Digital Twin" in risk["core_data_sources"]
    assert risk["manual_agent_dropdown_removed"] is True
    assert risk["manual_source_selection_removed"] is True
    assert risk["manual_object_selection_removed"] is True
    assert risk["manual_analysis_form_removed"] is True

    store = route_ai_question("南山店经营如何？")
    assert "Store Agent" in store["selected_agents"]
    assert "Store" in store["business_objects"]

    inventory = route_ai_question("Osprey库存怎么办？")
    assert "Supply Agent" in inventory["selected_agents"]
    assert "Inventory" in inventory["business_objects"]


def test_ceo_center_core_twin_and_data_activity_flow_are_v6_ready():
    center = build_ceo_today_center()
    assert all(center.values())
    twin = build_core_digital_twin()
    assert twin["flow"] == ["SAP B1", "Core", "AI", "Decision", "Action", "Learning"]
    assert twin["memory_layer"] is True
    flow = build_business_event_flow("inventory_decrease")
    assert flow["steps"] == ["Core Event", "AI Analysis", "Supply Agent", "Recommendation", "Task", "Feedback", "Memory Learning"]


def test_release_guard_blocks_mixed_or_legacy_versions():
    assert release_guard()["deployment_allowed"] is True
    mixed = release_guard({"gateway.vafox.com": "AI OS V6", "ai.vafox.com": "AI-OS-V5.1"})
    assert mixed["deployment_allowed"] is False
    assert mixed["mixed_versions_detected"] is True
    assert mixed["legacy_versions_detected"] == ["AI-OS-V5.1"]


def test_links_health_tasks_and_acceptance_contract_pass():
    links = audit_links()
    assert links["status"] == "PASS"
    assert links["broken_links"] == []

    task = create_ai_task("Osprey库存怎么办？", owner="procurement", today=date(2026, 7, 16))
    assert task["task_id"] == "v6-inventory-20260716"
    assert task["status"] == "pending_human_approval"

    health = health_check_payload()
    assert health["status"] == "PASS"

    contract = build_ai_os_v6_contract()
    assert contract["version"] == "AI OS V6"
    assert contract["release_guard"]["deployment_allowed"] is True
    assert all(value == "PASS" for value in contract["acceptance"].values())
