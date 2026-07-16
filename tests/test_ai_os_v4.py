from datetime import date

from foxbrain_os.ai_os_v4 import (
    build_ai_answer,
    build_ai_os_v4_contract,
    create_ai_task,
    route_identity,
    route_intent,
)


def test_gateway_identity_routing_is_automatic():
    assert route_identity("CEO")["destination"] == "huyan.vafox.com"
    assert route_identity("Procurement")["experience"] == "Supply Intelligence"
    assert route_identity("unknown")["experience"] == "AI Workspace"


def test_ai_router_selects_agents_without_user_configuration():
    nanshan = route_intent("Nanshan store problem?")
    assert nanshan["requires_user_configuration"] is False
    assert nanshan["agents"] == ["Store Agent", "Supply Agent"]
    profit = route_intent("Why profit decreased?")
    assert "Finance Agent" in profit["agents"]
    assert "Commerce Agent" in profit["agents"]
    inventory = route_intent("Future inventory risk?")
    assert "Supply Agent" in inventory["agents"]
    assert "Forecast Engine" in inventory["agents"]


def test_answer_contract_contains_required_sections_and_sources():
    answer = build_ai_answer("Which brand has growth opportunity?")
    for key in ("conclusion", "reason", "data_source", "recommendation", "next_action"):
        assert key in answer
    assert answer["route"]["business_objects"] == ["Brand"]


def test_task_generation_requires_human_approval():
    task = create_ai_task("Future inventory risk?", owner="procurement", today=date(2026, 7, 16))
    assert task["status"] == "pending_human_approval"
    assert task["approval_required"] is True
    assert task["deadline"] == "2026-07-18"


def test_v4_contract_preserves_sap_truth_and_acceptance():
    contract = build_ai_os_v4_contract()
    assert contract["guardrails"]["sap_role"] == "Business Truth Layer"
    assert contract["guardrails"]["sap_business_logic_modified"] is False
    assert all(value == "PASS" for value in contract["acceptance"].values())
