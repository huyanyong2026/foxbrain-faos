import unittest
from pathlib import Path

from apps.ai.identity import (
    IDENTITY_SCHEMA_STATEMENTS,
    ROLE_DEFINITIONS,
    allows,
    authorize_ai_context,
    build_identity_context,
    permissions_for_roles,
)


ROOT = Path(__file__).resolve().parents[1]
AI_ROOT = ROOT / "apps" / "ai"


class FireFoxIdentityCenterTest(unittest.TestCase):
    def test_identity_schema_covers_people_org_rbac_and_audit(self):
        schema = "\n".join(IDENTITY_SCHEMA_STATEMENTS)
        for table in (
            "identity_org_units", "identity_positions", "identity_profiles", "identity_roles",
            "identity_permissions", "identity_role_permissions", "identity_user_roles",
            "identity_data_scopes", "identity_login_audit", "identity_permission_audit",
            "identity_wecom_sso_states",
        ):
            self.assertIn(table, schema)

    def test_required_business_roles_are_explicit(self):
        self.assertTrue({"ceo", "management", "store_manager", "purchaser", "employee"}.issubset(ROLE_DEFINITIONS))
        self.assertTrue(all(ROLE_DEFINITIONS[key]["permissions"] for key in ROLE_DEFINITIONS))

    def test_ceo_has_all_permissions(self):
        permissions = permissions_for_roles(["ceo"])
        self.assertTrue(allows(permissions, "vault.read"))
        self.assertTrue(allows(permissions, "identity.manage"))

    def test_store_manager_ai_is_limited_to_own_store(self):
        identity = build_identity_context(8, "张店长", "E008", ["store_manager"], store_id=3)
        context = authorize_ai_context(identity, "inventory")
        self.assertEqual(context["effective_store_id"], "3")
        with self.assertRaisesRegex(PermissionError, "本人负责的门店"):
            authorize_ai_context(identity, "inventory", requested_store_id=9)

    def test_employee_cannot_use_inventory_agent(self):
        identity = build_identity_context(9, "李员工", "E009", ["employee"], store_id=3)
        with self.assertRaisesRegex(PermissionError, "没有使用"):
            authorize_ai_context(identity, "inventory")
        self.assertEqual(authorize_ai_context(identity, "content")["core_access"], "read_only")

    def test_purchaser_can_analyze_inventory_but_not_company_management(self):
        permissions = permissions_for_roles(["purchaser"])
        self.assertTrue(allows(permissions, "inventory.read"))
        self.assertFalse(allows(permissions, "business.read"))

    def test_app_has_identity_admin_login_audit_and_wecom_contract(self):
        source = (AI_ROOT / "app.py").read_text(encoding="utf-8")
        for marker in (
            "/identity", "/ops-api/identity/users", "record_login_audit",
            "/auth/wecom/status", "/auth/wecom/start", "/auth/wecom/callback",
            "authorize_ai_context", "must_change_password",
        ):
            self.assertIn(marker, source)
        self.assertNotIn("47.107.117.131", source)

    def test_user_pages_are_chinese_and_require_real_identity(self):
        login = (AI_ROOT / "templates" / "login.html").read_text(encoding="utf-8")
        identity = (AI_ROOT / "templates" / "identity.html").read_text(encoding="utf-8")
        self.assertIn("姓名、员工编号或手机号", login)
        self.assertIn("真实姓名", identity)
        self.assertIn("禁止共用账号", identity)
        self.assertNotIn("API路径", identity)


if __name__ == "__main__":
    unittest.main()
