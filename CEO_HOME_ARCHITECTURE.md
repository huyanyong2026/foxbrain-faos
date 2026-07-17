# VAFOX CEO Home Architecture

Version: Genesis-Construction-002  
Domain: `huyan.vafox.com`  
Purpose: Founder / CEO Home for enterprise awareness, risk, opportunity, decision, and AI briefing.

## 1. Experience Rule

`huyan.vafox.com` is not a dashboard and not a report center. It is the CEO Home: a calm command home that helps the founder understand the enterprise and decide what matters.

## 2. CEO Home Sections

### 1. Enterprise Today

A concise briefing of the enterprise's current state.

Includes:

- Overall operating pulse.
- Most important changes since last briefing.
- Mission-critical updates.
- Freshness status of underlying data.

### 2. Health

Health summarizes whether the enterprise is functioning well.

Signals may include:

- Sales and demand health.
- Inventory and supply health.
- Cash and margin indicators.
- Team execution health.
- Customer and partner health.

### 3. Risks

Risks identify what may harm the enterprise.

Risk entries require:

- Risk statement.
- Evidence from Core / Digital Twin.
- Severity.
- Time sensitivity.
- Suggested owner or mission.
- Confidence and freshness indicator.

### 4. Opportunities

Opportunities identify where VAFOX can move forward.

Opportunity entries require:

- Opportunity statement.
- Evidence.
- Potential impact.
- Required decision or experiment.
- Suggested mission path.

### 5. Decisions

Decision space organizes what needs CEO attention.

Decision types:

- Approve.
- Reject.
- Ask for more evidence.
- Delegate.
- Convert to mission.
- Schedule review.

Sensitive decisions must use workflow and governance. CEO Home may recommend and draft, but must not bypass approval and audit controls.

### 6. AI Briefing

AI Briefing is a generated narrative from trusted enterprise context.

Briefing rules:

- Use Core-prepared context.
- Explain important changes, risks, and decisions.
- Surface confidence and freshness when relevant.
- Separate fact, inference, and recommendation.
- Preserve auditability.

### 7. Ask VAFOX

Ask VAFOX is the CEO natural-language interface to the enterprise.

Flow:

```text
CEO question
  ↓
Intent + decision context understanding
  ↓
Permission confirmation
  ↓
Core / Digital Twin / Memory retrieval
  ↓
FoxBrain reasoning
  ↓
Answer, briefing, or decision draft
  ↓
Optional mission / workflow creation
```

## 3. CEO Home Data Boundary

CEO Home consumes the same foundation as every Home:

- Gateway identity and session.
- Core enterprise context.
- Digital Twin prepared state.
- FoxBrain Intelligence Engine.
- Mission Engine.
- Workflow.
- Runtime Governance AI-OS-V5.1.

CEO Home must not directly query SAP production, create separate executive datasets, or build isolated reporting logic.

## 4. Interaction Principles

- Calm before complex.
- Brief before detail.
- Decision before report.
- Evidence before action.
- Mission before follow-up chaos.
- Human authority remains explicit.

## 5. Implementation Boundary for Phase 2

This package defines architecture only. Do not implement large CEO features yet. Future construction should start with read-only briefing contracts and permission-safe Ask VAFOX flows before any decision automation.
