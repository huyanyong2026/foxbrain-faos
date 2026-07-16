# VAFOX Design System V1

## Principles
- One enterprise OS visual language across Gateway, Huyan, AI, and Core.
- Reuse existing Portal V2 layout primitives: top navigation, bottom mobile navigation, panels, cards, metrics, split views, status tags, and action buttons.
- Evidence-first enterprise workflows: every dashboard card should lead to data, task, decision, or approval context.

## Components
- Navigation: primary top navigation, mobile bottom navigation, global search, AI copilot launcher.
- Dashboard Cards: role dashboard entries and operating summaries.
- AI Cards: agent purpose, permission, knowledge source, memory, and task status.
- Data Tables: enterprise data lists and governance records.
- Risk Cards: risk radar and prioritized operating issues.
- Task Cards: running, completed, and approval-pending work.
- Notification Components: system status, risk notifications, and approval alerts.

## Reuse Rule
All future VAFOX modules should reuse the shared `layout`, `card`, `metric`, `bullets`, `grid`, `panel`, `split`, and `status-tag` patterns in `portal_v2.py` instead of creating a duplicate UI system.
