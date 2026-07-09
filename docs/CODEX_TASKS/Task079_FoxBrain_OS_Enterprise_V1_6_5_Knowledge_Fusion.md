# Task079 FoxBrain OS Enterprise V1.6.5 Knowledge Fusion

## Request

Based on FoxBrain OS Enterprise V1.6, complete the V1.6.5 knowledge fusion upgrade. Focus on a three-layer fusion system: SAP enterprise knowledge base, external industry knowledge base and boss experience base. Existing Agents must call fused knowledge.

## Implementation

- Added `foxbrain_os/knowledge_fusion.py`.
- Added fusion APIs under `/api/knowledge/fusion`.
- Added Agent fusion context API under `/api/agents/v1.6/fusion-knowledge`.
- Added external industry knowledge payload from reviewed `knowledge_items`.
- Connected fusion context to V1.6 multi-agent collaboration payload and pending approval plans.
- Added docs and smoke tests.

## Safety

- No database rebuild.
- No SAP writeback.
- External industry knowledge is context only.
- Boss experience requires review before active Agent use.
- High-risk Agent recommendations still require human approval.
