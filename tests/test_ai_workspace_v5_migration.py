from pathlib import Path

from foxbrain_os.ai_os_v5 import build_ai_response, create_autonomous_task, link_cross_system_context, route_intent

ROOT = Path(__file__).resolve().parents[1]


def test_ai_router_v5_chinese_business_questions_auto_route():
    store = route_intent("南山店最近经营怎么样？")
    assert "Store Agent" in store["required_agents"]
    assert store["manual_agent_selection_required"] is False
    assert store["manual_data_mapping_required"] is False

    risk = route_intent("Osprey库存风险？")
    assert "Inventory" in risk["business_objects"]
    assert "Supply Agent" in risk["required_agents"]
    assert "Core Inventory Events" in risk["required_data"]


def test_response_task_data_link_standard():
    response = build_ai_response("为什么利润下降？")
    for section in ("conclusion", "reason", "data_source", "recommendation", "next_action"):
        assert section in response
    assert "Finance Agent" in response["route"]["required_agents"]

    task = create_autonomous_task("Osprey库存风险？")
    assert task["status"] == "pending_human_approval"
    assert task["approval_required"] is True

    link = link_cross_system_context("ai.vafox.com")
    assert link["manual_user_mapping_required"] is False
    assert link["linked_systems"] == ["Gateway", "Huyan", "AI", "Core"]


def test_workbench_template_has_no_legacy_manual_selection():
    html = (ROOT / "apps/ai/templates/workbench.html").read_text(encoding="utf-8")
    assert "FoxBrain AI Workforce V5" in html
    assert "data-ai-router-v5=\"enabled\"" in html
    for legacy in ("选择助手", "关联对象类型", "本次分析依据", "提交分析"):
        assert legacy not in html
