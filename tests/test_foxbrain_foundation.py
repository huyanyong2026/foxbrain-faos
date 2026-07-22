import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from apps.foundation.app import (AI_EMPLOYEES, AUDIT_LOG, ROLE_PERMISSIONS, USERS, ai_query, core_read, identity_from_authorization, issue_token, login)
from apps.foundation.app import LoginRequest, QueryRequest


def token_for(username):
    user = USERS[username]
    return "Bearer " + issue_token({"user_id": user["id"], "roles": user["roles"], "data_scope": user["scope"]})


def test_canonical_roles_and_gateway_destinations():
    assert {"ceo", "manager", "store_manager", "employee", "buyer", "product_manager"} <= set(ROLE_PERMISSIONS)
    assert login(LoginRequest(username="ceo", password="change-me"))["redirect_to"] == "https://huyan.vafox.com"
    assert login(LoginRequest(username="employee", password="change-me"))["redirect_to"] == "https://ai.vafox.com"
    assert login(LoginRequest(username="system", password="change-me"))["redirect_to"] == "https://control.vafox.com"
    assert AI_EMPLOYEES["ai-inventory-analyst"]["roles"] == ["buyer"]


def test_runtime_response_has_context_citation_and_audit():
    AUDIT_LOG.clear()
    response = ai_query(QueryRequest(question="库存如何？", resource="product"), token_for("ceo"))
    assert response["identity_context"]["user_id"] == "usr-ceo"
    assert response["citations"][0]["mode"] == "read_only"
    assert response["audit_id"].startswith("audit_")


def test_core_is_read_only_and_token_context_is_signed():
    response = core_read("inventory", token_for("ceo"))
    assert response["mode"] == "read_only"
    assert identity_from_authorization(token_for("employee"))["roles"] == ["employee"]
