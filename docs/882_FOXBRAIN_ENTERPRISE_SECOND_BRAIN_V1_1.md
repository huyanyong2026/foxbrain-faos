# FoxBrain Enterprise Second Brain V1.1

## Focus

V1.1 upgrades four core capabilities:

1. Drive 2.0
2. Object Engine
3. Knowledge Pipeline
4. CEO Home

This is an architecture and product-baseline upgrade, not a page-only change.

## Drive 2.0

FoxBrain Drive 2.0 is the Enterprise Knowledge Drive. Files and folders are no longer passive storage; they become AI-readable enterprise knowledge assets.

Initial domains:

- Brand Drive
- Store Drive
- Product Drive
- Contract Drive
- Media Drive

Rules:

- Folders become objects.
- Documents become knowledge objects.
- AI outputs keep source lineage.
- Sensitive content requires review.

## Object Engine

Object Engine standardizes enterprise objects:

- Company
- Store
- Brand
- Product
- Customer
- Document
- Memory

Every object must have object type, source, owner, permission scope, timeline and relationships.

## Knowledge Pipeline

Knowledge Pipeline converts files and records into governed AI context:

```text
Document
-> OCR
-> Chunk
-> Embedding
-> Vector DB
-> Graph
-> AI Summary
-> Knowledge Object
-> Agent
```

AI summaries and sensitive knowledge objects require human review before high-risk use.

## CEO Home

CEO Home V1.1 keeps the root home minimal. The first page still shows the ten Owner OS entries only; detailed CEO information appears after click-through.

CEO sections:

- Top Focus
- Business Brief
- Knowledge Brief
- Action Brief

## Routes

- `/drive`
- `/objects`
- `/knowledge-pipeline`
- `/ceo-home`

## APIs

- `/api/second-brain/v1.1`
- `/api/drive/v2`
- `/api/object-engine`
- `/api/knowledge-pipeline`
- `/api/ceo-home`

## Guardrails

- SAP remains the system of record.
- High-risk actions require human approval.
- Source lineage is required.
- Root home must not become a content-heavy dashboard.
