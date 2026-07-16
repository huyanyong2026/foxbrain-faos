# AI Workforce OS V5 Design

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

## Universal AI Interface
Homepage prompt: Hello, what would you like to know? Users ask natural questions such as company risks, store health, purchase planning, and brand opportunity.

## Removed Manual Configuration
Agent selection, object selection, data source selection, and analysis type selection are removed.

## Response Standard
Every response includes Conclusion, Reason, Data Source, Recommendation, and Next Action.
