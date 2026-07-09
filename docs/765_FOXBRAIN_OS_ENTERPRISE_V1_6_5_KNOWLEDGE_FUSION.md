# FoxBrain OS Enterprise V1.6.5 Knowledge Fusion

## Goal

Continue from FoxBrain OS Enterprise V1.6 without rebuilding the system. V1.6.5 builds a three-layer knowledge fusion system for existing Agents.

## Three Layers

1. SAP Enterprise Knowledge Base
   - Source: SAP Knowledge Engine and downstream AI warehouse.
   - Role: company factual base for sales, inventory, product, member and gross profit facts.
   - Rule: SAP remains the source of truth and no SAP writeback is allowed from fusion.

2. External Industry Knowledge Base
   - Source: reviewed external research, industry documents and market notes in `knowledge_items`.
   - Role: market context, benchmark, retail method and content inspiration.
   - Rule: external industry knowledge is context only and cannot override SAP facts.

3. Boss Experience Knowledge Base
   - Source: reviewed memories, decision memories, AI operation feedback and preferences.
   - Role: operating principles, decision tradeoffs, store experience and risk tolerance.
   - Rule: boss experience requires review before active Agent use.

## Agent Usage

Existing Agents call fusion knowledge before drafting recommendations:

- CEO Agent
- Business Agent
- Inventory Agent
- Product Agent
- Member Agent
- Content Agent

Each Agent output must expose SAP basis, industry context, boss experience basis, limitations and approval requirements where relevant.

## APIs

- `/api/knowledge/fusion`
- `/api/knowledge/v1.6.5`
- `/api/knowledge/fusion/external-industry`
- `/api/knowledge/fusion/contract`
- `/api/knowledge/fusion/agents/{agent}`
- `/api/agents/v1.6/fusion-knowledge`

## Safety

Fusion recommendations are explainable, traceable and auditable. High-risk actions still require human approval.
