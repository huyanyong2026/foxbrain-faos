# VAFOX Workforce Home Architecture

Version: Genesis-Construction-002  
Domain: `ai.vafox.com`  
Purpose: mobile-first employee Home for Today, Mission, Execution, Learning, and Growth.

## 1. Experience Rule

`ai.vafox.com` is not a dashboard, agent selector, data source selector, or manual analysis workspace. It is the employee Home.

The employee should immediately understand:

- Who am I in VAFOX today?
- What matters today?
- What should I do?
- How can AI help me?

## 2. Home Model

```text
Home
  ↓
Today
  ↓
Mission
  ↓
Execution
  ↓
Learning
  ↓
Growth
```

### Home

Personal landing state generated from Gateway identity and Core context.

Contains:

- VID-based greeting.
- Active role and organization context.
- Today summary.
- Primary mission prompt.
- AI Companion entry.

### Today

A short, prioritized view of what matters now.

Inputs:

- Mission Engine.
- Core freshness-aware enterprise context.
- Permission-filtered Digital Twin signals.
- Personal workflow state.

### Mission

The user's work is framed as missions, not reports.

Mission types:

- Required mission.
- Suggested mission.
- Learning mission.
- Approval mission.
- Follow-up mission.

### Execution

Execution guides the user through concrete next steps.

Execution may include:

- Checklist.
- Draft response.
- Approval request.
- Data review.
- Workflow handoff.
- Human confirmation before sensitive action.

### Learning

Learning captures what the user needs to understand to perform better.

Examples:

- Product knowledge.
- Process guidance.
- Customer or supplier context.
- Safety and compliance reminders.

### Growth

Growth reflects accumulated capability, contribution, and mission learning.

Growth signals must avoid gamified vanity metrics that conflict with enterprise trust.

## 3. AI Companion Model

The user asks naturally. The system handles the workflow invisibly.

```text
Natural question
  ↓
Intent understanding
  ↓
Permission check
  ↓
Core data retrieval
  ↓
Reasoning with FoxBrain Intelligence Engine
  ↓
Answer with freshness and confidence context
  ↓
Optional mission or workflow action
```

AI Companion responsibilities:

- Understand user intent.
- Resolve active role and mission context.
- Check permission before retrieval.
- Retrieve data only through Core.
- Reason over approved context.
- Provide concise answers.
- Create optional action drafts.
- Escalate uncertainty or restricted requests.

AI Companion must not:

- Ask the user to choose an agent first.
- Ask the user to select a data source first.
- Bypass Core.
- Execute sensitive business actions without approval.
- Reveal data outside the session permission snapshot.

## 4. Mobile Information Architecture

Primary navigation:

1. Home.
2. Today.
3. Missions.
4. Ask AI.
5. Me.

The first screen must answer within 3 seconds:

- Identity: name, role, relationship.
- Priority: one to three things that matter today.
- Action: the next mission or decision.
- Help: one-tap Ask AI.

## 5. Integration Boundaries

`ai.vafox.com` consumes:

- Gateway session and VID context.
- Core enterprise context APIs.
- Digital Twin prepared state.
- FoxBrain Intelligence Engine reasoning.
- Mission Engine tasks and recommendations.
- Workflow approval and action lifecycle.
- Memory for approved personal and enterprise learning.

It does not own source data, authentication, permission authority, SAP integration, or enterprise data validation.

## 6. Future Compatibility

Workforce Home must be designed as the first Home pattern, not a one-off application. Shared contracts should later support Customer Home, Supplier Home, Brand Home, Club Home, and Community Home without duplicating identity, Core, or AI governance.
