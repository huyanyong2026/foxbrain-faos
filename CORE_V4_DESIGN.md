# CORE_V4_DESIGN

Version: AI-OS-V4.0

## Purpose
FoxBrain V4 upgrades the platform from an enterprise AI system into an autonomous AI enterprise operating system. The experience starts from business events and natural questions, then automatically matches identity, business object, data source, agent, recommendation, task draft, human approval, execution, and learning.

## Non-negotiable Rules
- SAP remains the Business Truth Layer.
- Core remains the Enterprise Digital Twin.
- AI remains the Intelligence Layer.
- Humans remain the Strategic Decision Owner.
- AI must not modify SAP business logic or create duplicate business truth.
- RBAC, ABAC, and audit logs are mandatory for all AI-driven flows.

## V4 Operating Flow
Business Event → Core Data Understanding → AI Reasoning → Agent Selection → Recommendation → Task Creation → Human Approval → Execution → Learning.

## Acceptance
This document is backed by `foxbrain_os.ai_os_v4` and `tests/test_ai_os_v4.py`. Acceptance requires automatic routing, proactive CEO intelligence, natural AI conversation, governed data matching, visible data activity, security checks, deployment readiness, and rollback readiness.

## Enterprise Digital Twin
Core exposes master data, sales events, inventory events, purchase events, customer events, task events, and AI context without replacing SAP as truth.
