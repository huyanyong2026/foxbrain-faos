# Sprint018 Enterprise Copilot Summary

## Scope

Sprint018 implements the Enterprise Copilot foundation on the existing `huyan.vafox.com` portal codebase.

This is an incremental upgrade. It does not rebuild the system, does not develop `ai.vafox.com`, and does not connect to SAP write access.

## Data Model

Added Copilot persistence tables:

- `copilot_sessions`
- `copilot_messages`
- `copilot_feedback`

The assistant message stores:

- answer text
- `evidence_json`
- `context_json`
- session intent

## API

Added:

- `POST /api/copilot/ask`
- `GET /api/copilot/sessions`
- `GET /api/copilot/sessions/:id`
- `GET /api/copilot/context?q=...`
- `POST /api/copilot/feedback`
- `POST /api/copilot/messages/:id/memory-draft`

## Page

Added:

- `/copilot`

The page supports:

- CEO question input
- quick question chips
- answer display
- evidence display
- session history
- memory draft creation from an evidence-backed answer

## Context Engine

The Copilot Context Engine retrieves enterprise context from existing Enterprise OS modules:

- Data Lake and business metrics
- Enterprise Objects
- Knowledge Graph
- Business Rule Engine
- Decision Engine
- Enterprise Memory
- Daily Intelligence
- Global Search results

Initial intent routing supports:

- `business_question`
- `inventory_question`
- `brand_question`
- `store_question`
- `product_question`
- `sales_question`
- `decision_question`
- `history_question`

## Evidence Mechanism

Every answer is generated from a normalized evidence list.

Evidence items include:

- `source_type`
- `source_id`
- `title`
- `summary`
- `url`
- `confidence`
- related object type/id when available

If there is no usable enterprise evidence, Copilot returns an insufficient-evidence answer and does not invent business conclusions.

## Memory Integration

Added memory draft creation from assistant answers:

- source: `copilot_messages`
- target: `enterprise_memories`
- status: `draft`
- relation: `memory_relations`

Memory draft creation is blocked when the answer has no evidence.

## CEO Dashboard Integration

The CEO homepage AI entry now points to:

- `/copilot`

The existing Jarvis page remains available at:

- `/jarvis`

## Safety

- No SAP production connection was added.
- No SAP write operation was added.
- No external AI API is required.
- Answers are constrained to existing Enterprise OS data.
- High-risk execution remains outside Copilot and requires human approval.

