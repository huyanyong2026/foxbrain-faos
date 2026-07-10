# Sprint018: Enterprise Copilot Foundation｜企业智能助手基础

Status: Ready for Codex
Target: huyan.vafox.com
Priority: P0
Depends on: Sprint009 Knowledge Graph, Sprint010 Decision Engine, Sprint011 Business Rules, Sprint017 Daily Intelligence

---

## 1. Sprint Goal

Build FoxBrain Enterprise Copilot Foundation.

The goal is to allow CEO to ask questions about the enterprise and receive evidence-based answers.

```text
CEO Question
↓
Intent Understanding
↓
Enterprise Context Retrieval
↓
Evidence Collection
↓
Answer Generation
↓
Memory / Feedback
```

---

## 2. Core Principle

Copilot is not a general chatbot.

It is an enterprise reasoning interface.

Every answer must show:

- data sources
- evidence
- related objects
- related decisions
- confidence

No unsupported business conclusion.

---

## 3. Initial Question Types

Support:

```text
business_question
inventory_question
brand_question
store_question
product_question
sales_question
decision_question
history_question
```

Examples:

- 为什么某品牌销售下降？
- 哪些库存风险最高？
- 哪个门店表现最好？
- 最近有哪些重要经营变化？
- 某个决定为什么做出？

---

## 4. Copilot Context Engine

Create enterprise context retrieval layer.

Sources:

- Data Lake
- Objects
- Knowledge Graph
- Business Rules
- Decision Insights
- Daily Intelligence
- Memories

Return:

```text
Entity Context
Metrics
Timeline
Evidence
Rules
Previous Decisions
```

---

## 5. Data Model

Create:

## copilot_sessions

Fields:

```text
id
user_id
question
intent
status
created_at
```

## copilot_messages

Fields:

```text
id
session_id
role
content
evidence_json
context_json
created_at
```

## copilot_feedback

Fields:

```text
id
message_id
feedback_type
comment
created_at
```

---

## 6. UI Requirements

Add:

```text
/copilot
```

Display:

- Question input
- Answer
- Evidence
- Related objects
- Related decisions
- Related memory

---

## 7. API Requirements

Add:

```text
POST /api/copilot/ask
GET /api/copilot/sessions
GET /api/copilot/sessions/:id
POST /api/copilot/feedback
```

---

## 8. CEO Dashboard Integration

Add:

AI问企业入口。

Keep homepage simple.

---

## 9. Memory Integration

Allow useful answers to become enterprise memory drafts.

Preserve:

- question
- answer
- evidence
- decision context

---

## 10. QA Acceptance

Sprint018 passes when:

- Copilot page works.
- Enterprise context can be retrieved.
- Answers include evidence.
- Related objects can be displayed.
- Feedback can be recorded.
- Memory draft creation works.
- Existing Sprint001-017 functions remain working.
- No SAP write access.
- No unsupported AI conclusions.

---

## 11. Codex Instruction

Incremental upgrade only.

Do not replace existing AI architecture.

Do not develop ai.vafox.com.

Use existing Enterprise OS data layers.

Deliver:

```text
SPRINT018_ENTERPRISE_COPILOT_SUMMARY.md
SPRINT018_ENTERPRISE_COPILOT_TEST_REPORT.md
```
