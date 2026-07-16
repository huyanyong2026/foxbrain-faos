import unittest
from pathlib import Path

from apps.ai.identity import ROLE_DEFINITIONS, build_identity_context, allows, permissions_for_roles
from apps.ai.domain import DIGITAL_WORKFORCE_AGENTS, DEFAULT_APPROVAL_POLICY, SCHEMA_STATEMENTS
from foxbrain_os.foundation_v2 import (
    acceptance_matrix,
    ai_workforce_contract,
    core_digital_twin_contract,
    devops_release_contract,
    foundation_v2_contract,
    gateway_policy_contract,
    huyan_ceo_os_contract,
)

ROOT = Path(__file__).resolve().parents[1]


class FoundationV2Test(unittest.TestCase):
    def test_gateway_contract_covers_identity_rbac_abac_and_health_router(self):
        contract = gateway_policy_contract()
        self.assertEqual(contract["domain"], "gateway.vafox.com")
        for role in ("CEO", "Employee", "Store Manager", "Procurement", "Supplier", "Customer"):
            self.assertIn(role, contract["identity_roles"])
        self.assertIn("rate_limiting", contract["api_gateway"])
        self.assertEqual(contract["health_router"], ["huyan.vafox.com", "ai.vafox.com", "core.vafox.com"])

    def test_huyan_contract_is_ceo_os_not_business_redesign(self):
        contract = huyan_ceo_os_contract()
        self.assertIn("Gross Margin", contract["command_center"])
        self.assertEqual(contract["daily_briefing"], ["What happened", "Why happened", "Recommended actions"])
        self.assertIn("Operation risk", contract["risk_radar"])

    def test_ai_contract_has_registry_workspace_knowledge_memory_and_no_sap_write(self):
        contract = ai_workforce_contract()
        agent_names = {agent["name"] for agent in contract["agent_registry"]}
        self.assertTrue({"CEO Agent", "Supply Chain Agent", "Store Agent", "Customer Agent", "Supplier Agent"}.issubset(agent_names))
        self.assertIn("Report generation", contract["workspace"])
        self.assertIn("Historical decisions", contract["memory_system"])
        self.assertEqual(contract["sap_write_policy"], "forbidden")

    def test_core_contract_has_master_data_events_business_api_and_governance(self):
        contract = core_digital_twin_contract()
        self.assertEqual(contract["domain"], "core.vafox.com")
        for model in ("Product", "Brand", "Store", "Supplier", "Customer", "Employee", "Event"):
            self.assertIn(model, contract["master_data_models"])
        for event in ("Sales", "Inventory", "Purchase", "Customer", "Task", "Approval"):
            self.assertIn(event, contract["event_engine"])
        self.assertIn("data_source_tracking", contract["data_governance"])

    def test_security_roles_include_supplier_customer_and_abac_scopes(self):
        self.assertTrue({"supplier", "customer"}.issubset(ROLE_DEFINITIONS))
        supplier_permissions = permissions_for_roles(["supplier"])
        self.assertTrue(allows(supplier_permissions, "brand.own.read"))
        supplier_identity = build_identity_context(21, "供应商", "S001", ["supplier"])
        self.assertEqual(supplier_identity["data_scopes"][0]["type"], "brand")
        customer_permissions = permissions_for_roles(["customer"])
        self.assertTrue(allows(customer_permissions, "customer.own.read"))

    def test_digital_workforce_and_memory_schema_are_declared_without_breaking_legacy_agents(self):
        self.assertEqual(len(DIGITAL_WORKFORCE_AGENTS), 5)
        self.assertIn("memory_promotion", DEFAULT_APPROVAL_POLICY)
        self.assertIn("ai_memory_items", "\n".join(SCHEMA_STATEMENTS))

    def test_devops_release_and_acceptance_matrix_cover_required_gates(self):
        release = devops_release_contract()
        self.assertEqual(release["pipeline"], ["Codex Cloud", "GitHub", "Automated Test", "Build", "Deploy", "Health Check", "Release"])
        self.assertIn("Rollback plan", release["pre_deploy_gates"])
        matrix = acceptance_matrix()
        self.assertIn("Permission", matrix["Gateway"])
        self.assertIn("Memory", matrix["AI"])
        self.assertIn("Business API", matrix["Core"])

    def test_required_v2_documentation_exists(self):
        for name in (
            "FOXBrain_ARCHITECTURE_V2.md",
            "FOXBrain_API_V2.md",
            "FOXBrain_SECURITY_V2.md",
            "FOXBrain_DEPLOYMENT_V2.md",
            "FOXBrain_OPERATION_V2.md",
            "FOXBrain_HEALTHCHECK_V2.md",
            "FOXBrain_RELEASE_V2.md",
        ):
            content = (ROOT / name).read_text(encoding="utf-8")
            self.assertIn("VAFOX", content)

    def test_full_contract_preserves_sap_guardrails(self):
        contract = foundation_v2_contract()
        self.assertEqual(contract["version"], "2.0")
        self.assertIn("SAP remains the business truth layer.", contract["sap_guardrails"])
        self.assertIn("SAP B1", contract["architecture"])


if __name__ == "__main__":
    unittest.main()
