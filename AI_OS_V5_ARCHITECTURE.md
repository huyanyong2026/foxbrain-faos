# AI OS V5 Architecture

Version: AI-OS-V5.0

## Mission
Transform FoxBrain from an AI Enterprise System into an Autonomous AI Enterprise Operating System. The operating model changes from human-operated systems to AI-operated enterprise context with humans retaining strategic decision ownership.

## Guardrails
- SAP remains the Business Truth Layer; do not modify SAP business logic.
- Core remains the Enterprise Digital Twin; do not create duplicate business truth.
- AI remains the Intelligence Layer; it recommends and drafts actions.
- Human owners approve execution and remain the strategic decision owners.
- RBAC, ABAC, and audit logs are mandatory for every data view and action.

## Operating Flow
Business Event → Core Data Activity Engine → AI Understanding → Agent Router → AI Analysis → Recommendation → Task Generation → Human Approval → Execution → Memory Learning.

## Modules
1. Gateway V5 automatically identifies CEO, employee, procurement, store manager, supplier, and customer identities.
2. Huyan V5 presents CEO Today, AI risks, AI opportunities, recommended actions, decision center, AI meeting, and strategic simulation.
3. AI Workspace V5 provides one universal question interface and removes manual agent, object, source, and analysis selection.
4. Core V5 exposes SAP → Core → AI → Decision → Action activity flow and provides context, history, knowledge, and decision memory.
5. Automation V5 detects events, analyzes them, drafts tasks, notifies owners, captures feedback, and learns.

## Acceptance
Gateway, Huyan, AI Workspace, AI Router, Core, Automation, Security, and Deployment are PASS when deterministic contract tests pass.
