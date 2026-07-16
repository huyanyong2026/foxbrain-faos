# VAFOX Business Activation V1.0

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

## Architecture

SAP B1 -> Core Enterprise Digital Twin -> AI Platform -> Business Applications. Business Activation V1.0 only reads facts from Core and produces approval-ready recommendations. No module in BA-V1 writes to SAP.

## Components

1. Supply Chain Agent: replenishment, overstock, inventory health, dashboard, CSV/Excel-ready exports.
2. CEO Operating System: Huyan dashboard, daily briefing, risk radar, decision center.
3. Enterprise WeCom AI: employee natural-language entry with RBAC/ABAC filtering.
4. Store Digital Employee: store dashboard, health, task focus, AI suggestions.
