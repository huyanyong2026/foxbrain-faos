# Huyan V3 Design

Version: UX-V3.0

## Mission
Transform FoxBrain from an AI tool surface into an AI-native enterprise second brain for ai.vafox.com and huyan.vafox.com.

## Core Principle
Users ask business questions directly. The system automatically understands intent, selects hidden agents, retrieves permitted data, analyzes evidence, recommends a decision, and creates review-gated tasks or memory drafts.

## Experience Contract
- No user-facing agent selector.
- No manual object type or data-source configuration.
- Every reliable answer follows: Conclusion, Reason, Data Source, Recommendation, Next Action.
- RBAC, ABAC, audit logging, and human approval gates remain active.

## V3 Components
- AI-native workspace with a large chat entrance and business example prompts.
- AI Router Engine for intent recognition and hidden agent selection.
- Hidden Agent Architecture: CEO, Supply Chain, Store, Finance, Growth, Customer, Supplier, and Commerce agents.
- CEO Daily Command Center with enterprise health, five priorities, risks, opportunities, and recommended actions.
- Task generation from evidence-backed answers, always as drafts until human approval.
- Memory upgrade for decisions, outcomes, preferences, and historical analysis.

## Acceptance Mapping
- AI.VAFOX.COM: direct ask without selecting Agent.
- AI Router: automatic agent choice stored in answer context.
- AI Answer: structured conclusion/reason/data/recommendation/action.
- Task Generation: evidence-backed draft tasks.
- Memory: evidence-backed draft memories and learning records.
- Huyan: proactive CEO intelligence and question mode.
- Deployment: feature branch `feature/ux-v3-ai-native`, automated tests, PR, merge, deploy, health check.
