import pathlib


ROOT = pathlib.Path(__file__).resolve().parents[1]


def read(name):
    return (ROOT / name).read_text(encoding="utf-8")


def test_compose_core_services():
    text = read("docker-compose.yml")
    for service in ["foxbrain-web", "foxbrain-api", "foxbrain-worker", "postgres", "redis", "minio", "qdrant", "nginx"]:
        assert service in text
    assert text.count("restart: always") >= 8


def test_v6_worker_schedule_envs():
    env = read(".env.example")
    for key in ["SAP_SYNC_TIME", "KNOWLEDGE_INDEX_TIME", "BACKUP_TIME", "DAILY_REPORT_TIME", "WEB_RESEARCH_TIME", "WEEKLY_REPORT_TIME", "MONTHLY_REPORT_DAY"]:
        assert key in env


def test_v6_routes_present():
    portal = read("portal_v2.py")
    for route in ["/action/today", "/operating-loop", "/digital-twin", "/ai-memory", "/data-fabric", "/operations"]:
        assert route in portal


def test_enterprise_pack_routes_present():
    portal = read("portal_v2.py")
    for route in [
        "/api/dashboard/ceo",
        "/api/sap/sync/connector",
        "/api/agents/registry",
        "/api/knowledge/platform",
        "/api/knowledge/ingestion/status",
        "/api/knowledge/governance",
        "/api/knowledge/retrieval-contract",
        "/api/knowledge/graph-contract",
        "/api/agents/framework",
        "/api/agents/runtime-contract",
        "/api/agents/permissions",
        "/api/agents/tool-interface",
        "/api/agents/memory-contract",
        "/api/agents/approval-policy",
        "/api/agents/audit-contract",
        "/api/dashboard/service",
        "/api/dashboard/kpis",
        "/api/dashboard/alerts",
        "/api/dashboard/recommendations",
        "/api/dashboard/finance",
        "/api/dashboard/store",
        "/api/automation/framework",
        "/api/automation/scheduler",
        "/api/automation/retry-policy",
        "/api/automation/approval-policy",
        "/api/automation/notifications",
        "/api/automation/audit",
        "/api/automation/workflow-library",
        "/api/brain/framework",
        "/api/brain/memory",
        "/api/brain/decision-engine",
        "/api/brain/forecast",
        "/api/brain/simulation",
        "/api/brain/ai-council",
        "/api/brain/recommendation-contract",
        "/api/portal/framework",
        "/api/portal/sso",
        "/api/portal/navigation",
        "/api/portal/components",
        "/api/portal/messages",
        "/api/portal/tasks",
        "/api/portal/responsive",
        "/api/memory/framework",
        "/api/memory/repository",
        "/api/memory/governance",
        "/api/memory/timeline",
        "/api/memory/retrieval",
        "/api/memory/decision-history",
        "/api/memory/ai-contract",
        "/api/product/release-readiness",
        "/api/product/deployment-standard",
        "/api/product/observability",
        "/api/product/rollback",
        "/api/product/security-review",
        "/api/product/production-checklist",
        "/api/security/framework",
        "/api/security/identity-access",
        "/api/security/rbac",
        "/api/security/audit",
        "/api/security/audit-export",
        "/api/security/data-governance",
        "/api/security/backup-recovery",
        "/api/security/approval-governance",
        "/api/sdk/framework",
        "/api/sdk/manifest-schema",
        "/api/sdk/extension-points",
        "/api/sdk/versioning",
        "/api/sdk/backward-compatibility",
        "/api/extensions/contracts",
        "/api/extensions/registry",
        "/api/marketplace/apps",
        "/api/data-intelligence/framework",
        "/api/kpi/catalog",
        "/api/kpi/metrics",
        "/api/data-intelligence/model",
        "/api/data-quality/monitor",
        "/api/insights/engine",
        "/api/trends",
        "/api/digital-twin/framework",
        "/api/digital-twin/entities",
        "/api/digital-twin/relationships",
        "/api/digital-twin/state-history",
        "/api/digital-twin/simulation",
        "/api/digital-twin/visualization",
        "/api/decision-engine/framework",
        "/api/decision-engine/risk-scoring",
        "/api/decision-engine/opportunities",
        "/api/decision-engine/recommendations",
        "/api/decision-engine/approval-gate",
        "/api/strategy-center/framework",
        "/api/strategy-center/okr",
        "/api/strategy-center/models",
        "/api/strategy-center/scenario-comparison",
        "/api/strategy-center/expansion-analysis",
        "/api/strategy-center/brand-product-strategy",
        "/api/strategy-center/dashboard",
        "/api/university/framework",
        "/api/university/catalog",
        "/api/university/learning-paths",
        "/api/university/ai-tutor",
        "/api/university/certification",
        "/api/university/progress",
        "/api/university/knowledge-feedback",
        "/api/growth-engine/framework",
        "/api/growth-engine/scorecard",
        "/api/growth-engine/store-growth",
        "/api/growth-engine/brand-product",
        "/api/growth-engine/customer-growth",
        "/api/growth-engine/executive-scorecard",
        "/api/executive-command-center/framework",
        "/api/executive-command-center/dashboard",
        "/api/executive-command-center/risks",
        "/api/executive-command-center/ai-command",
        "/api/executive-command-center/system-health",
        "/api/executive-command-center/modules",
        "/api/executive-command-center/monitoring",
        "/api/product/release-1-0",
        "/api/product/release-1-0/modules",
        "/api/product/release-1-0/integration",
        "/api/product/architecture-review",
        "/api/security/baseline",
    ]:
        assert route in portal


def test_pack_knowledge_governance_schema_present():
    portal = read("portal_v2.py")
    for field in ["owner", "department", "version", "retention_policy", "deleted_at"]:
        assert f'"knowledge_items", "{field}"' in portal


def test_pack_agent_tool_governance_schema_present():
    portal = read("portal_v2.py")
    for field in ["tool_category", "tool_version", "risk_level", "approval_required", "audit_event"]:
        assert f'"agent_tools", "{field}"' in portal
    for phrase in ["Price Decision Draft", "Contract Review Draft", "Finance Action Draft", "high_risk_actions_blocked_until_approved"]:
        assert phrase in portal


def test_pack_dashboard_framework_present():
    portal = read("portal_v2.py")
    for phrase in [
        "dashboard_kpi_service_payload",
        "dashboard_alert_service_payload",
        "dashboard_recommendation_service_payload",
        "unified_dashboard_data_service",
        "business_recommendations_must_show_basis_for_manager_review",
        "ai_recommendations_and_alerts_are_independent_components_not_mixed_into_raw_business_data",
    ]:
        assert phrase in portal


def test_pack_automation_framework_present():
    portal = read("portal_v2.py")
    for field in ["risk_level", "approval_required", "approval_status", "retry_policy", "max_retries", "audit_status"]:
        assert f'"automations", "{field}"' in portal
    for field in ["attempt_no", "next_retry_at", "approval_id", "audit_event_id"]:
        assert f'"automation_runs", "{field}"' in portal
    for phrase in [
        "automation_framework_payload",
        "automation_scheduler_payload",
        "automation_retry_policy_payload",
        "automation_approval_policy_payload",
        "automation_is_high_risk",
        "high_risk_operations_are_never_auto_executed",
        "every_automation_run_and_retry_must_be_audited",
    ]:
        assert phrase in portal


def test_pack_enterprise_brain_present():
    portal = read("portal_v2.py")
    for field in ["evidence_json", "lineage_json", "permission_scope", "reviewed_by", "reviewed_at", "expansion_status"]:
        assert f'"memories", "{field}"' in portal
    for phrase in [
        "enterprise_brain_payload",
        "brain_memory_service_payload",
        "brain_decision_engine_payload",
        "brain_forecast_payload",
        "brain_simulation_payload",
        "brain_ai_council_payload",
        "all_ai_recommendations_must_cite_data_or_knowledge_basis",
        "no_basis_rule",
    ]:
        assert phrase in portal


def test_pack_mobile_portal_present():
    portal = read("portal_v2.py")
    for phrase in [
        "enterprise_portal",
        "portal_framework_payload",
        "portal_sso_payload",
        "portal_navigation_payload",
        "portal_message_center_payload",
        "portal_task_center_payload",
        "portal_component_contract_payload",
        "mobile_bottom_nav",
        "single_login_for_modules",
    ]:
        assert phrase in portal
    assert '"/portal"' in portal


def test_foxbrain_os_2_master_upgrade_docs_present():
    required = [
        "docs/200_FOXBRAIN_OS_2_0_MASTER_UPGRADE.md",
        "docs/201_FOXBRAIN_OS_2_0_AI_ORCHESTRATION.md",
        "docs/202_FOXBRAIN_OS_2_0_UNIFIED_DATA_SERVICE.md",
        "docs/203_FOXBRAIN_OS_2_0_ARCHITECTURE_REVIEW.md",
        "docs/CODEX_TASKS/Task066_FoxBrain_OS_2_0_Master_Upgrade.md",
    ]
    for name in required:
        assert (ROOT / name).exists()


def test_foxbrain_os_2_upgrade_rules_are_documented():
    master = read("docs/200_FOXBRAIN_OS_2_0_MASTER_UPGRADE.md")
    for phrase in [
        "compatibility-first",
        "must not delete existing capabilities",
        "Unified data service",
        "AI collaboration",
        "Production stability",
        "architecture review",
    ]:
        assert phrase in master


def test_foxbrain_os_3_ai_operations_present():
    portal = read("portal_v2.py")
    for phrase in [
        "ai_operation_plans",
        "ai_operation_feedback",
        "ai_operations_center",
        "ai_task_planner_payload",
        "approve_ai_operation_plan",
        "blocked_manual_required",
        "all_high_risk_operations_require_human_approval_and_must_not_auto_execute",
        "/ai-operations",
        "/ai-task-planner",
        "/api/ai-operations",
        "/api/ai-task-planner",
    ]:
        assert phrase in portal


def test_foxbrain_os_3_docs_present_and_safety_rule_documented():
    for doc in [
        "docs/300_FOXBRAIN_OS_3_0_AI_OPERATIONS_CENTER.md",
        "docs/301_FOXBRAIN_OS_3_0_APPROVAL_EXECUTION_FEEDBACK.md",
        "docs/CODEX_TASKS/Task067_FoxBrain_OS_3_0_AI_Operations.md",
    ]:
        assert (ROOT / doc).exists()
    safety = read("docs/301_FOXBRAIN_OS_3_0_APPROVAL_EXECUTION_FEEDBACK.md")
    for phrase in [
        "All high-risk operations must retain human approval and must not auto execute",
        "SAP write-back",
        "finance payment",
        "price changes",
        "external publishing",
    ]:
        assert phrase in safety


def test_foxbrain_os_4_digital_workforce_present():
    portal = read("portal_v2.py")
    for phrase in [
        "digital_workforce_performance",
        "digital_employee_id",
        "approval_rule",
        "audit_policy",
        "performance_policy",
        "digital_workforce_payload",
        "digital_workforce_center",
        "api_digital_workforce_get",
        "high_risk_operations_must_require_human_approval",
        "/digital-workforce",
        "/api/digital-workforce",
    ]:
        assert phrase in portal


def test_foxbrain_os_4_docs_present_and_governance_rule_documented():
    for doc in [
        "docs/400_FOXBRAIN_OS_4_0_ENTERPRISE_DIGITAL_WORKFORCE.md",
        "docs/401_FOXBRAIN_OS_4_0_DIGITAL_EMPLOYEE_GOVERNANCE.md",
        "docs/CODEX_TASKS/Task068_FoxBrain_OS_4_0_Digital_Workforce.md",
    ]:
        assert (ROOT / doc).exists()
    doc_text = read("docs/400_FOXBRAIN_OS_4_0_ENTERPRISE_DIGITAL_WORKFORCE.md")
    for phrase in [
        "Role",
        "Permissions",
        "Tool scope",
        "Approval rules",
        "Audit logs",
        "Performance evaluation",
        "High-risk operations must retain human approval and must not auto execute",
    ]:
        assert phrase in doc_text


def test_foxbrain_os_5_enterprise_digital_brain_present():
    portal = read("portal_v2.py")
    for phrase in [
        "enterprise_digital_brain_recommendations",
        "enterprise_digital_brain_payload",
        "digital_brain_evidence_packet",
        "digital_brain_recommendations_payload",
        "save_digital_brain_recommendation",
        "api_digital_brain_get",
        "sap_remains_core_business_data_source",
        "all_ai_recommendations_must_be_explainable",
        "all_ai_recommendations_must_be_traceable",
        "all_ai_recommendations_must_be_auditable",
        "high_risk_operations_require_human_approval",
        "/digital-brain",
        "/api/digital-brain",
    ]:
        assert phrase in portal


def test_foxbrain_os_5_docs_present_and_safety_rule_documented():
    for doc in [
        "docs/500_FOXBRAIN_OS_5_0_ENTERPRISE_DIGITAL_BRAIN.md",
        "docs/501_FOXBRAIN_OS_5_0_EXPLAINABLE_TRACEABLE_AUDITABLE_AI.md",
        "docs/CODEX_TASKS/Task069_FoxBrain_OS_5_0_Enterprise_Digital_Brain.md",
    ]:
        assert (ROOT / doc).exists()
    doc_text = read("docs/500_FOXBRAIN_OS_5_0_ENTERPRISE_DIGITAL_BRAIN.md")
    for phrase in [
        "SAP B1 remains the core business data source",
        "All AI recommendations must be explainable",
        "All AI recommendations must be traceable",
        "All AI recommendations must be auditable",
        "All high-risk operations require human approval",
        "enterprise_digital_brain_recommendations",
    ]:
        assert phrase in doc_text


def test_pack_enterprise_memory_present():
    portal = read("portal_v2.py")
    for field in ["owner", "tags", "access_level", "retention_policy", "version"]:
        assert f'"memories", "{field}"' in portal
    for phrase in [
        "enterprise_memory_repository_payload",
        "enterprise_memory_governance_payload",
        "enterprise_memory_timeline_payload",
        "enterprise_memory_retrieval_payload",
        "enterprise_decision_history_payload",
        "enterprise_memory_ai_contract_payload",
        "permission_filter_before_agent_context",
        "agent_answers_must_cite_memory_id_or_source",
    ]:
        assert phrase in portal


def test_pack_release_production_present():
    portal = read("portal_v2.py")
    for phrase in [
        "release_readiness_payload",
        "release_deployment_standard_payload",
        "release_observability_payload",
        "release_backup_restore_payload",
        "release_security_review_payload",
        "release_checklist_payload",
        "release_candidate_ready",
        "deployment_repeatability_status",
        "rollback_status",
    ]:
        assert phrase in portal


def test_pack_security_governance_present():
    portal = read("portal_v2.py")
    for phrase in [
        "security_governance_payload",
        "security_identity_access_payload",
        "security_rbac_payload",
        "security_audit_payload",
        "security_audit_export_payload",
        "security_data_governance_payload",
        "security_backup_recovery_payload",
        "security_approval_governance_payload",
        "security_baseline_payload",
        "all_ai_workflow_approval_and_system_config_changes_must_be_traceable",
        "high_risk_default",
        "Strict-Transport-Security",
        "Content-Security-Policy",
        "X-Content-Type-Options",
        "Permissions-Policy",
        "foxbrain_os_1_0_security_baseline",
    ]:
        assert phrase in portal


def test_pack_sdk_marketplace_present():
    portal = read("portal_v2.py")
    for phrase in [
        "sdk_platform_payload",
        "sdk_manifest_schema_payload",
        "sdk_extension_points_payload",
        "sdk_versioning_payload",
        "sdk_backward_compatibility_payload",
        "sdk_marketplace_payload",
        "sdk_plugin_registry_payload",
        "plugin_manifest",
        "extension_points",
        "semantic_versioning_required",
        "new_capabilities_prefer_plugins_before_core_changes",
        "existing_plugin_contracts_must_continue_to_work_across_minor_and_patch_releases",
        "manual_review_required_before_extension_can_modify_price_contract_finance_or_external_publish_data",
    ]:
        assert phrase in portal


def test_pack_data_intelligence_present():
    portal = read("portal_v2.py")
    for phrase in [
        "unified_kpi_catalog_payload",
        "unified_data_model_payload",
        "unified_metrics_service_payload",
        "data_quality_monitor_payload",
        "trend_api_payload",
        "insight_engine_payload",
        "data_intelligence_framework_payload",
        "all_dashboards_agents_and_decision_engines_must_use_this_kpi_catalog_to_avoid_duplicate_calculation",
        "dashboard_agent_and_decision_engine_kpis_must_come_from_unified_metrics_service",
        "all_ai_insights_must_reference_explicit_data_evidence",
        "quality_warnings_must_be_visible_before_ai_insights_are_trusted",
        "canonical_entities",
    ]:
        assert phrase in portal


def test_pack_digital_twin_present():
    portal = read("portal_v2.py")
    for phrase in [
        "digital_twin_entity_registry_payload",
        "digital_twin_relationship_service_payload",
        "digital_twin_state_engine_payload",
        "digital_twin_simulation_payload",
        "digital_twin_visualization_payload",
        "digital_twin_framework_payload",
        "digital_twin_get",
        "simulation_must_not_modify_production_data",
        "read_only_twin_and_sandboxed_simulations_never_modify_production_data",
        "relationships_should_be_queryable_versioned_and_traceable_to_source",
        "snapshots_are_append_only_and_never_overwrite_production_data",
        "brain_simulation_uses_digital_twin_sandbox_and_never_modifies_production_data",
    ]:
        assert phrase in portal


def test_pack_decision_engine_present():
    portal = read("portal_v2.py")
    for phrase in [
        "enterprise_decision_engine_payload",
        "decision_risk_scoring_payload",
        "decision_opportunity_engine_payload",
        "explainable_recommendations_payload",
        "decision_approval_gate_payload",
        "decision_engine_get",
        "all_business_recommendations_must_show_basis_risk_score_and_confidence",
        "each_decision_risk_score_must_include_rationale_and_evidence",
        "high_risk_decision_actions_must_enter_human_approval_and_must_not_auto_execute",
        "decision_engine_can_recommend_and_request_approval_but_must_not_auto_execute_high_risk_actions",
        "must_use_unified_data_model",
        "must_use_unified_kpi_catalog",
        "must_use_enterprise_knowledge",
    ]:
        assert phrase in portal


def test_pack_ai_strategy_center_present():
    portal = read("portal_v2.py")
    for phrase in [
        "ai_strategy_center_payload",
        "strategy_okr_service_payload",
        "strategy_model_payload",
        "strategy_scenario_comparison_payload",
        "strategy_expansion_analysis_payload",
        "strategy_brand_product_payload",
        "strategy_dashboard_payload",
        "strategy_center_get",
        "strategy_okrs_must_link_to_unified_kpi_catalog_and_metrics_service",
        "strategy_models_must_use_unified_data_model_enterprise_knowledge_operating_metrics_and_history",
        "strategy_scenarios_are_compared_in_digital_twin_sandbox_and_do_not_modify_production_data",
        "strategy_analysis_must_remain_consistent_with_enterprise_decision_engine_digital_twin_and_data_intelligence",
    ]:
        assert phrase in portal


def test_pack_foxbrain_university_present():
    portal = read("portal_v2.py")
    for phrase in [
        "foxbrain_university_payload",
        "university_learning_catalog_payload",
        "university_learning_paths_payload",
        "university_ai_tutor_payload",
        "university_certification_payload",
        "university_progress_payload",
        "university_knowledge_feedback_payload",
        "university_get",
        "enterprise_knowledge_platform_and_learning_center_are_bidirectionally_connected",
        "learning_paths_are_recommendations_and_do_not_change_business_permissions_automatically",
        "certification_results_can_support_employee_growth_but_must_not_automatically_change_business_permissions",
        "learning_results_never_auto_grant_business_permissions_manager_rules_decide",
        "learning_questions_improve_knowledge_base_after_review_not_direct_publish",
    ]:
        assert phrase in portal


def test_pack_growth_engine_present():
    portal = read("portal_v2.py")
    for phrase in [
        "enterprise_growth_engine_payload",
        "growth_scorecard_payload",
        "store_growth_analytics_payload",
        "brand_product_growth_payload",
        "customer_growth_models_payload",
        "executive_growth_scorecard_payload",
        "growth_engine_get",
        "growth_scores_must_be_traceable_to_unified_data_model_kpi_and_decision_engine",
        "all_growth_recommendations_must_be_explainable_and_traceable_to_data_sources",
        "store_growth_recommendations_must_trace_to_metrics_tasks_and_knowledge",
        "brand_and_product_growth_scores_must_reference_category_brand_product_and_promotion_sources",
        "customer_growth_recommendations_must_trace_to_member_segments_loyalty_and_campaign_sources",
    ]:
        assert phrase in portal


def test_pack_executive_command_center_present():
    portal = read("portal_v2.py")
    for phrase in [
        "executive_command_center_payload",
        "executive_command_dashboard_payload",
        "executive_risk_center_payload",
        "executive_ai_command_payload",
        "executive_system_health_payload",
        "executive_module_monitoring_payload",
        "executive_command_center_get",
        "unified_enterprise_management_entry",
        "all_command_center_modules_follow_rbac_and_default_deny",
        "all_command_center_data_uses_unified_data_model_and_metrics_service",
        "system_health_rolls_up_all_modules_into_unified_monitoring",
        "ai_command_can_draft_route_and_request_approval_but_must_not_bypass_permissions",
        "executive_risk_center_uses_unified_risk_inputs_and_traceable_evidence",
    ]:
        assert phrase in portal


def test_pack_release_1_0_present():
    portal = read("portal_v2.py")
    docs_report = read("docs/FoxBrain_OS_1_0_Architecture_Review_Report.md")
    for phrase in [
        "release_1_0_payload",
        "release_1_0_module_registry_payload",
        "release_1_0_integration_payload",
        "architecture_review_report_payload",
        "do_not_add_unplanned_features_prioritize_architecture_integration_interface_consistency_docs_tests_production_readiness",
        "no_unplanned_features_architecture_unification_first",
        "release_candidate_ready_after_remote_smoke_test",
        "packs_01_19_integrated",
    ]:
        assert phrase in portal
    for phrase in [
        "FoxBrain OS 1.0 Architecture Review Report",
        "Completed Modules",
        "Pending Modules",
        "Technical Debt",
        "Next Stage Recommendations",
        "remote smoke test",
    ]:
        assert phrase in docs_report


def test_production_deployment_files_present():
    for file_name in [
        "Dockerfile",
        "docker-compose.yml",
        ".env.example",
        "install.sh",
        "healthcheck.sh",
        "backup.sh",
        "restore.sh",
        "README_CLOUD_DEPLOY.md",
        "README_BACKUP_RESTORE.md",
        ".github/workflows/deploy-cloud.yml",
    ]:
        assert (ROOT / file_name).exists()


def test_production_compose_health_and_restart():
    compose = read("docker-compose.yml")
    for phrase in ["restart: always", "healthcheck:", "foxbrain-web", "foxbrain-worker", "nginx"]:
        assert phrase in compose


def test_enterprise_pack_docs_present():
    for doc in [
        "docs/110_ENTERPRISE_PACK_01.md",
        "docs/111_ENTERPRISE_PACK_02_SAP_AI.md",
        "docs/112_ENTERPRISE_PACK_03_KNOWLEDGE.md",
        "docs/113_ENTERPRISE_PACK_04_AI_AGENTS.md",
        "docs/114_ENTERPRISE_PACK_05_DASHBOARD.md",
        "docs/115_ENTERPRISE_PACK_06_AUTOMATION.md",
        "docs/116_ENTERPRISE_PACK_07_ENTERPRISE_BRAIN.md",
        "docs/117_ENTERPRISE_PACK_08_MOBILE_PORTAL.md",
        "docs/118_ENTERPRISE_PACK_09_ENTERPRISE_MEMORY.md",
        "docs/119_ENTERPRISE_PACK_10_RELEASE_PRODUCTION.md",
        "docs/120_ENTERPRISE_PACK_11_SECURITY_GOVERNANCE.md",
        "docs/121_ENTERPRISE_PACK_12_SDK_MARKETPLACE.md",
        "docs/122_ENTERPRISE_PACK_13_DATA_INTELLIGENCE.md",
        "docs/123_ENTERPRISE_PACK_14_DIGITAL_TWIN.md",
        "docs/124_ENTERPRISE_PACK_15_DECISION_ENGINE.md",
        "docs/125_ENTERPRISE_PACK_16_AI_STRATEGY_CENTER.md",
        "docs/126_ENTERPRISE_PACK_17_FOXBRAIN_UNIVERSITY.md",
        "docs/127_ENTERPRISE_PACK_18_GROWTH_ENGINE.md",
        "docs/128_ENTERPRISE_PACK_19_COMMAND_CENTER.md",
        "docs/129_ENTERPRISE_PACK_20_RELEASE_1_0.md",
        "docs/FoxBrain_OS_1_0_Architecture_Review_Report.md",
        "docs/OPERATIONS_RUNBOOK_1_0.md",
        "docs/SECURITY_BASELINE_1_0.md",
        "docs/SDK_EXTENSION_STANDARD.md",
        "docs/RELEASE_1_0_PRODUCTION_CHECKLIST.md",
        "docs/CODEX_TASKS/Task041_Pack02_SAP_AI_Connector.md",
        "docs/CODEX_TASKS/Task042_Pack03_Knowledge_Platform.md",
        "docs/CODEX_TASKS/Task043_Pack04_AI_Agent_Framework.md",
        "docs/CODEX_TASKS/Task044_Pack05_Dashboard_Framework.md",
        "docs/CODEX_TASKS/Task045_Pack06_Automation_Framework.md",
        "docs/CODEX_TASKS/Task046_Pack07_Enterprise_Brain.md",
        "docs/CODEX_TASKS/Task047_Pack08_Mobile_Portal.md",
        "docs/CODEX_TASKS/Task048_Pack09_Enterprise_Memory.md",
        "docs/CODEX_TASKS/Task049_Pack10_Release_Production.md",
        "docs/CODEX_TASKS/Task050_Pack11_Security_Governance.md",
        "docs/CODEX_TASKS/Task051_Pack12_SDK_Marketplace.md",
        "docs/CODEX_TASKS/Task052_Pack13_Data_Intelligence.md",
        "docs/CODEX_TASKS/Task053_Pack14_Digital_Twin.md",
        "docs/CODEX_TASKS/Task054_Pack15_Decision_Engine.md",
        "docs/CODEX_TASKS/Task055_Pack16_AI_Strategy_Center.md",
        "docs/CODEX_TASKS/Task056_Pack17_FoxBrain_University.md",
        "docs/CODEX_TASKS/Task057_Pack18_Growth_Engine.md",
        "docs/CODEX_TASKS/Task058_Pack19_Command_Center.md",
        "docs/CODEX_TASKS/Task059_Pack20_Release_1_0.md",
    ]:
        assert (ROOT / doc).exists()


def test_foxbrain_os_6_enterprise_ai_platform_present():
    portal = read("portal_v2.py")
    for phrase in [
        "platform_plugins",
        "integration_hub_connections",
        "api_governance_policies",
        "platform_tenants",
        "enterprise_ai_platform_payload",
        "platform_plugins_payload",
        "integration_hub_payload",
        "api_governance_payload",
        "multi_company_brand_payload",
        "developer_docs_payload",
        "platform_monitoring_payload",
        "high_risk_platform_operations_require_human_approval",
        "/enterprise-ai-platform",
        "/api/enterprise-ai-platform",
        "manual_approval_required",
    ]:
        assert phrase in portal


def test_foxbrain_os_6_homepage_minimal_entry_layer():
    portal = read("portal_v2.py")
    dashboard_start = portal.rindex("    def dashboard(self, user):")
    dashboard_end = portal.index("    def os_layer_cards(self, items):", dashboard_start)
    dashboard = portal[dashboard_start:dashboard_end]
    assert "minimal_links" in dashboard
    assert "return self.out(layout(T[\"brand\"], body, user=user, wide=False))" in dashboard
    assert "/enterprise-ai-platform" in portal
    assert "/enterprise-ai-platform" not in dashboard
    for phrase in ["/owner/enterprise", "/owner/assets", "/owner/archive", "/drive", "/jarvis", "/owner/decision", "/owner/data", "/owner/projects", "/owner/strategy", "/owner/system"]:
        assert phrase in dashboard
    for phrase in ["/os/business", "/os/ai", "/os/messages", "/os/me"]:
        assert phrase not in dashboard


def test_homepage_business_radar_is_independent_section():
    portal = read("portal_v2.py")
    final_dashboard_start = portal.rindex("    def dashboard(self, user):")
    final_dashboard_end = portal.index("    def os_layer_cards(self, items):", final_dashboard_start)
    final_dashboard = portal[final_dashboard_start:final_dashboard_end]
    assert "/business-radar" not in final_dashboard
    assert "self.cockpit_data()" not in final_dashboard
    assert "smart_business_insights" not in final_dashboard
    for phrase in [
        "yesterday_sales",
        "month_sales",
        "gross_profit",
        "risk_count",
        "insight_cards",
        "business_radar_payload",
    ]:
        assert phrase not in final_dashboard
    assert "def business_radar" in portal
    assert "def business_radar_payload" in portal
    assert "def api_business_radar_get" in portal
    assert 'if path == "/business-radar"' in portal
    assert '"/api/business-radar"' in portal
    assert "entry_only_no_expanded_metrics_or_insights" in portal


def test_business_radar_independent_section_docs_present():
    docs = [
        "docs/767_BUSINESS_RADAR_INDEPENDENT_SECTION.md",
        "docs/CODEX_TASKS/Task080_Business_Radar_Independent_Section.md",
    ]
    for doc in docs:
        assert (ROOT / doc).exists()
    combined = "\n".join(read(doc) for doc in docs)
    for phrase in [
        "Business Radar",
        "independent section",
        "/business-radar",
        "/api/business-radar",
        "home page only shows an entry",
        "must not expand radar metrics",
        "No database changes",
    ]:
        assert phrase in combined


def test_foxbrain_os_6_docs_present():
    docs = [
        "docs/600_FOXBRAIN_OS_6_0_ENTERPRISE_AI_PLATFORM.md",
        "docs/601_FOXBRAIN_OS_6_0_PLUGIN_INTEGRATION_API_GOVERNANCE.md",
        "docs/CODEX_TASKS/Task070_FoxBrain_OS_6_0_Enterprise_AI_Platform.md",
    ]
    for doc in docs:
        assert (ROOT / doc).exists()
    combined = "\n".join(read(doc) for doc in docs)
    for phrase in [
        "Enterprise AI Platform",
        "Plugin system",
        "Integration Hub",
        "API governance",
        "Multi-company",
        "multi-brand",
        "developer documentation",
        "Platform monitoring",
        "High-risk",
        "human approval",
        "home page",
        "minimal",
    ]:
        assert phrase in combined


def test_foxbrain_os_6_1_sap_smart_knowledge_present():
    portal = read("portal_v2.py")
    for phrase in [
        "sap_knowledge_mappings",
        "sap_knowledge_jobs",
        "sap_knowledge_snapshots",
        "sap_knowledge_source_rows",
        "generate_sap_knowledge_items",
        "sap_knowledge_payload",
        "sap_knowledge_center",
        "/knowledge/sap",
        "/api/knowledge/sap-intelligence",
        "/api/knowledge/sap-generate",
        "/api/knowledge/sap-mappings",
        "/api/knowledge/sap-snapshots",
        "read_only_knowledge_generation_no_sap_writeback",
        "sap_smart_knowledge_base",
    ]:
        assert phrase in portal


def test_foxbrain_os_6_1_sap_smart_knowledge_docs_present():
    docs = [
        "docs/610_FOXBRAIN_OS_6_1_SAP_SMART_KNOWLEDGE.md",
        "docs/611_FOXBRAIN_OS_6_1_SAP_KNOWLEDGE_MAPPING_TEMPLATE.md",
        "docs/CODEX_TASKS/Task071_FoxBrain_OS_6_1_SAP_Smart_Knowledge.md",
    ]
    for doc in docs:
        assert (ROOT / doc).exists()
    combined = "\n".join(read(doc) for doc in docs)
    for phrase in [
        "FoxBrain OS 6.1",
        "SAP Smart Knowledge",
        "brands, products, stores, employees, customers and suppliers",
        "read-only",
        "No SAP writeback",
        "source snapshot",
        "AI-queryable",
    ]:
        assert phrase in combined


def test_enterprise_v1_architecture_contract_module_present():
    architecture = read("foxbrain_os/architecture.py")
    init_file = read("foxbrain_os/__init__.py")
    portal = read("portal_v2.py")
    for phrase in [
        "EnterpriseModule",
        "UpgradePhase",
        "ENTERPRISE_MODULES",
        "ENTERPRISE_UPGRADE_PHASES",
        "HIGH_RISK_ACTIONS",
        "approval_required_for",
        "enterprise_v1_architecture_contract",
        "compatibility_first_modular_refactor",
        "high_risk_actions_require_human_approval",
    ]:
        assert phrase in architecture
    assert "enterprise_v1_architecture_contract" in init_file
    assert "/api/enterprise-ai-platform/architecture" in portal
    assert "enterprise_v1_architecture" in portal


def test_enterprise_v1_architecture_contract_imports():
    import importlib.util

    spec = importlib.util.spec_from_file_location("foxbrain_architecture", ROOT / "foxbrain_os" / "architecture.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    contract = module.enterprise_v1_architecture_contract()
    assert contract["ok"] is True
    assert contract["version"] == "FoxBrain OS Enterprise V1.0"
    assert module.approval_required_for("sap_writeback") is True
    assert module.approval_required_for("read_only_query", "low") is False
    assert "knowledge" in [item["key"] for item in contract["modules"]]
    assert "stage_1" in [item["phase"] for item in contract["upgrade_phases"]]


def test_enterprise_v1_stage_docs_present():
    docs = [
        "docs/700_FOXBRAIN_OS_ENTERPRISE_V1_0_ARCHITECTURE_UPGRADE.md",
        "docs/701_FOXBRAIN_OS_ENTERPRISE_V1_0_STAGE_0_STRUCTURE_AUDIT.md",
        "docs/702_FOXBRAIN_OS_ENTERPRISE_V1_0_STAGE_1_ARCHITECTURE_BASELINE.md",
        "docs/CODEX_TASKS/Task072_FoxBrain_OS_Enterprise_V1_0_Architecture_Baseline.md",
    ]
    for doc in docs:
        assert (ROOT / doc).exists()
    combined = "\n".join(read(doc) for doc in docs)
    for phrase in [
        "Enterprise V1.0",
        "Stage 0",
        "Stage 1",
        "architecture contract",
        "compatibility-first",
        "not a page-only",
        "High-risk operations require human approval",
    ]:
        assert phrase in combined


def test_enterprise_v1_1_ai_knowledge_brain_module_present():
    brain = read("foxbrain_os/knowledge_brain.py")
    init_file = read("foxbrain_os/__init__.py")
    architecture = read("foxbrain_os/architecture.py")
    portal = read("portal_v2.py")
    for phrase in [
        "SAP_UNDERSTANDING_DIMENSIONS",
        "KNOWLEDGE_BRAIN_GUARDRAILS",
        "build_sap_data_understanding",
        "build_enterprise_knowledge_brain",
        "build_query_plan",
        "sap_data_understanding",
        "ai_knowledge_brain",
        "cite_knowledge_or_sap_source",
        "sap_writeback_disabled",
    ]:
        assert phrase in brain
    assert "build_enterprise_knowledge_brain" in init_file
    assert "knowledge_brain" in architecture
    for phrase in [
        "/knowledge/brain",
        "/api/knowledge/brain",
        "/api/knowledge/sap-understanding",
        "/api/knowledge/query-plan",
        "ai_knowledge_brain_payload",
        "sap_data_understanding_payload",
    ]:
        assert phrase in portal


def test_enterprise_v1_1_ai_knowledge_brain_imports():
    import importlib.util

    spec = importlib.util.spec_from_file_location("foxbrain_knowledge_brain", ROOT / "foxbrain_os" / "knowledge_brain.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    sap = module.build_sap_data_understanding({"month_sales": 100, "inventory_amount": 50}, {"freshness": "fresh"}, {"metrics": {"sap_knowledge_items": 2, "candidate_count": 3}})
    brain = module.build_enterprise_knowledge_brain({"knowledge_items": 2, "chunks": 4, "pending_review": 0}, sap, [])
    plan = module.build_query_plan("查看 SAP 库存和毛利", "sap")
    assert sap["ok"] is True
    assert brain["version"] == "FoxBrain OS Enterprise V1.1"
    assert plan["needs_sap_context"] is True
    assert brain["guardrails"]["sap_writeback_disabled"] is True


def test_enterprise_v1_1_docs_present():
    docs = [
        "docs/710_FOXBRAIN_OS_ENTERPRISE_V1_1_AI_KNOWLEDGE_BRAIN.md",
        "docs/711_FOXBRAIN_OS_ENTERPRISE_V1_1_STAGE_2_AI_KNOWLEDGE_BRAIN_RESULT.md",
        "docs/CODEX_TASKS/Task073_FoxBrain_OS_Enterprise_V1_1_AI_Knowledge_Brain.md",
    ]
    for doc in docs:
        assert (ROOT / doc).exists()
    combined = "\n".join(read(doc) for doc in docs)
    for phrase in [
        "V1.1",
        "AI Knowledge Brain",
        "SAP data understanding",
        "enterprise knowledge base",
        "No SAP writeback",
        "High-risk actions require human approval",
        "without rebuilding the system",
    ]:
        assert phrase in combined


def test_enterprise_v1_2_agent_orchestration_module_present():
    orchestration = read("foxbrain_os/agent_orchestration.py")
    init_file = read("foxbrain_os/__init__.py")
    architecture = read("foxbrain_os/architecture.py")
    portal = read("portal_v2.py")
    for phrase in [
        "AGENT_DOMAINS",
        "AGENT_EXECUTION_POLICY",
        "Business Operations Agent",
        "Inventory Agent",
        "Member Growth Agent",
        "Content Agent",
        "all_ai_execution_requires_approval",
        "build_agent_orchestration_contract",
        "build_agent_plan_request",
        "extend_existing_agent_framework_without_database_refactor",
    ]:
        assert phrase in orchestration
    assert "build_agent_orchestration_contract" in init_file
    assert "agent_orchestration" in architecture
    for phrase in [
        "/agents/v1.2",
        "/api/agents/v1.2",
        "/api/agents/v1.2/plan",
        "enterprise_v12_agent_orchestration_payload",
        "create_v12_agent_plan",
        "all_ai_execution_requests_must_enter_approval_flow",
        "blocked_manual_required",
        "approval_then_execute",
    ]:
        assert phrase in portal


def test_enterprise_v1_2_agent_orchestration_imports():
    import importlib.util

    spec = importlib.util.spec_from_file_location("foxbrain_agent_orchestration", ROOT / "foxbrain_os" / "agent_orchestration.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    contract = module.build_agent_orchestration_contract()
    plan = module.build_agent_plan_request("inventory", "review stock risk", "boss")
    domains = [item["key"] for item in contract["domains"]]
    assert contract["ok"] is True
    assert contract["version"] == "FoxBrain OS Enterprise V1.2"
    assert {"business", "inventory", "membership", "content"}.issubset(set(domains))
    assert plan["approval_required"] is True
    assert plan["execution_mode"] == "approval_then_execute"
    assert plan["execution_status"] == "blocked_manual_required"
    assert plan["risk_level"] == "high"


def test_enterprise_v1_2_docs_present():
    docs = [
        "docs/720_FOXBRAIN_OS_ENTERPRISE_V1_2_AGENT_ORCHESTRATION.md",
        "docs/721_FOXBRAIN_OS_ENTERPRISE_V1_2_STAGE_3_AGENT_ORCHESTRATION_RESULT.md",
        "docs/CODEX_TASKS/Task074_FoxBrain_OS_Enterprise_V1_2_Agent_Orchestration.md",
    ]
    for doc in docs:
        assert (ROOT / doc).exists()
    combined = "\n".join(read(doc) for doc in docs)
    for phrase in [
        "V1.2",
        "Business Operations Agent",
        "Inventory Agent",
        "Member Growth Agent",
        "Content Agent",
        "All AI execution requests must enter the approval flow first",
        "without refactoring the database",
        "SAP B1 remains the core business data source",
    ]:
        assert phrase in combined


def test_enterprise_v1_3_auto_operation_module_present():
    auto = read("foxbrain_os/auto_operation.py")
    init_file = read("foxbrain_os/__init__.py")
    architecture = read("foxbrain_os/architecture.py")
    portal = read("portal_v2.py")
    for phrase in [
        "SAP_READ_ONLY_POLICY",
        "AUTO_OPERATION_STAGES",
        "SAP Daily Sync",
        "AI Analysis",
        "Boss Daily Report",
        "Task Center",
        "Approval Flow",
        "build_auto_operation_contract",
        "build_daily_loop_plan",
        "writeback_allowed",
    ]:
        assert phrase in auto
    assert "build_auto_operation_contract" in init_file
    assert "auto_operation_loop" in architecture
    for phrase in [
        "/auto-operation",
        "/api/auto-operation",
        "/api/auto-operation/contract",
        "/api/auto-operation/run-daily-loop",
        "auto_operation_payload",
        "create_v13_daily_loop_plan",
        "sap_production_server_independent_read_only_sync_no_writeback",
        "daily_auto_operation_loop",
    ]:
        assert phrase in portal


def test_enterprise_v1_3_auto_operation_imports():
    import importlib.util

    spec = importlib.util.spec_from_file_location("foxbrain_auto_operation", ROOT / "foxbrain_os" / "auto_operation.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    contract = module.build_auto_operation_contract()
    plan = module.build_daily_loop_plan(
        {"freshness": "fresh", "last_status": "success", "next_run_time": "22:00"},
        {"metrics": {"month_sales": 100}, "active_risks": []},
        {"actions": ["review sales"]},
        {"steps": []},
        {"approvals": []},
    )
    assert contract["ok"] is True
    assert contract["version"] == "FoxBrain OS Enterprise V1.3"
    assert contract["sap_read_only_policy"]["sap_production_server_independent"] is True
    assert contract["sap_read_only_policy"]["writeback_allowed"] is False
    assert plan["approval_required"] is True
    assert plan["execution_mode"] == "approval_then_execute"
    assert plan["execution_status"] == "blocked_manual_required"
    assert plan["sap"]["read_only"] is True


def test_enterprise_v1_3_docs_present():
    docs = [
        "docs/730_FOXBRAIN_OS_ENTERPRISE_V1_3_AUTO_OPERATION_LOOP.md",
        "docs/731_FOXBRAIN_OS_ENTERPRISE_V1_3_STAGE_4_AUTO_OPERATION_RESULT.md",
        "docs/CODEX_TASKS/Task075_FoxBrain_OS_Enterprise_V1_3_Auto_Operation_Loop.md",
    ]
    for doc in docs:
        assert (ROOT / doc).exists()
    combined = "\n".join(read(doc) for doc in docs)
    for phrase in [
        "V1.3",
        "SAP daily sync",
        "AI analysis",
        "boss daily report",
        "task center",
        "approval flow",
        "SAP production server remains independent",
        "read-only",
        "No SAP writeback",
    ]:
        assert phrase in combined


def test_enterprise_v1_4_sap_knowledge_engine_module_present():
    engine = read("foxbrain_os/sap_knowledge_engine.py")
    init_file = read("foxbrain_os/__init__.py")
    architecture = read("foxbrain_os/architecture.py")
    portal = read("portal_v2.py")
    for phrase in [
        "SAP_PRODUCTION_BOUNDARY",
        "READ_ONLY_SYNC_LAYERS",
        "AI_WAREHOUSE_DATASETS",
        "SAP_KNOWLEDGE_MODELS",
        "Product Knowledge Model",
        "Sales Knowledge Model",
        "Inventory Knowledge Model",
        "Member Knowledge Model",
        "build_sap_knowledge_engine_contract",
        "build_warehouse_readiness",
        "build_model_catalog",
        "do_not_directly_connect_modify_sap_production_database",
    ]:
        assert phrase in engine
    assert "build_sap_knowledge_engine_contract" in init_file
    assert "sap_knowledge_engine" in architecture
    for phrase in [
        "/api/sap-knowledge-engine",
        "/api/sap-knowledge-engine/warehouse",
        "/api/sap-knowledge-engine/models",
        "/api/knowledge/sap-engine",
        "sap_knowledge_engine_payload",
        "enterprise_v14_sap_knowledge_engine",
    ]:
        assert phrase in portal


def test_enterprise_v1_4_sap_knowledge_engine_imports():
    import importlib.util

    spec = importlib.util.spec_from_file_location("foxbrain_sap_knowledge_engine", ROOT / "foxbrain_os" / "sap_knowledge_engine.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    contract = module.build_sap_knowledge_engine_contract()
    readiness = module.build_warehouse_readiness({"freshness": "fresh"}, {"sap_knowledge_items": 1})
    catalog = module.build_model_catalog()
    product = module.build_model_catalog("product")
    assert contract["ok"] is True
    assert contract["version"] == "FoxBrain OS Enterprise V1.4"
    assert contract["production_boundary"]["direct_production_write_disabled"] is True
    assert contract["production_boundary"]["read_only_sync_only"] is True
    assert len(contract["read_only_sync_layers"]) == 4
    assert len(readiness["datasets"]) == 4
    assert catalog["model_count"] == 4
    assert product["models"][0]["entity"] == "product"


def test_enterprise_v1_4_docs_present():
    docs = [
        "docs/740_FOXBRAIN_OS_ENTERPRISE_V1_4_SAP_KNOWLEDGE_ENGINE.md",
        "docs/741_FOXBRAIN_OS_ENTERPRISE_V1_4_STAGE_2_SAP_KNOWLEDGE_RESULT.md",
        "docs/CODEX_TASKS/Task076_FoxBrain_OS_Enterprise_V1_4_SAP_Knowledge_Engine.md",
    ]
    for doc in docs:
        assert (ROOT / doc).exists()
    combined = "\n".join(read(doc) for doc in docs)
    for phrase in [
        "V1.4",
        "SAP Knowledge Engine",
        "Read-only SAP sync layer",
        "AI data warehouse",
        "Product knowledge model",
        "Sales knowledge model",
        "Inventory knowledge model",
        "Member knowledge model",
        "Do not directly connect to modify the SAP production database",
        "No SAP writeback",
    ]:
        assert phrase in combined


def test_enterprise_v1_5_knowledge_training_quality_module_present():
    quality = read("foxbrain_os/knowledge_training_quality.py")
    init_file = read("foxbrain_os/__init__.py")
    architecture = read("foxbrain_os/architecture.py")
    portal = read("portal_v2.py")
    for phrase in [
        "KNOWLEDGE_QUALITY_DIMENSIONS",
        "AI_LEARNING_SIGNALS",
        "BOSS_EXPERIENCE_MODELS",
        "Source Traceability",
        "Human Review",
        "Boss Operating Principle",
        "Boss Decision Memory",
        "build_knowledge_training_quality_contract",
        "score_knowledge_quality",
        "build_ai_learning_plan",
        "reviewed_context_learning_not_autonomous_model_training",
    ]:
        assert phrase in quality
    assert "build_knowledge_training_quality_contract" in init_file
    assert "knowledge_training_quality" in architecture
    for phrase in [
        "/api/knowledge-quality",
        "/api/knowledge-quality/score",
        "/api/ai-learning/plan",
        "/api/boss-experience/memory",
        "/api/knowledge/v1.5",
        "knowledge_training_quality_payload",
        "enterprise_v15_knowledge_training_quality",
    ]:
        assert phrase in portal


def test_enterprise_v1_5_knowledge_training_quality_imports():
    import importlib.util

    spec = importlib.util.spec_from_file_location("foxbrain_knowledge_training_quality", ROOT / "foxbrain_os" / "knowledge_training_quality.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    contract = module.build_knowledge_training_quality_contract()
    score = module.score_knowledge_quality({"total": 10, "reviewed": 8, "with_source": 9, "with_summary": 7, "with_keywords": 6, "sap_items": 4, "approved_memory": 2, "decisions": 1})
    plan = module.build_ai_learning_plan(score, {"approved_memory": 2, "decision_memories": 1})
    assert contract["ok"] is True
    assert contract["version"] == "FoxBrain OS Enterprise V1.5"
    assert len(contract["quality_dimensions"]) >= 6
    assert len(contract["ai_learning_signals"]) >= 6
    assert len(contract["boss_experience_models"]) >= 4
    assert score["score"] > 0
    assert score["level"] in ("strong", "usable", "needs_review", "foundation")
    assert plan["learning_mode"] == "reviewed_context_learning_not_autonomous_model_training"


def test_enterprise_v1_5_docs_present():
    docs = [
        "docs/750_FOXBRAIN_OS_ENTERPRISE_V1_5_KNOWLEDGE_TRAINING_QUALITY.md",
        "docs/751_FOXBRAIN_OS_ENTERPRISE_V1_5_STAGE_2_KNOWLEDGE_QUALITY_RESULT.md",
        "docs/CODEX_TASKS/Task077_FoxBrain_OS_Enterprise_V1_5_Knowledge_Training_Quality.md",
    ]
    for doc in docs:
        assert (ROOT / doc).exists()
    combined = "\n".join(read(doc) for doc in docs)
    for phrase in [
        "V1.5",
        "knowledge-base quality",
        "AI learning",
        "boss operating experience",
        "Source traceability",
        "Human review",
        "Boss operating principles",
        "reviewed context learning",
        "High-risk actions still require human approval",
    ]:
        assert phrase in combined


def test_enterprise_v1_6_multi_agent_system_module_present():
    multi_agent = read("foxbrain_os/multi_agent_system.py")
    init_file = read("foxbrain_os/__init__.py")
    architecture = read("foxbrain_os/architecture.py")
    portal = read("portal_v2.py")
    for phrase in [
        "MULTI_AGENT_ROLES",
        "SHARED_SAP_KNOWLEDGE_POLICY",
        "CEO Agent",
        "Business Agent",
        "Inventory Agent",
        "Product Agent",
        "Member Agent",
        "Content Agent",
        "build_multi_agent_system_contract",
        "build_shared_sap_context",
        "build_agent_collaboration_plan",
        "extend_existing_agent_framework_with_shared_sap_knowledge_context_without_rebuilding",
    ]:
        assert phrase in multi_agent
    assert "build_multi_agent_system_contract" in init_file
    assert "multi_agent_system" in architecture
    for phrase in [
        "/agents/v1.6",
        "/api/agents/v1.6",
        "/api/agents/v1.6/shared-sap-knowledge",
        "/api/agents/v1.6/collaboration-plan",
        "enterprise_v16_multi_agent_payload",
        "create_v16_collaboration_plan",
        "enterprise_v16_multi_agent_system",
        "agents_share_sap_knowledge_context",
        "blocked_manual_required",
    ]:
        assert phrase in portal


def test_enterprise_v1_6_multi_agent_system_imports():
    import importlib.util

    spec = importlib.util.spec_from_file_location("foxbrain_multi_agent_system", ROOT / "foxbrain_os" / "multi_agent_system.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    contract = module.build_multi_agent_system_contract()
    shared_context = module.build_shared_sap_context(
        {"contract": {"knowledge_models": [{"key": "product_knowledge_model", "entity": "product"}], "ai_data_warehouse": [{"key": "products"}]}},
        {"quality_score": {"level": "usable"}},
    )
    plan = module.build_agent_collaboration_plan("review growth risk", ["ceo", "inventory", "product", "content"])
    role_names = [role["name"] for role in contract["roles"]]
    assert contract["ok"] is True
    assert contract["version"] == "FoxBrain OS Enterprise V1.6"
    assert {"CEO Agent", "Business Agent", "Inventory Agent", "Product Agent", "Member Agent", "Content Agent"}.issubset(set(role_names))
    assert len(contract["collaboration_flows"]) >= 3
    assert shared_context["readiness"] == "ready"
    assert "product_knowledge_model" in shared_context["available_models"]
    assert plan["approval_required"] is True
    assert plan["execution_mode"] == "approval_then_execute"
    assert plan["execution_status"] == "blocked_manual_required"
    assert plan["risk_level"] == "high"


def test_enterprise_v1_6_docs_present():
    docs = [
        "docs/760_FOXBRAIN_OS_ENTERPRISE_V1_6_MULTI_AGENT_SYSTEM.md",
        "docs/761_FOXBRAIN_OS_ENTERPRISE_V1_6_STAGE_3_MULTI_AGENT_RESULT.md",
        "docs/CODEX_TASKS/Task078_FoxBrain_OS_Enterprise_V1_6_Multi_Agent_System.md",
    ]
    for doc in docs:
        assert (ROOT / doc).exists()
    combined = "\n".join(read(doc) for doc in docs)
    for phrase in [
        "V1.6",
        "multi-agent",
        "CEO Agent",
        "Business Agent",
        "Inventory Agent",
        "Product Agent",
        "Member Agent",
        "Content Agent",
        "shared SAP",
        "No SAP writeback",
        "High-risk",
    ]:
        assert phrase in combined


def test_enterprise_v1_6_5_knowledge_fusion_module_present():
    fusion = read("foxbrain_os/knowledge_fusion.py")
    init_file = read("foxbrain_os/__init__.py")
    architecture = read("foxbrain_os/architecture.py")
    portal = read("portal_v2.py")
    for phrase in [
        "FUSION_KNOWLEDGE_LAYERS",
        "KNOWLEDGE_FUSION_POLICY",
        "SAP Enterprise Knowledge Base",
        "External Industry Knowledge Base",
        "Boss Experience Knowledge Base",
        "build_knowledge_fusion_contract",
        "build_fusion_context",
        "build_agent_fusion_context",
        "external_industry_knowledge_is_context_not_final_truth",
        "boss_experience_requires_review_before_active_use",
    ]:
        assert phrase in fusion
    assert "build_knowledge_fusion_contract" in init_file
    assert "knowledge_fusion" in architecture
    for phrase in [
        "/api/knowledge/fusion",
        "/api/knowledge/v1.6.5",
        "/api/knowledge/fusion/external-industry",
        "/api/agents/v1.6/fusion-knowledge",
        "knowledge_fusion_payload",
        "agent_fusion_knowledge_payload",
        "enterprise_v165_knowledge_fusion",
        "fusion_knowledge",
        "agents_share_fusion_knowledge_context",
    ]:
        assert phrase in portal


def test_enterprise_v1_6_5_knowledge_fusion_imports():
    import importlib.util

    spec = importlib.util.spec_from_file_location("foxbrain_knowledge_fusion", ROOT / "foxbrain_os" / "knowledge_fusion.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    contract = module.build_knowledge_fusion_contract()
    context = module.build_fusion_context(
        {"knowledge_models": {"models": [{"key": "sales_knowledge_model"}, {"key": "inventory_knowledge_model"}]}},
        {"knowledge_quality": {"level": "usable"}, "boss_experience": {"approved_memory": 1, "decision_memories": 1, "operation_feedback": 1}},
        {"items": [{"title": "retail benchmark"}]},
    )
    agent = module.build_agent_fusion_context("inventory", context)
    assert contract["ok"] is True
    assert contract["version"] == "FoxBrain OS Enterprise V1.6.5"
    assert len(contract["layers"]) == 3
    layer_keys = [layer["key"] for layer in contract["layers"]]
    assert {"sap_enterprise_knowledge", "external_industry_knowledge", "boss_experience_knowledge"}.issubset(set(layer_keys))
    assert context["fusion_ready"] is True
    assert context["layer_readiness"]["external_industry_knowledge"] == "ready"
    assert agent["agent"]["agent_key"] == "inventory"
    assert agent["approval_required_for_high_risk"] is True


def test_enterprise_v1_6_5_docs_present():
    docs = [
        "docs/765_FOXBRAIN_OS_ENTERPRISE_V1_6_5_KNOWLEDGE_FUSION.md",
        "docs/766_FOXBRAIN_OS_ENTERPRISE_V1_6_5_STAGE_2_KNOWLEDGE_FUSION_RESULT.md",
        "docs/CODEX_TASKS/Task079_FoxBrain_OS_Enterprise_V1_6_5_Knowledge_Fusion.md",
    ]
    for doc in docs:
        assert (ROOT / doc).exists()
    combined = "\n".join(read(doc) for doc in docs)
    for phrase in [
        "V1.6.5",
        "Knowledge Fusion",
        "SAP Enterprise Knowledge Base",
        "External Industry Knowledge Base",
        "Boss Experience Knowledge Base",
        "existing Agents",
        "No SAP writeback",
        "High-risk",
    ]:
        assert phrase in combined


def test_enterprise_v1_6_6_knowledge_training_rules_engine_module_present():
    engine = read("foxbrain_os/knowledge_training_rules_engine.py")
    init_file = read("foxbrain_os/__init__.py")
    architecture = read("foxbrain_os/architecture.py")
    portal = read("portal_v2.py")
    for phrase in [
        "TRAINING_SIGNALS",
        "OPERATING_RULE_LIBRARY",
        "DECISION_GUARDRAILS",
        "KNOWLEDGE_TRAINING_POLICY",
        "Inventory Risk First",
        "Gross Profit Before Sales Volume",
        "FireFox Operating Logic Required",
        "build_knowledge_training_engine_contract",
        "build_operating_rule_library",
        "build_training_cycle_plan",
        "build_ai_decision_logic",
    ]:
        assert phrase in engine
    assert "build_knowledge_training_engine_contract" in init_file
    assert "knowledge_training_rules_engine" in architecture
    for phrase in [
        "/api/knowledge-training-engine",
        "/api/knowledge/v1.6.6",
        "/api/knowledge-training-engine/rules",
        "/api/knowledge-training-engine/training-cycle",
        "/api/knowledge-training-engine/decision-logic",
        "knowledge_training_engine_payload",
        "enterprise_v166_knowledge_training_engine",
        "ai_decisions_must_follow_reviewed_fire_fox_operating_rules",
    ]:
        assert phrase in portal


def test_enterprise_v1_6_6_knowledge_training_rules_engine_imports():
    import importlib.util

    spec = importlib.util.spec_from_file_location("foxbrain_training_rules", ROOT / "foxbrain_os" / "knowledge_training_rules_engine.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    contract = module.build_knowledge_training_engine_contract()
    rules = module.build_operating_rule_library()
    inventory = module.build_operating_rule_library("inventory")
    cycle = module.build_training_cycle_plan({"layer_readiness": {"sap_enterprise_knowledge": "ready"}}, {"knowledge_quality": {"level": "usable"}})
    logic = module.build_ai_decision_logic({"fusion_ready": True}, {"month_sales": 100})
    assert contract["ok"] is True
    assert contract["version"] == "FoxBrain OS Enterprise V1.6.6"
    assert len(contract["training_signals"]) >= 4
    assert len(rules["rules"]) >= 6
    assert inventory["rules"][0]["domain"] == "inventory"
    assert cycle["approval_required"] is True
    assert logic["decision_logic"]["source_priority"][0] == "SAP facts define current company state"
    assert logic["approval_boundary"] == "ai_decision_support_only_high_risk_execution_requires_human_approval"


def test_enterprise_v1_6_6_docs_present():
    docs = [
        "docs/768_FOXBRAIN_OS_ENTERPRISE_V1_6_6_KNOWLEDGE_TRAINING_RULES_ENGINE.md",
        "docs/769_FOXBRAIN_OS_ENTERPRISE_V1_6_6_STAGE_2_TRAINING_RULES_RESULT.md",
        "docs/CODEX_TASKS/Task081_FoxBrain_OS_Enterprise_V1_6_6_Knowledge_Training_Rules_Engine.md",
    ]
    for doc in docs:
        assert (ROOT / doc).exists()
    combined = "\n".join(read(doc) for doc in docs)
    for phrase in [
        "V1.6.6",
        "Knowledge Training",
        "operating rule library",
        "FireFox operating logic",
        "SAP data",
        "external knowledge",
        "boss operating experience",
        "No SAP writeback",
        "High-risk",
    ]:
        assert phrase in combined


def test_enterprise_v1_7_ai_business_decision_center_module_present():
    module = read("foxbrain_os/ai_business_management.py")
    init_file = read("foxbrain_os/__init__.py")
    architecture = read("foxbrain_os/architecture.py")
    portal = read("portal_v2.py")
    for phrase in [
        "AI_BUSINESS_CENTER_MODULES",
        "AI_BUSINESS_AUTOMATIONS",
        "V17_DATA_TABLES",
        "V17_GUARDRAILS",
        "build_ai_business_center_contract",
        "build_daily_business_report",
        "build_sales_forecast",
        "build_inventory_analysis",
        "build_purchase_recommendation",
        "build_profit_analysis",
        "build_risk_alerts",
        "build_ai_task_plan",
        "SAP sales",
        "SAP inventory",
        "brand profiles",
        "operating rules",
    ]:
        assert phrase in module
    assert "build_ai_business_center_contract" in init_file
    assert "ai_business_management_center" in architecture
    for phrase in [
        "/ai-business-center",
        "/api/decision/today",
        "/api/forecast/sales",
        "/api/inventory/risk",
        "/api/purchase/recommend",
        "/api/profit/analysis",
        "/api/risk/list",
        "/api/ai/task/create",
        "ai_business_center_payload",
        "persist_ai_business_snapshot",
        "enterprise_v17_ai_business_center",
        "all_high_risk_business_actions_require_boss_approval_no_auto_execution",
    ]:
        assert phrase in portal


def test_enterprise_v1_7_ai_business_decision_center_imports():
    import importlib.util

    spec = importlib.util.spec_from_file_location("foxbrain_ai_business", ROOT / "foxbrain_os" / "ai_business_management.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    metrics = {"yesterday_sales": 0, "month_sales": 300000, "gross_profit": 90000, "gross_margin": 0.3, "risk_count": 12, "inventory_amount": 1800000}
    contract = module.build_ai_business_center_contract()
    report = module.build_daily_business_report(metrics)
    forecast = module.build_sales_forecast(metrics, "7d")
    inventory = module.build_inventory_analysis(metrics)
    purchase = module.build_purchase_recommendation(metrics, inventory)
    profit = module.build_profit_analysis(metrics)
    risks = module.build_risk_alerts(metrics)
    task = module.build_ai_task_plan("分析一下南山店最近经营情况")
    assert contract["ok"] is True
    assert contract["version"] == "FoxBrain OS Enterprise V1.7"
    assert "boss_approval" in contract["data_flow"]
    assert report["approval_required"] is True
    assert forecast["confidence"] > 0
    assert inventory["health_score"] > 0
    assert purchase["approval_required"] is True
    assert profit["real_profit_contribution_ranking"][0]["brand"] == "Kailas"
    assert any(r["type"] == "sales_risk" for r in risks)
    assert task["required_calls"] == ["SAP sales", "SAP inventory", "brand profiles", "operating rules"]
    assert task["expected_output"] == ["problem", "cause", "advice", "execution_plan"]
    assert task["approval_required"] is True


def test_enterprise_v1_7_ai_business_decision_center_docs_and_boundaries_present():
    docs = [
        "docs/770_FOXBRAIN_OS_ENTERPRISE_V1_7_AI_BUSINESS_DECISION_CENTER.md",
        "docs/771_FOXBRAIN_OS_ENTERPRISE_V1_7_STAGE_4_AI_BUSINESS_RESULT.md",
        "docs/CODEX_TASKS/Task082_FoxBrain_OS_Enterprise_V1_7_AI_Business_Decision_Center.md",
    ]
    dirs = [
        "apps/api/modules/decision-center/README.md",
        "apps/api/modules/forecast/README.md",
        "apps/api/modules/risk-engine/README.md",
        "apps/api/modules/ai-memory/README.md",
        "apps/worker/jobs/decision-analysis/README.md",
    ]
    for path in docs + dirs:
        assert (ROOT / path).exists()
    portal = read("portal_v2.py")
    for table in [
        "sales_forecasts",
        "inventory_analysis",
        "risk_alerts",
        "business_memory",
        "ai_recommendation_history",
    ]:
        assert "create table if not exists " + table in portal
    combined = "\n".join(read(doc) for doc in docs + dirs)
    for phrase in [
        "V1.7",
        "AI Business Center",
        "sales forecast",
        "inventory risk",
        "human approval",
        "SAP readonly",
        "AI recommendation history",
    ]:
        assert phrase in combined


def test_enterprise_v1_8_workflow_automation_engine_module_present():
    module = read("foxbrain_os/workflow_automation_engine.py")
    init_file = read("foxbrain_os/__init__.py")
    architecture = read("foxbrain_os/architecture.py")
    portal = read("portal_v2.py")
    for phrase in [
        "WORKFLOW_NODE_TYPES",
        "V18_DIGITAL_EMPLOYEES",
        "V18_DATA_TABLES",
        "V18_GUARDRAILS",
        "build_workflow_automation_contract",
        "build_inventory_warning_workflow",
        "build_ai_operating_task",
        "build_notification_plan",
        "build_decision_feedback_learning",
        "build_business_case_template",
        "build_periodic_report_plan",
        "build_workflow_acceptance_plan",
        "AI General Manager",
        "AI Purchase Manager",
        "Human Approval",
    ]:
        assert phrase in module
    assert "build_workflow_automation_contract" in init_file
    assert "workflow_automation_engine" in architecture
    for phrase in [
        "/workflow-automation",
        "/api/workflow-automation",
        "/api/workflow/run-inventory-risk",
        "/api/workflow-automation/builder",
        "/api/workflow-automation/tasks",
        "/api/workflow-automation/approvals",
        "/api/workflow-automation/notifications",
        "/api/workflow-automation/digital-employees",
        "/api/workflow-automation/feedback",
        "/api/workflow-automation/business-cases",
        "workflow_automation_payload",
        "create_v18_inventory_workflow_run",
        "enterprise_v18_workflow_automation_engine",
        "ai_can_create_tasks_notifications_and_approval_records_but_high_risk_execution_waits_for_human_approval",
    ]:
        assert phrase in portal


def test_enterprise_v1_8_workflow_automation_engine_imports():
    import importlib.util

    spec = importlib.util.spec_from_file_location("foxbrain_workflow_automation", ROOT / "foxbrain_os" / "workflow_automation_engine.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    contract = module.build_workflow_automation_contract()
    workflow = module.build_inventory_warning_workflow()
    task = module.build_ai_operating_task("检查最近库存风险")
    notification = module.build_notification_plan(task)
    feedback = module.build_decision_feedback_learning("Kailas increase inventory", "approved", "sales up 30%")
    case = module.build_business_case_template()
    daily = module.build_periodic_report_plan("daily")
    acceptance = module.build_workflow_acceptance_plan("检查最近库存风险")
    assert contract["ok"] is True
    assert contract["version"] == "FoxBrain OS Enterprise V1.8"
    assert "automatic_task_creation" in contract["closed_loop"]
    assert len(contract["node_types"]) >= 8
    assert workflow["approval_required"] is True
    assert workflow["nodes"][0]["type"] == "start"
    assert task["approval_required"] is True
    assert notification["default_channel"] == "in_app"
    assert feedback["learning_rule"] == "approved_results_raise_similar_advice_weight_after_review"
    assert case["knowledge_upgrade"] == "document_knowledge_base_to_enterprise_experience_base"
    assert daily["title"] == "FireFox daily business report"
    assert acceptance["workflow"] == ["call_sap", "analyze_inventory", "generate_risk", "create_task", "notify_owner", "wait_for_approval"]
    assert acceptance["execution_status"] == "waiting_for_human_approval"


def test_enterprise_v1_8_workflow_automation_docs_schema_and_boundaries_present():
    docs = [
        "docs/780_FOXBRAIN_OS_ENTERPRISE_V1_8_WORKFLOW_AUTOMATION_ENGINE.md",
        "docs/781_FOXBRAIN_OS_ENTERPRISE_V1_8_STAGE_4_WORKFLOW_RESULT.md",
        "docs/CODEX_TASKS/Task083_FoxBrain_OS_Enterprise_V1_8_Workflow_Automation_Engine.md",
    ]
    dirs = [
        "apps/api/modules/workflow/README.md",
        "apps/api/modules/task-center/README.md",
        "apps/api/modules/notification/README.md",
        "apps/api/modules/approval/README.md",
        "apps/worker/jobs/workflow-engine/README.md",
    ]
    for path in docs + dirs:
        assert (ROOT / path).exists()
    portal = read("portal_v2.py")
    for table in [
        "workflows",
        "workflow_nodes",
        "task_logs",
        "approvals",
        "ai_memory",
        "decision_feedback",
        "business_cases",
    ]:
        assert "create table if not exists " + table in portal
    combined = "\n".join(read(doc) for doc in docs + dirs)
    for phrase in [
        "V1.8",
        "Workflow",
        "AI task",
        "approval",
        "notification",
        "decision feedback",
        "business case",
        "human approval",
    ]:
        assert phrase in combined


def test_enterprise_v1_9_enterprise_knowledge_graph_module_present():
    module = read("foxbrain_os/enterprise_knowledge_graph.py")
    init_file = read("foxbrain_os/__init__.py")
    architecture = read("foxbrain_os/architecture.py")
    portal = read("portal_v2.py")
    for phrase in [
        "ENTERPRISE_ENTITY_MODELS",
        "AI_PERMISSION_ROLES",
        "V19_DATA_TABLES",
        "V19_GUARDRAILS",
        "build_enterprise_knowledge_graph_contract",
        "build_kg_builder_plan",
        "build_relationship_query_plan",
        "build_employee_fit_analysis",
        "build_ai_permission_matrix",
        "build_customer_ai_profile_contract",
        "build_employee_ai_profile_contract",
        "build_business_map_payload",
        "AI Chairman Assistant",
        "AI Customer Assistant",
        "Employee AI Assistant",
    ]:
        assert phrase in module
    assert "build_enterprise_knowledge_graph_contract" in init_file
    assert "enterprise_knowledge_graph" in architecture
    for phrase in [
        "/enterprise-knowledge-graph",
        "/api/enterprise-knowledge-graph",
        "/api/enterprise-knowledge-graph/entities",
        "/api/enterprise-knowledge-graph/graph",
        "/api/enterprise-knowledge-graph/permissions",
        "/api/enterprise-knowledge-graph/digital-employees",
        "/api/enterprise-knowledge-graph/customer-assistant",
        "/api/enterprise-knowledge-graph/employee-assistant",
        "/api/enterprise-knowledge-graph/business-map",
        "/api/enterprise-knowledge-graph/kg-builder",
        "/api/enterprise-knowledge-graph/employee-fit",
        "/api/enterprise-knowledge-graph/query",
        "enterprise_v19_enterprise_knowledge_graph",
        "ai_permissions_are_role_based_and_high_risk_actions_require_human_approval",
    ]:
        assert phrase in portal


def test_enterprise_v1_9_enterprise_knowledge_graph_imports():
    import importlib.util

    spec = importlib.util.spec_from_file_location("foxbrain_enterprise_kg", ROOT / "foxbrain_os" / "enterprise_knowledge_graph.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    contract = module.build_enterprise_knowledge_graph_contract()
    builder = module.build_kg_builder_plan()
    query = module.build_relationship_query_plan("为什么南山店Kailas销售增长？")
    inventory = module.build_relationship_query_plan("分析火狐狸未来三个月库存风险")
    fit = module.build_employee_fit_analysis("Kailas")
    permission = module.build_ai_permission_matrix("store_manager")
    customer = module.build_customer_ai_profile_contract()
    employee = module.build_employee_ai_profile_contract()
    business_map = module.build_business_map_payload()
    assert contract["ok"] is True
    assert contract["version"] == "FoxBrain OS Enterprise V1.9"
    assert "enterprise_knowledge_graph" == contract["module"]
    assert builder["schedule"] == "02:30 daily"
    assert builder["sap_writeback"] is False
    assert "Nanshan Store" in query["relationship_chain"]
    assert "SAP inventory" in inventory["relationship_chain"]
    assert fit["analysis_inputs"] == ["sales_history", "product_knowledge", "customer_feedback", "training_records"]
    assert "store_sales" in permission["data_scope"]
    assert customer["permission_rule"] == "customer_can_only_access_own_profile"
    assert employee["permission_rule"] == "employee_can_only_access_own_profile"
    assert business_map["mobile_ready"] is True


def test_enterprise_v1_9_enterprise_knowledge_graph_docs_schema_and_boundaries_present():
    docs = [
        "docs/790_FOXBRAIN_OS_ENTERPRISE_V1_9_ENTERPRISE_KNOWLEDGE_GRAPH.md",
        "docs/791_FOXBRAIN_OS_ENTERPRISE_V1_9_STAGE_2_KG_PERMISSION_RESULT.md",
        "docs/CODEX_TASKS/Task084_FoxBrain_OS_Enterprise_V1_9_Enterprise_Knowledge_Graph.md",
    ]
    dirs = [
        "apps/api/modules/knowledge-graph/README.md",
        "apps/api/modules/digital-employees/README.md",
        "apps/api/modules/permissions-ai/README.md",
        "apps/api/modules/entity-center/README.md",
        "apps/worker/jobs/kg-builder/README.md",
    ]
    for path in docs + dirs:
        assert (ROOT / path).exists()
    portal = read("portal_v2.py")
    for table in [
        "entities",
        "entity_relations",
        "knowledge_graph_nodes",
        "knowledge_graph_edges",
        "digital_employees",
        "ai_permissions",
        "employee_ai_profiles",
        "customer_ai_profiles",
        "business_relationships",
    ]:
        assert "create table if not exists " + table in portal
    combined = "\n".join(read(doc) for doc in docs + dirs)
    for phrase in [
        "V1.9",
        "Enterprise Knowledge Graph",
        "Entity Center",
        "AI Permission",
        "Employee AI Assistant",
        "Customer AI Assistant",
        "02:30 daily",
        "SAP readonly",
    ]:
        assert phrase in combined


def test_enterprise_v2_1_digital_twin_simulation_module_present():
    module = read("foxbrain_os/digital_twin_simulation.py")
    init_file = read("foxbrain_os/__init__.py")
    architecture = read("foxbrain_os/architecture.py")
    portal = read("portal_v2.py")
    for phrase in [
        "DIGITAL_TWIN_MODELS",
        "SCENARIO_TYPES",
        "V21_DATA_TABLES",
        "V21_GUARDRAILS",
        "build_digital_twin_simulation_contract",
        "build_company_twin_model",
        "build_discount_adjustment_scenario",
        "build_new_store_scenario",
        "build_brand_mix_scenario",
        "build_cashflow_forecast",
        "build_inventory_twin_forecast",
        "build_employee_twin_model",
        "build_strategy_agent_report",
        "build_board_assistant_pack",
        "AI Board Assistant",
        "Future Order Pickup",
    ]:
        assert phrase in module
    assert "build_digital_twin_simulation_contract" in init_file
    assert "digital_twin_simulation" in architecture
    for phrase in [
        "/ai-strategy-center",
        "/api/v2.1",
        "/api/v2.1/digital-twin",
        "/api/v2.1/scenario/osprey-discount",
        "/api/v2.1/scenario/new-store",
        "/api/v2.1/scenario/brand-mix",
        "/api/v2.1/cashflow/forecast",
        "/api/v2.1/inventory/forecast",
        "/api/v2.1/strategy/report",
        "v21_strategy_payload",
        "persist_v21_simulation",
        "create_v21_strategy_report",
        "enterprise_v21_digital_twin_simulation",
        "simulation_outputs_are_sandboxed_and_execution_requires_human_approval",
    ]:
        assert phrase in portal


def test_enterprise_v2_1_digital_twin_simulation_imports():
    import importlib.util

    spec = importlib.util.spec_from_file_location("foxbrain_v21_twin", ROOT / "foxbrain_os" / "digital_twin_simulation.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    contract = module.build_digital_twin_simulation_contract()
    company = module.build_company_twin_model({"month_sales": 100})
    discount = module.build_discount_adjustment_scenario("Osprey", 0.62, 0.59)
    store = module.build_new_store_scenario()
    brand = module.build_brand_mix_scenario("legacy", "VAFOX")
    cash = module.build_cashflow_forecast(90)
    inventory = module.build_inventory_twin_forecast(60)
    employee = module.build_employee_twin_model()
    report = module.build_strategy_agent_report("今年300万Osprey期货是否应该全部提货？")
    board = module.build_board_assistant_pack()
    assert contract["ok"] is True
    assert contract["version"] == "FoxBrain OS Enterprise V2.1"
    assert "model_adjustment" in contract["simulation_feedback_loop"]
    assert company["sandbox_rule"] == "read_only_twin_simulation_never_modifies_business_data"
    assert discount["approval_required"] is True
    assert store["forecast"]["year_2"] == "break_even_expected"
    assert brand["approval_required"] is True
    assert cash["periods"] == [30, 90, 180]
    assert "shortage_risk" in inventory["outputs"]
    assert "sales_ability" in employee["dimensions"]
    assert report["required_reads"] == ["historical_sales", "inventory", "price_system", "hong_kong_price", "brand_risk", "cashflow", "rebate"]
    assert report["output"] == ["pickup_ratio", "risk", "sales_plan", "cash_arrangement"]
    assert board["assistant"] == "AI Board Assistant"


def test_enterprise_v2_1_digital_twin_simulation_docs_schema_and_boundaries_present():
    docs = [
        "docs/810_FOXBRAIN_OS_ENTERPRISE_V2_1_DIGITAL_TWIN_SIMULATION.md",
        "docs/811_FOXBRAIN_OS_ENTERPRISE_V2_1_STAGE_5_SIMULATION_RESULT.md",
        "docs/CODEX_TASKS/Task085_FoxBrain_OS_Enterprise_V2_1_Digital_Twin_Simulation.md",
    ]
    dirs = [
        "apps/api/modules/digital-twin/README.md",
        "apps/api/modules/business-simulator/README.md",
        "apps/api/modules/scenario-engine/README.md",
        "apps/api/modules/prediction-engine/README.md",
        "apps/worker/jobs/simulation/README.md",
    ]
    for path in docs + dirs:
        assert (ROOT / path).exists()
    portal = read("portal_v2.py")
    for table in [
        "digital_twin_models",
        "business_scenarios",
        "simulation_results",
        "strategy_reports",
        "cashflow_forecasts",
        "store_models",
        "employee_models",
        "investment_models",
    ]:
        assert "create table if not exists " + table in portal
    combined = "\n".join(read(doc) for doc in docs + dirs)
    for phrase in [
        "V2.1",
        "Digital Twin",
        "Business Simulator",
        "Scenario Engine",
        "Prediction Engine",
        "cashflow",
        "inventory",
        "human approval",
    ]:
        assert phrase in combined


def test_enterprise_v2_2_business_autopilot_module_present():
    module = read("foxbrain_os/business_autopilot.py")
    init_file = read("foxbrain_os/__init__.py")
    architecture = read("foxbrain_os/architecture.py")
    portal = read("portal_v2.py")
    for phrase in [
        "BUSINESS_HEALTH_DIMENSIONS",
        "AUTOPILOT_JOBS",
        "V22_DATA_TABLES",
        "V22_GUARDRAILS",
        "build_business_autopilot_contract",
        "calculate_business_health_score",
        "build_daily_inspection_plan",
        "build_early_warning_forecast",
        "build_action_plan",
        "build_ceo_dashboard_payload",
        "build_rule_evolution_plan",
        "build_learning_record_template",
        "build_chairman_agent_brief",
        "build_biggest_risk_analysis",
        "Chairman Agent",
        "Early Warning Engine",
    ]:
        assert phrase in module
    assert "build_business_autopilot_contract" in init_file
    assert "business_autopilot" in architecture
    for phrase in [
        "/business-autopilot",
        "/api/v2.2",
        "/api/v2.2/health-score",
        "/api/v2.2/inspection/daily",
        "/api/v2.2/alerts",
        "/api/v2.2/actions",
        "/api/v2.2/ceo-dashboard",
        "/api/v2.2/learning",
        "/api/v2.2/rules/evolution",
        "/api/v2.2/chairman-agent",
        "/api/v2.2/risk/biggest",
        "v22_autopilot_payload",
        "run_v22_risk_scan",
        "enterprise_v22_business_autopilot",
        "autopilot_creates_alerts_tasks_and_reports_but_high_risk_execution_requires_human_approval",
    ]:
        assert phrase in portal


def test_enterprise_v2_2_business_autopilot_imports():
    import importlib.util

    spec = importlib.util.spec_from_file_location("foxbrain_v22_autopilot", ROOT / "foxbrain_os" / "business_autopilot.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    contract = module.build_business_autopilot_contract()
    health = module.calculate_business_health_score({"month_sales": 100, "gross_margin": 30, "risk_count": 8})
    inspection = module.build_daily_inspection_plan()
    warning = module.build_early_warning_forecast()
    action = module.build_action_plan()
    ceo = module.build_ceo_dashboard_payload()
    rule = module.build_rule_evolution_plan()
    learning = module.build_learning_record_template()
    chairman = module.build_chairman_agent_brief()
    risk = module.build_biggest_risk_analysis()
    assert contract["ok"] is True
    assert contract["version"] == "FoxBrain OS Enterprise V2.2"
    assert "detect_anomaly" in contract["flow"]
    assert health["score"] > 0
    assert inspection["schedule"] == "06:00 daily"
    assert warning["periods"] == [7, 30, 90]
    assert action["task"]["due_days"] == 7
    assert len(ceo["top_10_metrics"]) == 10
    assert rule["purchase_weights"] == {"sales": 30, "inventory": 30, "brand_value": 20, "market_trend": 20}
    assert "Osprey price adjustment" in learning["case_library"]
    assert chairman["agent"] == "Chairman Agent"
    assert risk["required_calls"] == ["SAP", "knowledge_graph", "digital_twin", "historical_cases", "market_research"]
    assert len(risk["top_5_risks"]) == 5


def test_enterprise_v2_2_business_autopilot_docs_schema_and_boundaries_present():
    docs = [
        "docs/820_FOXBRAIN_OS_ENTERPRISE_V2_2_BUSINESS_AUTOPILOT.md",
        "docs/821_FOXBRAIN_OS_ENTERPRISE_V2_2_STAGE_6_AUTOPILOT_RESULT.md",
        "docs/CODEX_TASKS/Task086_FoxBrain_OS_Enterprise_V2_2_Business_Autopilot.md",
    ]
    dirs = [
        "apps/api/modules/autopilot/README.md",
        "apps/api/modules/business-monitor/README.md",
        "apps/api/modules/alert-center/README.md",
        "apps/api/modules/action-engine/README.md",
        "apps/api/modules/self-learning/README.md",
        "apps/worker/jobs/autonomous-operation/README.md",
    ]
    for path in docs + dirs:
        assert (ROOT / path).exists()
    portal = read("portal_v2.py")
    for table in [
        "business_health_scores",
        "monitor_rules",
        "business_alerts",
        "action_tasks",
        "action_results",
        "ai_learning_records",
        "rule_evolution",
        "ceo_daily_reports",
    ]:
        assert "create table if not exists " + table in portal
    combined = "\n".join(read(doc) for doc in docs + dirs)
    for phrase in [
        "V2.2",
        "Business Autopilot",
        "Business Health Score",
        "Daily Inspection",
        "Action Engine",
        "Chairman Agent",
        "human approval",
        "continuous learning",
    ]:
        assert phrase in combined


def test_enterprise_v2_3_ecosystem_hub_module_present():
    module = read("foxbrain_os/ecosystem_integration_hub.py")
    init_file = read("foxbrain_os/__init__.py")
    architecture = read("foxbrain_os/architecture.py")
    portal = read("portal_v2.py")
    for phrase in [
        "ECOSYSTEM_CONNECTORS",
        "V23_DATA_TABLES",
        "V23_GUARDRAILS",
        "build_ecosystem_hub_contract",
        "build_enterprise_data_lake_plan",
        "build_wecom_crm_agent",
        "build_crm_manager_plan",
        "build_ecommerce_connector_plan",
        "build_content_factory_plan",
        "build_api_gateway_plan",
        "build_omnichannel_analysis",
        "build_vip_recall_workflow",
        "WeCom CRM Agent",
        "AI Content Factory",
    ]:
        assert phrase in module
    assert "build_ecosystem_hub_contract" in init_file
    assert "enterprise_ecosystem_hub" in architecture
    for phrase in [
        "/ecosystem-hub",
        "/api/v2.3",
        "/api/v2.3/data-lake",
        "/api/v2.3/wecom",
        "/api/v2.3/crm",
        "/api/v2.3/ecommerce",
        "/api/v2.3/content-factory",
        "/api/v2.3/api-gateway",
        "/api/v2.3/omnichannel-analysis",
        "/api/v2.3/churn-recall",
        "/api/v2.3/integration-logs",
        "v23_ecosystem_payload",
        "run_v23_churn_recall",
        "enterprise_v23_ecosystem_hub",
        "external_channel_execution_and_api_permission_changes_require_human_approval",
    ]:
        assert phrase in portal


def test_enterprise_v2_3_ecosystem_hub_imports():
    import importlib.util

    spec = importlib.util.spec_from_file_location("foxbrain_v23_ecosystem", ROOT / "foxbrain_os" / "ecosystem_integration_hub.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    contract = module.build_ecosystem_hub_contract()
    lake = module.build_enterprise_data_lake_plan()
    wecom = module.build_wecom_crm_agent()
    crm = module.build_crm_manager_plan()
    ecommerce = module.build_ecommerce_connector_plan()
    content = module.build_content_factory_plan()
    gateway = module.build_api_gateway_plan()
    churn = module.build_omnichannel_analysis("找出最近90天流失风险最高的100个客户，并制定召回方案。")
    workflow = module.build_vip_recall_workflow()
    assert contract["ok"] is True
    assert contract["version"] == "FoxBrain OS Enterprise V2.3"
    assert "channel_execution" in contract["closed_loop"]
    assert len(lake["sync_jobs"]) == 5
    assert wecom["agent"] == "WeCom CRM Agent"
    assert "churn_risk_customer" in crm["lifecycle"]
    assert "Tmall" in ecommerce["platforms"]
    assert content["factory"] == "AI Content Factory"
    assert "call_logs" in gateway["capabilities"]
    assert churn["required_calls"] == ["SAP purchase records", "CRM members", "WeCom interactions", "product preferences", "campaign records"]
    assert workflow["external_send_requires_approval"] is True


def test_enterprise_v2_3_ecosystem_hub_docs_schema_and_boundaries_present():
    docs = [
        "docs/830_FOXBRAIN_OS_ENTERPRISE_V2_3_ECOSYSTEM_HUB.md",
        "docs/831_FOXBRAIN_OS_ENTERPRISE_V2_3_STAGE_7_ECOSYSTEM_RESULT.md",
        "docs/CODEX_TASKS/Task087_FoxBrain_OS_Enterprise_V2_3_Ecosystem_Hub.md",
    ]
    dirs = [
        "apps/api/modules/ecosystem/README.md",
        "apps/api/modules/crm-connect/README.md",
        "apps/api/modules/wecom/README.md",
        "apps/api/modules/ecommerce/README.md",
        "apps/api/modules/content-center/README.md",
        "apps/api/modules/api-gateway/README.md",
        "apps/worker/jobs/ecosystem-sync/README.md",
    ]
    for path in docs + dirs:
        assert (ROOT / path).exists()
    portal = read("portal_v2.py")
    for table in [
        "data_sources",
        "sync_jobs",
        "customer_profiles",
        "customer_tags",
        "customer_events",
        "channel_orders",
        "content_assets",
        "integration_logs",
    ]:
        assert "create table if not exists " + table in portal
    combined = "\n".join(read(doc) for doc in docs + dirs)
    for phrase in [
        "V2.3",
        "Ecosystem Hub",
        "Enterprise WeChat",
        "Member CRM",
        "Ecommerce",
        "AI Content Factory",
        "API Gateway",
        "approval",
    ]:
        assert phrase in combined


def test_foxbrain_os_ux_2_information_architecture_module_present():
    module = read("foxbrain_os/ux_information_architecture.py")
    init_file = read("foxbrain_os/__init__.py")
    architecture = read("foxbrain_os/architecture.py")
    portal = read("portal_v2.py")
    for phrase in [
        "UX_NAVIGATION_LAYERS",
        "UX_PRINCIPLES",
        "build_ux_information_architecture_contract",
        "FoxBrain OS UX 2.0",
        "Apple Experience Edition",
        "first_layer_four_entries_only_no_repeated_business_content",
        "fixed_global_search_fixed_ai_entry_mobile_bottom_navigation_and_no_home_small_text",
        "home_has_no_explanatory_small_text",
        "global_search_is_fixed",
        "mobile_bottom_navigation",
        "details_only_after_click_through",
    ]:
        assert phrase in module
    assert "build_ux_information_architecture_contract" in init_file
    assert "ux_information_architecture" in architecture
    for phrase in [
        "/api/ux",
        "/api/ux/information-architecture",
        "/api/ux/v2",
        "/os/business",
        "/os/ai",
        "/os/messages",
        "/os/me",
        "/os/search",
        "os_global_search",
        "global-search",
        "bottom-nav",
        "os_business_layer",
        "os_ai_layer",
        "os_messages_layer",
        "os_me_layer",
        "api_ux_get",
    ]:
        assert phrase in portal
    final_dashboard = portal.rsplit("def dashboard(self, user):", 1)[1].split("def os_layer_cards", 1)[0]
    for phrase in ["/owner/enterprise", "/owner/assets", "/owner/archive", "/drive", "/jarvis", "/owner/decision", "/owner/data", "/owner/projects", "/owner/strategy", "/owner/system"]:
        assert phrase in final_dashboard
    assert "small" not in final_dashboard
    assert "first_layer" not in final_dashboard
    for phrase in ["/os/business", "/os/ai", "/os/messages", "/os/me", "/business-radar", "/enterprise-ai-platform", "/business-autopilot", "/ecosystem-hub"]:
        assert phrase not in final_dashboard


def test_foxbrain_os_ux_2_information_architecture_imports():
    import importlib.util

    spec = importlib.util.spec_from_file_location("foxbrain_ux_2", ROOT / "foxbrain_os" / "ux_information_architecture.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    contract = module.build_ux_information_architecture_contract()
    assert contract["ok"] is True
    assert contract["version"] == "FoxBrain OS UX 2.0"
    assert contract["codename"] == "Apple Experience Edition"
    assert contract["recommended_structure"]["home"] == ["Business", "AI", "Messages", "Me"]
    assert contract["principles"]["one_page_one_subject"] is True
    assert contract["principles"]["find_anything_within_three_steps"] is True
    assert contract["principles"]["home_has_no_explanatory_small_text"] is True
    assert contract["principles"]["global_search_is_fixed"] is True
    assert contract["principles"]["ai_entry_is_fixed"] is True
    assert contract["fixed_entries"]["global_search"] == "/os/search"
    assert contract["fixed_entries"]["mobile_bottom_nav"] == ["/os/business", "/os/ai", "/os/messages", "/os/me"]
    assert len(contract["layers"]) == 4
    assert max(layer["max_entries"] for layer in contract["layers"]) <= 8


def test_foxbrain_owner_os_v1_foundation_module_present():
    module = read("foxbrain_os/owner_os_foundation.py")
    init_file = read("foxbrain_os/__init__.py")
    architecture = read("foxbrain_os/architecture.py")
    portal = read("portal_v2.py")
    for phrase in [
        "FoxBrain Owner OS V1 Foundation",
        "OWNER_HOME_ENTRIES",
        "OWNER_OS_CENTERS",
        "BLUEPRINT_DOCUMENTS",
        "OWNER_OS_PRODUCT_PRINCIPLES",
        "OWNER_OS_V1_BLUEPRINT_SECTIONS",
        "OWNER_OS_V1_DELIVERY_PLAN",
        "SAP_INDEPENDENCE_PRINCIPLES",
        "build_owner_home_contract",
        "build_master_blueprint_contract",
        "build_owner_os_foundation_contract",
        "System of Record",
        "System of Intelligence",
        "System of Execution",
    ]:
        assert phrase in module
    assert "build_owner_os_foundation_contract" in init_file
    assert "owner_os_foundation" in architecture
    for phrase in [
        "/api/owner-os",
        "/api/owner-os/home",
        "/api/owner-os/master-blueprint",
        "/api/owner-os/product-principles",
        "/api/owner-os/v1-blueprint",
        "/api/owner-os/delivery-plan",
        "/owner/enterprise",
        "/owner/assets",
        "/owner/archive",
        "/owner/knowledge",
        "/owner/decision",
        "/owner/data",
        "/owner/projects",
        "/owner/strategy",
        "/owner/system",
        "owner_os_center_page",
        "api_owner_os_get",
    ]:
        assert phrase in portal


def test_foxbrain_owner_os_v1_foundation_imports():
    import importlib.util

    spec = importlib.util.spec_from_file_location("owner_os_foundation", ROOT / "foxbrain_os" / "owner_os_foundation.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    contract = module.build_owner_os_foundation_contract()
    home = module.build_owner_home_contract()
    blueprint = module.build_master_blueprint_contract()
    assert contract["ok"] is True
    assert contract["version"] == "FoxBrain Owner OS V1 Foundation"
    assert contract["domain"] == "huyan.vafox.com"
    assert contract["pause_enterprise_os_until_owner_os_foundation_ready"] is True
    assert contract["relationship"] == {
        "sap": "System of Record",
        "owner_os": "System of Intelligence",
        "enterprise_os": "System of Execution",
    }
    assert contract["sap_principles"]["sap_stays_independent_server"] is True
    assert contract["sap_principles"]["no_ai_installed_on_sap"] is True
    assert contract["sap_principles"]["sap_writeback_requires_human_approval"] is True
    assert contract["current_priority"] == "complete_master_blueprint_v1_before_more_feature_pages"
    assert len(home["home_entries"]) == 10
    assert [item["route"] for item in home["home_entries"]] == [
        "/owner/enterprise",
        "/owner/assets",
        "/owner/archive",
        "/owner/knowledge",
        "/jarvis",
        "/owner/decision",
        "/owner/data",
        "/owner/projects",
        "/owner/strategy",
        "/owner/system",
    ]
    assert blueprint["name"] == "FoxBrain Master Blueprint"
    assert blueprint["version"] == "Owner OS V1.0"
    assert len(blueprint["documents"]) == 4
    assert blueprint["product_principles"]["not_erp"].startswith("Owner OS does not create")
    assert blueprint["product_principles"]["not_oa"].startswith("Employee approvals")
    assert len(blueprint["v1_blueprint_sections"]) == 9
    assert len(blueprint["delivery_plan"]) == 5


def test_foxbrain_owner_os_v1_foundation_docs_present():
    docs = [
        ROOT / "docs" / "860_FOXBRAIN_OWNER_OS_V1_FOUNDATION.md",
        ROOT / "docs" / "861_FOXBRAIN_OWNER_OS_V1_FOUNDATION_STAGE_RESULT.md",
        ROOT / "docs" / "870_FOXBRAIN_OWNER_OS_V1_0_MASTER_BLUEPRINT.md",
        ROOT / "docs" / "871_FOXBRAIN_OWNER_OS_V1_0_STAGE_BLUEPRINT_RESULT.md",
        ROOT / "docs" / "CODEX_TASKS" / "Task090_FoxBrain_Owner_OS_V1_Foundation.md",
        ROOT / "docs" / "CODEX_TASKS" / "Task091_FoxBrain_Owner_OS_V1_0_Master_Blueprint.md",
    ]
    for path in docs:
        assert path.exists()
    combined = "\n".join(path.read_text(encoding="utf-8") for path in docs)
    for phrase in [
        "FoxBrain Owner OS V1 Foundation",
        "enterprise second brain",
        "System of Intelligence",
        "Master Blueprint",
        "Product Constitution",
        "Technical Architecture",
        "Development Handbook",
        "SAP remains the independent",
        "human approval",
        "ten fixed",
        "Owner OS is not ERP",
        "Owner OS is not OA",
    ]:
        assert phrase in combined


def test_foxbrain_os_ux_2_docs_present():
    docs = [
        "docs/840_FOXBRAIN_OS_UX_2_0_APPLE_EXPERIENCE_EDITION.md",
        "docs/841_FOXBRAIN_OS_UX_2_0_STAGE_IA_RESULT.md",
        "docs/CODEX_TASKS/Task088_FoxBrain_OS_UX_2_0_Information_Architecture.md",
    ]
    for path in docs:
        assert (ROOT / path).exists()
    combined = "\n".join(read(doc) for doc in docs)
    for phrase in [
        "FoxBrain OS UX 2.0",
        "Apple Experience Edition",
        "one page one subject",
        "four first-layer entries",
        "Business",
        "AI",
        "Messages",
        "Me",
        "three steps",
        "global search",
        "fixed AI",
        "mobile bottom navigation",
        "explanatory small text",
        "home page",
    ]:
        assert phrase in combined


def test_foxbrain_owner_enterprise_7_9_module_present():
    module = read("foxbrain_os/owner_enterprise_planning.py")
    init_file = read("foxbrain_os/__init__.py")
    architecture = read("foxbrain_os/architecture.py")
    portal = read("portal_v2.py")
    for phrase in [
        "OWNER_ENTERPRISE_SYSTEMS",
        "SYNC_ALLOWED_DOMAINS",
        "SYNC_BLOCKED_DOMAINS",
        "ROLE_BOUNDARIES",
        "build_owner_enterprise_planning_contract",
        "build_sync_policy",
        "classify_data_domain",
        "FoxBrain Owner OS",
        "FoxBrain Enterprise OS",
        "personal_capital",
        "core_contract_original_files",
    ]:
        assert phrase in module
    assert "build_owner_enterprise_planning_contract" in init_file
    assert "owner_enterprise_planning" in architecture
    for phrase in [
        "/owner-enterprise-plan",
        "/api/owner-enterprise",
        "/api/owner-enterprise/sync-policy",
        "/api/owner-enterprise/classify",
        "owner_enterprise_plan",
        "api_owner_enterprise_get",
    ]:
        assert phrase in portal


def test_foxbrain_owner_enterprise_7_9_imports_and_boundaries():
    import importlib.util

    spec = importlib.util.spec_from_file_location("foxbrain_owner_enterprise_79", ROOT / "foxbrain_os" / "owner_enterprise_planning.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    contract = module.build_owner_enterprise_planning_contract()
    sync_policy = module.build_sync_policy()
    stores = module.classify_data_domain("stores")
    blocked = module.classify_data_domain("personal_capital")
    unknown = module.classify_data_domain("unknown_secret")
    assert contract["ok"] is True
    assert contract["version"] == "FoxBrain Owner/Enterprise OS 7.9"
    assert contract["conclusion"]["huyan.vafox.com"] == "FoxBrain Owner OS"
    assert contract["conclusion"]["ai.vafox.com"] == "FoxBrain Enterprise OS"
    assert sync_policy["rules"]["not_fully_connected"] is True
    assert sync_policy["rules"]["sensitive_owner_data_never_syncs_to_employee_system"] is True
    assert stores["sync_allowed"] is True
    assert blocked["sync_allowed"] is False
    assert blocked["policy"] == "blocked_never_sync_between_owner_and_enterprise"
    assert unknown["policy"] == "unknown_domain_requires_architecture_review"


def test_foxbrain_owner_enterprise_7_9_docs_present():
    docs = [
        "docs/850_FOXBRAIN_OWNER_ENTERPRISE_OS_7_9_PLANNING.md",
        "docs/851_FOXBRAIN_OWNER_ENTERPRISE_OS_7_9_STAGE_RESULT.md",
        "docs/CODEX_TASKS/Task089_FoxBrain_Owner_Enterprise_OS_7_9_Planning.md",
    ]
    for path in docs:
        assert (ROOT / path).exists()
    combined = "\n".join(read(doc) for doc in docs)
    for phrase in [
        "FoxBrain Owner OS",
        "FoxBrain Enterprise OS",
        "huyan.vafox.com",
        "ai.vafox.com",
        "partial synchronization",
        "Sensitive owner data never syncs",
        "SAP remains the independent",
        "data middle platform",
        "human approval",
    ]:
        assert phrase in combined


def test_foxbrain_enterprise_second_brain_module_present():
    module = read("foxbrain_os/enterprise_second_brain.py")
    init_file = read("foxbrain_os/__init__.py")
    architecture = read("foxbrain_os/architecture.py")
    portal = read("portal_v2.py")
    for phrase in [
        "FoxBrain Enterprise Second Brain V1.0",
        "SECOND_BRAIN_PRINCIPLES",
        "SECOND_BRAIN_ENGINES",
        "PRODUCT_SPEC_BOOKS",
        "build_enterprise_second_brain_contract",
        "Object Engine",
        "Knowledge Engine",
        "Memory Engine",
        "Decision Engine",
        "Relationship Engine",
    ]:
        assert phrase in module
    assert "build_enterprise_second_brain_contract" in init_file
    assert "enterprise_second_brain" in architecture
    for phrase in [
        "/second-brain",
        "/api/second-brain",
        "/api/second-brain/books",
        "/api/second-brain/engines",
        "/api/second-brain/roadmap",
        "enterprise_second_brain_page",
        "api_second_brain_get",
    ]:
        assert phrase in portal


def test_foxbrain_enterprise_second_brain_imports():
    import importlib.util

    spec = importlib.util.spec_from_file_location("foxbrain_second_brain", ROOT / "foxbrain_os" / "enterprise_second_brain.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    contract = module.build_enterprise_second_brain_contract()
    assert contract["ok"] is True
    assert contract["version"] == "FoxBrain Enterprise Second Brain V1.0"
    assert contract["positioning"] == "Enterprise AI Operating System"
    assert "ERP" in contract["not"]
    assert len(contract["product_spec_books"]) == 12
    assert len(contract["engines"]) == 5
    assert contract["principles"]["design_first_then_build"].startswith("Every feature")
    assert contract["roadmap"][0]["name"] == "Enterprise Second Brain"
    assert contract["firefox_landing_route"]["production_system"].startswith("SAP Business One")


def test_foxbrain_enterprise_second_brain_docs_present():
    docs = [
        "docs/880_FOXBRAIN_ENTERPRISE_SECOND_BRAIN_V1_0.md",
        "docs/881_FOXBRAIN_ENTERPRISE_SECOND_BRAIN_V1_0_STAGE_RESULT.md",
        "docs/CODEX_TASKS/Task092_FoxBrain_Enterprise_Second_Brain_V1_0.md",
    ]
    for path in docs:
        assert (ROOT / path).exists()
    combined = "\n".join(read(doc) for doc in docs)
    for phrase in [
        "FoxBrain Enterprise Second Brain V1.0",
        "Enterprise AI Operating System",
        "Object Engine",
        "Knowledge Engine",
        "Memory Engine",
        "Decision Engine",
        "Relationship Engine",
        "Product Constitution",
        "SAP Business One remains",
        "high-risk AI actions",
    ]:
        assert phrase in combined


def test_foxbrain_enterprise_second_brain_v11_module_present():
    module = read("foxbrain_os/enterprise_second_brain_v11.py")
    init_file = read("foxbrain_os/__init__.py")
    architecture = read("foxbrain_os/architecture.py")
    portal = read("portal_v2.py")
    for phrase in [
        "FoxBrain Enterprise Second Brain V1.1",
        "DRIVE_2_DOMAINS",
        "OBJECT_ENGINE_MODELS",
        "KNOWLEDGE_PIPELINE_STAGES",
        "CEO_HOME_V11_SECTIONS",
        "build_drive_2_contract",
        "build_object_engine_contract",
        "build_knowledge_pipeline_contract",
        "build_ceo_home_v11_contract",
        "Enterprise Knowledge Drive",
    ]:
        assert phrase in module
    assert "build_enterprise_second_brain_v11_contract" in init_file
    assert "enterprise_second_brain_v11" in architecture
    for phrase in [
        "/drive",
        "/objects",
        "/knowledge-pipeline",
        "/ceo-home",
        "/api/drive/v2",
        "/api/object-engine",
        "/api/knowledge-pipeline",
        "/api/ceo-home",
        "drive_2_page",
        "object_engine_page",
        "knowledge_pipeline_page",
        "ceo_home_v11_page",
        "FoxBrain CEO Home",
        "root_home_keeps_ten_entries_only_details_after_click",
    ]:
        assert phrase in portal


def test_foxbrain_enterprise_second_brain_v11_imports():
    import importlib.util

    spec = importlib.util.spec_from_file_location("foxbrain_second_brain_v11", ROOT / "foxbrain_os" / "enterprise_second_brain_v11.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    contract = module.build_enterprise_second_brain_v11_contract()
    assert contract["ok"] is True
    assert contract["version"] == "FoxBrain Enterprise Second Brain V1.1"
    assert "Drive 2.0" in contract["focus"]
    assert contract["drive_2"]["positioning"] == "Enterprise Knowledge Drive"
    assert len(contract["drive_2"]["domains"]) == 5
    assert len(contract["object_engine"]["models"]) >= 7
    assert contract["knowledge_pipeline"]["flow"] == ["Document", "OCR", "Chunk", "Embedding", "Vector DB", "Graph", "AI Summary", "Knowledge Object", "Agent"]
    assert contract["ceo_home"]["homepage_policy"] == "root_home_keeps_ten_entries_only_details_after_click"
    assert contract["guardrails"]["sap_remains_system_of_record"] is True
    assert contract["guardrails"]["high_risk_actions_require_human_approval"] is True


def test_foxbrain_enterprise_second_brain_v11_docs_present():
    docs = [
        "docs/882_FOXBRAIN_ENTERPRISE_SECOND_BRAIN_V1_1.md",
        "docs/883_FOXBRAIN_ENTERPRISE_SECOND_BRAIN_V1_1_STAGE_RESULT.md",
        "docs/CODEX_TASKS/Task093_FoxBrain_Enterprise_Second_Brain_V1_1.md",
    ]
    for path in docs:
        assert (ROOT / path).exists()
    combined = "\n".join(read(doc) for doc in docs)
    for phrase in [
        "FoxBrain Enterprise Second Brain V1.1",
        "Drive 2.0",
        "Object Engine",
        "Knowledge Pipeline",
        "CEO Home",
        "Document",
        "OCR",
        "Embedding",
        "Vector DB",
        "Knowledge Object",
        "SAP remains the system of record",
    ]:
        assert phrase in combined


def test_sprint001_drive_foundation_schema_routes_and_api_present():
    portal = read("portal_v2.py")
    for phrase in [
        "create table if not exists documents",
        'ensure_column(conn, "documents", col, ddl)',
        '("filename", "filename text")',
        '("original_filename", "original_filename text")',
        '("storage_path", "storage_path text")',
        '("mime_type", "mime_type text")',
        '("extension", "extension text")',
        '("size_bytes", "size_bytes integer not null default 0")',
        '("category", "category text not null default',
        '("processing_status", "processing_status text not null default',
        '("ai_summary", "ai_summary text")',
        '("extracted_text", "extracted_text text")',
        '("related_object_type", "related_object_type text")',
        '("related_object_id", "related_object_id integer")',
        '("version", "version integer not null default 1")',
        '("deleted_at", "deleted_at integer")',
        "drive_categories",
        "drive_supported_extensions",
        "drive_extract_text",
        "drive_generate_summary",
        "drive_generate_tags",
        "drive_classify_file",
        "drive_link_to_object",
        "document_to_json",
    ]:
        assert phrase in portal
    for phrase in [
        'if path == "/drive"',
        "/api/drive/upload",
        "/api/drive/files",
        "/api/drive/files/{}",
        "/api/drive/files/{}/download",
        "/api/drive/files/{}/reprocess",
        "/api/drive/categories",
        "def api_drive_get",
        "def api_drive_post",
        "def api_drive_upload",
        "def api_drive_delete",
        "def do_PATCH",
        "def do_DELETE",
    ]:
        assert phrase in portal


def test_sprint001_drive_home_keeps_ten_entries_and_opens_drive():
    portal = read("portal_v2.py")
    final_dashboard_start = portal.rindex("    def dashboard(self, user):")
    final_dashboard_end = portal.index("    def os_layer_cards(self, items):", final_dashboard_start)
    final_dashboard = portal[final_dashboard_start:final_dashboard_end]
    assert '"/drive"' in final_dashboard
    assert '"/owner/knowledge"' not in final_dashboard
    assert "minimal_links" in final_dashboard
    assert "FoxBrain CEO Home" in final_dashboard


def test_sprint001_docs_and_summary_present():
    docs = [
        "docs/MASTER_PLAN.md",
        "sprints/Sprint001_FoxBrain_Drive_Foundation.md",
        "docs/884_SPRINT001_FOXBRAIN_DRIVE_FOUNDATION_SUMMARY.md",
    ]
    for path in docs:
        assert (ROOT / path).exists()
    combined = "\n".join(read(doc) for doc in docs)
    for phrase in [
        "FoxBrain Drive Foundation",
        "POST /api/drive/upload",
        "GET /api/drive/files",
        "DELETE /api/drive/files/:id",
        "PATCH /api/drive/files/:id",
        "documents",
        "processing_status",
        "No existing data is deleted",
        "Sprint002 should implement Object Engine",
    ]:
        assert phrase in combined


def test_sprint002_object_engine_schema_routes_and_api_present():
    portal = read("portal_v2.py")
    for phrase in [
        "create table if not exists enterprise_objects",
        "create table if not exists object_relations",
        "idx_enterprise_objects_type_status",
        "idx_object_relations_source",
        "related_object_type",
        "related_object_id",
        "def object_types",
        "def object_templates",
        "def generateObjectSummary",
        "def suggestRelations",
        "def object_timeline_placeholder",
        "def enterprise_object_to_json",
    ]:
        assert phrase in portal
    for phrase in [
        'if path in ("/object-center", "/objects")',
        'path.startswith("/api/objects") or path == "/api/object-types"',
        "def api_objects_get",
        "def api_objects_post",
        "def api_objects_delete",
        "/api/object-types",
        "/api/objects/link-document",
        "/api/objects/{}/documents/link",
    ]:
        assert phrase in portal


def test_sprint002_object_engine_required_types_and_templates_present():
    portal = read("portal_v2.py")
    for phrase in [
        '"key": "store"',
        '"key": "employee"',
        '"key": "brand"',
        '"key": "product"',
        '"key": "supplier"',
        '"key": "customer"',
        '"key": "contract"',
        '"key": "project"',
        '"key": "meeting"',
        '"key": "task"',
        '"store": ["address", "area", "opening_date", "rent", "manager", "phone"]',
        '"employee": ["role", "store", "join_date", "phone", "status"]',
        '"brand": ["brand_origin", "supplier", "website", "positioning", "main_categories"]',
        '"product": ["brand", "sku", "category", "season", "barcode"]',
        '"supplier": ["contact_person", "phone", "wechat", "payment_terms"]',
        '"customer": ["phone", "wechat", "level", "source"]',
    ]:
        assert phrase in portal


def test_sprint002_drive_object_linking_and_summary_present():
    portal = read("portal_v2.py")
    summary = read("SPRINT002_OBJECT_ENGINE_SUMMARY.md")
    for phrase in [
        'select id,object_type,name from enterprise_objects',
        'name="related_object_ref"',
        "/api/objects/link-document",
        "link_document_to_object",
        "unlink_document_from_object",
        "update documents set related_object_type=?",
        "/object-center",
    ]:
        assert phrase in portal
    for phrase in [
        "Sprint002 Object Engine Summary",
        "enterprise_objects",
        "object_relations",
        "GET /api/objects",
        "POST /api/objects",
        "PATCH /api/objects/:id",
        "DELETE /api/objects/:id",
        "Drive-to-object links",
        "Sprint003",
    ]:
        assert phrase in summary


def test_sprint003_knowledge_pipeline_schema_and_helpers_present():
    portal = read("portal_v2.py")
    for phrase in [
        "create table if not exists document_chunks",
        'ensure_column(conn, "knowledge_items", "document_id", "document_id integer")',
        'ensure_column(conn, "knowledge_items", "content", "content text")',
        'ensure_column(conn, "knowledge_items", "source_path", "source_path text")',
        'ensure_column(conn, "knowledge_items", "chunk_index", "chunk_index integer")',
        'ensure_column(conn, "knowledge_items", "confidence", "confidence real not null default 0")',
        '("processing_error", "processing_error text")',
        "knowledge_pipeline_chunks",
        "document_knowledge_metrics",
        "process_document_to_knowledge",
        "embedding_status",
    ]:
        assert phrase in portal


def test_sprint003_knowledge_pipeline_routes_and_drive_integration_present():
    portal = read("portal_v2.py")
    for phrase in [
        "/api/knowledge/process-document/",
        "/api/knowledge/items",
        "/api/knowledge/search",
        "/api/documents",
        "def api_documents_get",
        "def api_documents_post",
        r"^/api/documents/(\d+)/chunks$",
        "knowledge_processing",
        "self.process_document_to_knowledge(user, doc_id",
        "self.process_document_to_knowledge(user, m_reprocess.group(1), force=True)",
        "Document -> Extract Text -> Chunk -> Summary -> Tags -> Knowledge Records -> Search Index -> Ready for AI Q&A",
    ]:
        assert phrase in portal


def test_sprint003_summary_present():
    summary = read("SPRINT003_KNOWLEDGE_PIPELINE_SUMMARY.md")
    for phrase in [
        "Sprint003 Knowledge Pipeline Summary",
        "document_chunks",
        "POST /api/knowledge/process-document/:documentId",
        "GET /api/knowledge/items",
        "GET /api/documents/:id/chunks",
        "POST /api/documents/:id/reprocess",
        "does not build ai.vafox.com",
        "does not require any external AI API",
        "OCR placeholder",
        "Sprint004",
    ]:
        assert phrase in summary


def test_sprint004_global_search_schema_routes_and_helpers_present():
    portal = read("portal_v2.py")
    for phrase in [
        'ensure_column(conn, "timeline_events", col, ddl)',
        "idx_timeline_entity",
        "idx_timeline_source",
        "idx_timeline_event_type",
        "def global_search_results",
        "def search_snippet",
        'if path in ("/api/search", "/api/search/global")',
        'if path == "/api/search/suggestions"',
        'if path == "/api/timeline"',
        "def api_search_timeline_post",
        'if path in ("/os/search", "/search")',
        "file",
        "object",
        "knowledge",
        "chunk",
        "document_chunks",
    ]:
        assert phrase in portal


def test_sprint004_timeline_object_integration_present():
    portal = read("portal_v2.py")
    for phrase in [
        "def add_timeline_event",
        "def timeline_rows_for_entity",
        r"^/api/objects/(\d+)/timeline$",
        "object_created",
        "object_updated",
        "document_linked",
        "knowledge_created",
        "manual_note",
        r"\u4f01\u4e1a\u65f6\u95f4\u8f74",
        'method="post" action="/api/timeline"',
        "self.timeline_rows_for_entity(conn, row[\"object_type\"], row[\"id\"], 80)",
    ]:
        assert phrase in portal


def test_sprint004_summary_present():
    summary = read("SPRINT004_GLOBAL_SEARCH_TIMELINE_SUMMARY.md")
    for phrase in [
        "Sprint004 Global Search + Enterprise Timeline Summary",
        "GET /api/search?q=",
        "GET /api/search/suggestions?q=",
        "GET /api/timeline",
        "POST /api/timeline",
        "GET /api/objects/:id/timeline",
        "file",
        "object",
        "knowledge",
        "chunk",
        "does not build ai.vafox.com",
        "does not require any external AI API",
        "Sprint005",
    ]:
        assert phrase in summary


def test_sprint005_ceo_dashboard_home_and_api_present():
    portal = read("portal_v2.py")
    final_dashboard = portal.rsplit("def dashboard(self, user):", 1)[1].split("def os_layer_cards", 1)[0]
    for phrase in [
        "ceo_dashboard_payload",
        "FoxBrain CEO Brain",
        "FoxBrain CEO Home",
        'method="get" action="/search"',
        r"\u4eca\u65e5\u6458\u8981",
        r"\u6838\u5fc3\u5165\u53e3",
        r"\u6700\u8fd1\u6587\u4ef6",
        r"\u6700\u8fd1\u5bf9\u8c61",
        r"\u6700\u8fd1\u77e5\u8bc6",
        r"\u6700\u8fd1\u65f6\u95f4\u8f74",
        r"\u7cfb\u7edf\u72b6\u6001",
    ]:
        assert phrase in final_dashboard
    for phrase in [
        r"\u4f01\u4e1a\u7b2c\u4e8c\u5927\u8111",
        "/drive",
        "/object-center",
        "/knowledge",
        "/search",
        "/timeline",
        "/jarvis",
    ]:
        assert phrase in portal
    for phrase in [
        '"documents_total"',
        '"documents_pending"',
        '"documents_processed"',
        '"objects_total"',
        '"knowledge_items_total"',
        '"timeline_events_total"',
        '"recent_documents"',
        '"recent_objects"',
        '"recent_knowledge"',
        '"recent_timeline"',
        '"system_status"',
        '"core_entries"',
        'if path == "/api/dashboard/ceo"',
        "return self.json_out(self.ceo_dashboard_payload(user))",
    ]:
        assert phrase in portal


def test_sprint005_summary_present():
    summary = read("SPRINT005_CEO_DASHBOARD_SUMMARY.md")
    for phrase in [
        "Sprint005 CEO Dashboard Summary",
        "FoxBrain CEO Brain",
        "GET /api/dashboard/ceo",
        "documents",
        "enterprise_objects",
        "knowledge_items",
        "timeline_events",
        "FoxBrain Drive",
        "Object Engine",
        "Knowledge Engine",
        "Search Engine",
        "Timeline Engine",
        "does not build ai.vafox.com",
        "does not require any external AI API",
        "Sprint006",
    ]:
        assert phrase in summary


def test_sprint006_memory_engine_schema_routes_and_api_present():
    portal = read("portal_v2.py")
    for phrase in [
        "create table if not exists enterprise_memories",
        "create table if not exists memory_relations",
        "idx_enterprise_memories_type",
        "idx_enterprise_memories_risk",
        "idx_enterprise_memories_object",
        "def enterprise_memory_types",
        "def enterprise_memory_to_json",
        "def normalize_enterprise_memory_form",
        "def write_enterprise_memory_timeline",
        'if path in ("/memory", "/memories")',
        'path.startswith("/api/memories") or path == "/api/memory-types"',
        "def api_enterprise_memories_get",
        "def api_enterprise_memories_post",
        "def api_enterprise_memories_delete",
        'if path == "/api/memory-types"',
        'if path == "/api/memories"',
        r"^/api/memories/(\d+)$",
        r"^/api/objects/(\d+)/memories$",
    ]:
        assert phrase in portal


def test_sprint006_memory_engine_fields_dashboard_search_timeline_present():
    portal = read("portal_v2.py")
    for phrase in [
        "decision",
        "meeting",
        "risk",
        "strategy",
        "operation",
        "purchase",
        "pricing",
        "store",
        "brand",
        "supplier",
        "reason",
        "impact",
        "related_object_type",
        "related_document_id",
        "related_knowledge_id",
        "enterprise_memories_total",
        "high_risk_memories_total",
        "recent_memories",
        '\"type\": \"memory\"',
        "memory_created",
        "memory_updated",
        "enterprise_memory",
        "memory_relations",
        '\"url\": \"/memory\"',
    ]:
        assert phrase in portal


def test_sprint006_summary_present():
    summary = read("SPRINT006_MEMORY_ENGINE_SUMMARY.md")
    for phrase in [
        "Sprint006 Memory Engine Summary",
        "enterprise_memories",
        "memory_relations",
        "GET /api/memories",
        "POST /api/memories",
        "PATCH /api/memories/:id",
        "DELETE /api/memories/:id",
        "GET /api/memory-types",
        "GET /api/objects/:id/memories",
        "Dashboard integration",
        "Search integration",
        "Timeline integration",
        "does not build ai.vafox.com",
        "does not require any external AI API",
        "Sprint007",
    ]:
        assert phrase in summary


def test_sprint008_data_lake_schema_routes_and_api_present():
    portal = read("portal_v2.py")
    for phrase in [
        "create table if not exists data_lake_sources",
        "create table if not exists data_lake_records",
        "create table if not exists data_lake_lineage",
        "create table if not exists data_quality_checks",
        "create table if not exists business_object_links",
        "create table if not exists business_object_suggestions",
        "create table if not exists business_metrics_snapshots",
        "create table if not exists sap_import_batches",
        "create table if not exists sap_sales",
        "create table if not exists sap_inventory",
        "idx_data_lake_sources_batch",
        "idx_data_lake_records_hash",
        "idx_business_object_suggestions_unique",
        "def rebuild_data_lake_for_batch",
        "def rebuild_data_lake",
        "def refresh_business_metrics",
        "def business_metrics_summary",
        "def data_lake_page",
        "def object_match_center",
        "def api_data_lake_get",
        "def api_data_lake_post",
        '"/api/data-lake/rebuild"',
        '"/api/business-metrics/summary"',
        '"/api/object-links"',
        '"/api/object-suggestions"',
    ]:
        assert phrase in portal


def test_sprint008_dashboard_search_and_safety_present():
    portal = read("portal_v2.py")
    for phrase in [
        "FoxBrain Data Lake",
        "Object Match Center",
        "data_lake_records",
        "suggested_objects",
        "quality_alerts",
        "sales_amount",
        "gross_profit",
        "inventory_retail_amount",
        "top_store_sales",
        "top_brand_sales",
        '"type": "data_lake_source"',
        '"type": "data_lake_record"',
        '"type": "object_link"',
        '"type": "object_suggestion"',
        '"type": "business_metric"',
        "file_import_only_no_production_sap_connection",
        r"\u4e0d\u8fde\u63a5\u751f\u4ea7 SAP",
    ]:
        assert phrase in portal


def test_sprint008_summary_and_report_present():
    summary = read("SPRINT008_DATA_LAKE_SUMMARY.md")
    report = read("SPRINT008_DATA_LAKE_TEST_REPORT.md")
    real_report = read("SPRINT008_REAL_SAP_DATA_TEST_REPORT.md")
    for phrase in [
        "Sprint008 Data Lake Summary",
        "data_lake_sources",
        "business_object_links",
        "CEO Dashboard V2",
        "POST /api/data-lake/rebuild",
        "GET /api/business-metrics/summary",
        "No production SAP connection",
        "Sprint009",
    ]:
        assert phrase in summary
    for phrase in [
        "Sprint008 Data Lake Test Report",
        "Syntax check",
        "Smoke tests",
        "Pipeline simulation",
        "Data Lake records",
        "Object suggestions",
        "Business metrics",
    ]:
        assert phrase in report
    for phrase in [
        "Sprint008 Real SAP Data Validation Report",
        "2501",
        "25kailas",
        "26kailas",
        "gb18030",
        "data_lake_records",
        "55,457",
        "42,672",
        "12,785",
        "Sales amount",
        "Gross profit",
        "Inventory retail amount",
        "No production SAP connection was made",
    ]:
        assert phrase in real_report


def test_sprint008_5_business_calibration_schema_routes_and_api_present():
    portal = read("portal_v2.py")
    for phrase in [
        "create table if not exists store_aliases",
        "create table if not exists brand_aliases",
        "create table if not exists business_calibration_rules",
        "create table if not exists business_metric_quality",
        "canonical_key text",
        "idx_business_object_suggestions_canonical",
        "def canonical_store_name",
        "def canonical_brand_name",
        "def product_canonical_key",
        "def business_calibration_page",
        '"/business-calibration"',
        '"/api/business-calibration/summary"',
        '"/api/business-calibration/store-aliases"',
        '"/api/business-calibration/brand-aliases"',
        '"/api/business-calibration/quality"',
        '"/api/business-calibration/rebuild"',
    ]:
        assert phrase in portal


def test_sprint008_5_dashboard_search_and_safety_present():
    portal = read("portal_v2.py")
    for phrase in [
        "Business Calibration",
        "gross_margin",
        "inventory_cost_amount",
        "metric_quality_warnings",
        '"type": "store_alias"',
        '"type": "brand_alias"',
        '"type": "calibration_rule"',
        '"type": "metric_quality"',
        "Store Alias",
        "Brand Alias",
        "Calibration Rule",
        "Metric Quality",
        "file_import_only_no_production_sap_connection",
        r"\u4e0d\u8fde\u63a5\u6216\u4fee\u6539\u751f\u4ea7 SAP",
    ]:
        assert phrase in portal


def test_sprint008_5_summary_and_report_present():
    summary = read("SPRINT008_5_BUSINESS_CALIBRATION_SUMMARY.md")
    report = read("SPRINT008_5_BUSINESS_CALIBRATION_TEST_REPORT.md")
    for phrase in [
        "Sprint008.5 Business Calibration Summary",
        "store_aliases",
        "brand_aliases",
        "business_calibration_rules",
        "business_metric_quality",
        "Object Match Center",
        "CEO Dashboard",
        "No production SAP connection",
    ]:
        assert phrase in summary
    for phrase in [
        "Sprint008.5 Business Calibration Test Report",
        "Store normalization",
        "Brand normalization",
        "Product calibration",
        "Object suggestion reduction",
        "Dashboard changes",
        "No production SAP connection",
    ]:
        assert phrase in report


def test_sprint009_knowledge_graph_schema_routes_and_api_present():
    portal = read("portal_v2.py")
    for phrase in [
        "create table if not exists knowledge_graph_nodes",
        "create table if not exists knowledge_graph_edges",
        'ensure_column(conn, "knowledge_graph_nodes", "object_id"',
        'ensure_column(conn, "knowledge_graph_nodes", "name"',
        'ensure_column(conn, "knowledge_graph_edges", "source_node_id"',
        'ensure_column(conn, "knowledge_graph_edges", "source_type"',
        "def build_business_knowledge_graph",
        "def knowledge_graph_explorer",
        "def knowledge_graph_context",
        '"/knowledge-graph"',
        "GET /api/graph/node/:id",
        "GET /api/graph/relations/:id",
        "GET /api/graph/context/:id",
        '"/api/graph/build"',
    ]:
        assert phrase in portal


def test_sprint009_knowledge_graph_sources_dashboard_and_search_present():
    portal = read("portal_v2.py")
    for phrase in [
        "All generated graph edges require source_type and source_id",
        "Every relationship includes source_type and source_id",
        "enterprise_objects",
        "object_relations",
        "sap_sales",
        "sap_inventory",
        "documents",
        "knowledge_items",
        "enterprise_memories",
        "graph_nodes",
        "graph_relationships",
        "connected_brands",
        "connected_products",
        '"type": "knowledge_graph"',
        '"type": "knowledge_graph_edge"',
        "Business Knowledge Graph",
        "no_production_sap_connection_no_unsupported_relationships",
    ]:
        assert phrase in portal


def test_sprint009_summary_and_report_present():
    summary = read("SPRINT009_KNOWLEDGE_GRAPH_SUMMARY.md")
    report = read("SPRINT009_KNOWLEDGE_GRAPH_TEST_REPORT.md")
    for phrase in [
        "Sprint009 Knowledge Graph Summary",
        "knowledge_graph_nodes",
        "knowledge_graph_edges",
        "GET /api/graph/node/:id",
        "GET /api/graph/relations/:id",
        "GET /api/graph/context/:id",
        "POST /api/graph/build",
        "All graph relationships require traceable sources",
    ]:
        assert phrase in summary
    for phrase in [
        "Sprint009 Knowledge Graph Test Report",
        "Graph build simulation",
        "Graph nodes",
        "Graph relationships",
        "Edges with source",
        "No production SAP connection",
        "Smoke tests",
    ]:
        assert phrase in report
