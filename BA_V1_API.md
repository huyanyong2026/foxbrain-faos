# FoxBrain Business Activation V1.0

Status: implemented as application-layer business activation on top of Foundation V2.0. SAP remains the business truth layer; Core remains the enterprise data layer; AI provides recommendations; humans approve actions.

## Scope

BA-001 Supply Chain Intelligence Center, BA-002 CEO Command Center, BA-003 Enterprise WeCom AI, and BA-004 Store Intelligence Center are delivered without redesigning infrastructure or changing SAP core logic.

## Foundation endpoints

- gateway.vafox.com: secured business entry and routing.
- huyan.vafox.com: CEO operating surface.
- ai.vafox.com: recommendation and assistant layer.
- core.vafox.com: read-only enterprise facts from the digital twin.

## Implementation reference

The deterministic activation services live in `foxbrain_os/business_activation_v1.py`. They transform Core facts into replenishment recommendations, overstock actions, inventory health scores, CEO dashboards, daily briefings, risk radar, WeCom responses, store dashboards, store assistant output, CSV exports, permission checks, and audit events.

## Acceptance mapping

- Supply Chain PASS: replenishment, overstock, inventory health, dashboard, and export are covered.
- CEO PASS: dashboard, daily briefing, risk radar, and decision center are covered.
- WeCom AI PASS: employee queries enforce permissions and data scope.
- Store PASS: dashboard and assistant are covered.
- Production PASS: release, operation, health check, and rollback runbooks are defined in the BA release and operation docs.

## Application APIs

The pure service functions are intentionally transport-agnostic so Gateway/Huyan/AI can expose them as HTTP routes without creating a second source of truth.

- `replenishment_recommendations(facts)` -> product, store, suggested quantity, priority, reason.
- `overstock_intelligence(facts)` -> transfer, promotion, clearance, keep candidates.
- `inventory_health_score(facts)` -> store health and risk counters.
- `supply_chain_dashboard(facts)` -> replenishment tasks, inventory risks, overstock, brand status.
- `ceo_dashboard(facts)` -> sales, gross margin, inventory, supply chain, store status and AI recommendations.
- `daily_ceo_briefing(facts)` -> what happened, why, recommended actions.
- `risk_radar(facts)` -> sales, inventory, supply, and store risk.
- `wecom_ai_query(question, facts, context)` -> authorized product/inventory/store response.
- `store_dashboard(facts, store_code)` and `store_ai_assistant(...)` -> store operations surface.
