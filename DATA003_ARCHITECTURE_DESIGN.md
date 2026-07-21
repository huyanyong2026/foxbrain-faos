# DATA-003: Customer–Retail–Knowledge Integration Architecture

**Status:** Design contract  
**Scope:** Customer, retail product and inventory intelligence, activity orchestration, employee assistance, and learning loops.  
**Operating boundary:** This is a read-oriented integration design. SAP remains the business-truth system; Core remains the enterprise fact center. Nothing in this document modifies SAP, changes Core production synchronization, or authorizes automatic production operations.

---

## 1. Design objectives and non-negotiable boundaries

DATA-003 connects three governed brains without creating a new system of record:

```text
Customer Brain                  Retail Brain                 Knowledge Brain
identity + consent + events  product + inventory + sales   approved content + policies
          \                         |                         /
           \                        |                        /
            ------ Core Service Layer / policy enforcement ----
                                      |
                         Activity Engine (recommend, never execute)
                                      |
               Employee AI Assistant / human review / approved workflow
                                      |
                      outcomes, feedback, and measured learning
```

| Principle | Required behavior |
| --- | --- |
| Source authority | SAP/ERP, CRM, POS, WMS, and knowledge owners retain authority for their records. Core stores governed facts and references; recommendations are derived intelligence. |
| Read before action | All APIs below are read-only except the Activity Engine's internal draft/feedback records. No API writes to SAP, Core production synchronization, inventory, price, order, or customer record. |
| Policy before data | A caller supplies authenticated principal, delegated subject (if any), purpose, tenant/legal entity, and correlation ID. The service applies RBAC + ABAC, field masking, row filtering, consent, and retention controls before responding. |
| Evidence before recommendation | A recommendation contains source/lineage references, freshness and quality state, calculation/model version, and an explicit confidence. |
| Human control | APIs may create a **proposal** or **task draft** only. An approved, separately governed workflow is required for every operational action. |
| Privacy by design | Direct identifiers remain in the restricted identity vault. Recommendation and activity services use `customer_id`, pseudonymous keys, and purpose-limited attributes; they never return raw identifiers by default. |

### 1.1 Three-brain ownership

| Brain | Canonical service objects | Inputs | Produces | Does not do |
| --- | --- | --- | --- | --- |
| Customer | Customer ID, consent, profile facets, lifecycle events | CRM/member/POS/e-commerce identities and interaction events | resolved identity, authorized profile and segment facts | replace a CRM source or expose PII without policy |
| Retail | Product, assortment, store, inventory position, sales signal | SAP/ERP/POS/WMS facts via existing governed Core products | product and inventory recommendation inputs | update stock, orders, prices, or SAP |
| Knowledge | Knowledge asset, policy, playbook, answer evidence | approved documents, FAQs, policies, training content | cited, versioned assistance context | treat unapproved AI text as policy |

---

## 2. Customer ID model

### 2.1 Identity model

`customer_id` is an immutable, opaque Core-issued UUID. It represents a resolved person or organization within one tenant; it is never a phone number, email address, membership number, or source-system key. The identity vault maps source identifiers to this ID, while the integration layer retains only hashed/tokenized values where feasible.

```text
source identifier (restricted) → normalized + salted HMAC → identity_alias
                                                        ↓
                                              match decision / evidence
                                                        ↓
 customer_id ← customer_identity_link → source system + source customer key
```

| Field | Type / example | Rules |
| --- | --- | --- |
| `customer_id` | UUID, `cst_01J...` | Immutable opaque ID; tenant-scoped. |
| `identity_alias_id` | UUID | One tokenized identifier alias; never returned to ordinary consumers. |
| `source_system` | enum: `crm`, `pos`, `ecommerce`, `sap_mirror`, `service` | Identifies the originating system, not authority transfer. |
| `source_customer_key` | string, restricted | Encrypted/restricted reference used for reconciliation. |
| `identity_type` | `phone`, `email`, `member_no`, `device`, `external_id` | Phone/email are normalized before tokenization. |
| `match_state` | `verified`, `probable`, `unresolved`, `rejected`, `merged` | Only `verified` is used for deterministic personalization by default. |
| `match_method` | `source_asserted`, `verified_attribute`, `reviewed`, `model_assisted` | Model-assisted matches require review before promotion to `verified`. |
| `consent_state` | `granted`, `denied`, `withdrawn`, `unknown` | Purpose-specific and time-bounded; unknown is deny for marketing/personalization. |
| `survivor_customer_id` | UUID/null | Set only after a reviewed merge; old IDs remain resolvable for audit. |

### 2.2 Resolution and lifecycle rules

1. Normalize identifier according to a versioned rule, create a keyed hash/token in the restricted vault, then look up exact aliases within tenant.
2. If a trusted source asserts the identity or verified attributes meet the approved match policy, link it as `verified`; otherwise retain a `probable` candidate without silently merging profiles.
3. Conflicts, merges, and unmerges are reviewer-controlled, auditable identity events. A merge preserves all source references and a redirect from the retired ID.
4. Consent is an append-only, purpose-specific event (`service`, `analytics`, `personalization`, `marketing`). Withdrawal takes effect immediately for new retrieval; downstream erasure/retention processes follow the applicable policy.
5. Customers can be represented as a minimal, pseudonymous profile when consent or evidence does not permit enrichment. No absence of consent is inferred as consent.

### 2.3 Customer API

**Base URL:** `/api/v1/customer`  
**Auth scopes:** `customers:read`; additionally `customers:identity:resolve` for resolution and `customers:sensitive:read` for approved unmasked fields.  
**Common headers:** `Authorization`, `X-Correlation-Id`, `X-Purpose`, `X-Actor-Id`, `X-Delegated-Subject` (agent only), `Accept: application/json`.

| Endpoint | Contract | Response / controls |
| --- | --- | --- |
| `POST /identity:resolve` | Resolve a restricted identifier for an explicit purpose. Body contains exactly one `identifier` object and optional `source_ref`; no bulk matching. | Returns `customer_id`, `match_state`, `consent_summary`, and decision ID. Requires elevated scope; audit every request and do not log raw identifier. |
| `GET /customers/{customer_id}` | Read authorized profile facets. Query: `fields`, `as_of`. | Returns masked fields by default, source freshness, consent summary, quality and lineage. Denies fields/purposes not allowed. |
| `GET /customers/{customer_id}/retail-context` | Read customer-safe purchase, affinity, and lifecycle features. Query: `window_days` (1–365), `store_id`, `as_of`. | Returns aggregates and segments only; no raw receipts or PII. Requires personalization/analytics purpose as applicable. |
| `GET /customers/{customer_id}/events` | Read authorized interaction/purchase event references. Query: `type`, `from`, `to`, `cursor`, `limit` (max 100). | Returns paged, redacted event facts and provenance; policy can aggregate or deny. |

Example identity-resolution request (restricted transport; identifiers excluded from application logs):

```json
{"identifier":{"type":"phone","value":"+86..."},"source_ref":{"system":"crm","record_id":"..."}}
```

Example profile response:

```json
{"customer_id":"cst_01J...","profile":{"display_name":"M***","lifecycle_stage":"active"},"consent":{"personalization":"granted","marketing":"withdrawn"},"quality":{"state":"certified","as_of":"2026-07-21T00:00:00Z"},"lineage":[{"source":"crm","ref":"lin_..."}],"policy":{"masked_fields":["phone","email"]}}
```

---

## 3. Retail recommendation APIs

Both services read certified Core facts and return decision support only. They have no write method and no side effect. Responses are snapshots: the caller must not treat a recommendation as an inventory reservation, a customer offer, a price instruction, or an approved task.

### 3.1 Product Recommendation API

**Endpoint:** `GET /api/v1/recommendations/products`  
**Scope:** `recommendations:product:read`; purpose must be `customer_service`, `clienteling`, `analytics`, or another approved value.

| Query field | Required | Meaning |
| --- | --- | --- |
| `customer_id` | one of this or `context_id` | Pseudonymous resolved customer; consent gate applies. |
| `context_id` | one of this or `customer_id` | Anonymous/session context with no identity resolution. |
| `store_id` | yes | Authorized store scope. |
| `channel` | yes | `store`, `ecommerce`, `service`, or `assistant`. |
| `limit` | no | 1–20, default 5. |
| `as_of` | no | ISO-8601 point-in-time request; defaults to latest certified snapshot. |

```json
{
  "request_id":"recp_...",
  "recommendations":[{
    "product_id":"prd_...",
    "rank":1,
    "reason_codes":["repeat_affinity","in_stock_at_store"],
    "confidence":0.78,
    "availability":{"state":"available","as_of":"2026-07-21T09:00:00Z"},
    "evidence":[{"type":"customer_feature","ref":"feat_..."},{"type":"product_fact","ref":"lin_..."}],
    "model":{"name":"product-ranker","version":"2026.07.1"}
  }],
  "policy":{"personalization_applied":true,"consent_basis":"granted"},
  "freshness":{"max_age_seconds":900},
  "disposition":"advisory_only"
}
```

If consent is absent/withdrawn, the service returns non-personalized, store/channel-appropriate ranking only and sets `personalization_applied: false`. It returns `409 CONTEXT_STALE` when the requested snapshot cannot be reproduced, `422 CONSENT_REQUIRED` when a requested personalized-only mode is not permitted, and `403 POLICY_DENIED` for scope violations.

### 3.2 Inventory Recommendation API

**Endpoint:** `GET /api/v1/recommendations/inventory`  
**Scope:** `recommendations:inventory:read`; caller must be authorized for the entity and store(s).  
**Query:** `store_id` (required), `horizon_days` (1–90, default 14), optional `product_id`, `category_id`, `as_of`, `limit` (max 200).

```json
{
  "request_id":"reci_...",
  "recommendations":[{
    "store_id":"store_nanshan",
    "product_id":"prd_...",
    "recommendation":"review_replenishment",
    "suggested_quantity":12,
    "priority":"high",
    "rationale":{"demand_window_days":30,"on_hand":3,"inbound":0,"projected_stockout_at":"2026-07-24"},
    "confidence":0.72,
    "constraints":["lead_time_unverified"],
    "evidence":[{"type":"inventory_position","ref":"lin_..."},{"type":"sales_aggregate","ref":"lin_..."}],
    "model":{"name":"inventory-advisor","version":"2026.07.1"}
  }],
  "freshness":{"inventory_as_of":"2026-07-21T09:00:00Z","sales_as_of":"2026-07-21T08:00:00Z"},
  "disposition":"advisory_only_no_order_created"
}
```

`suggested_quantity` is a planning value, not a replenishment order. The service suppresses recommendations when data is stale, quality is quarantined, demand is insufficient, or a policy constraint requires a planner review; it exposes the suppression reason instead of fabricating a value.

### 3.3 Shared API semantics

All endpoints use versioned JSON, UTC RFC 3339 timestamps, cursor pagination, `Idempotency-Key` only for internal draft creation, and a standard error body:

```json
{"error":{"code":"POLICY_DENIED","message":"Access is not permitted for the declared purpose.","correlation_id":"...","retryable":false}}
```

The Service Layer emits immutable access audit events containing principal, delegated subject, purpose, requested field set/scope, policy decision, response classification, correlation ID, and lineage references—but not raw identifiers or response payloads.

---

## 4. Activity Engine design

### 4.1 Purpose and state machine

The Activity Engine converts qualified business signals into explainable, human-owned work. It is an orchestration and observation layer, not an autonomous execution engine.

```text
observed → qualified → proposed → assigned → acknowledged → completed
                 │           │                  │
                 └→ suppressed / expired       └→ rejected / escalated
```

| Component | Responsibility |
| --- | --- |
| Signal intake | Consume authorized Core change events or scheduled certified snapshots; deduplicate by source event and rule version. |
| Qualifier | Check freshness, data quality, consent, policy, eligibility, thresholds, and rate/fatigue limits. |
| Recommender | Call product/inventory services, attach reasons/evidence/model details, and calculate priority. |
| Activity registry | Persist immutable activity IDs, state transitions, assignment draft, feedback, and audit trail. It does not persist a replacement inventory/customer truth. |
| Human work gateway | Surface an activity to an employee/manager; creates only a draft for an external governed workflow. |
| Outcome collector | Records observed outcome facts and employee feedback, separated from inferred success labels. |

An activity is keyed by `activity_id`; its idempotency/deduplication key is `(tenant, activity_type, subject_ref, source_event_ref, rule_version, window)`. State changes require an actor, timestamp, reason, correlation ID, and optimistic version. Expiry, suppression, and escalation are notifications/state changes only—never production commands.

### 4.2 Activity contract

```json
{
  "activity_id":"act_...",
  "type":"inventory_review",
  "subject":{"kind":"product_store","product_id":"prd_...","store_id":"store_nanshan"},
  "state":"proposed",
  "priority":"high",
  "proposal":{"recommended_action":"review replenishment quantity 12","disposition":"requires_human_approval"},
  "evidence_refs":["lin_...","rec_..."],
  "policy":{"decision":"allow","constraints":["planner_role_required"]},
  "expires_at":"2026-07-22T09:00:00Z",
  "audit_ref":"aud_..."
}
```

Permitted internal commands are `create-proposal`, `assign-draft`, `acknowledge`, `complete-with-outcome`, `reject`, `suppress`, and `escalate`. Any adapter to an operational workflow receives a human-approved task reference and is out of DATA-003 scope; no activity command is mapped directly to SAP/ERP/POS/WMS mutation.

---

## 5. Employee AI Assistant contract

The Assistant is a policy-bound client of the three brains and Activity Engine. It helps an employee understand facts, recommendations, approved knowledge, and task drafts; it is not an identity authority, policy authority, or autonomous operator.

| Contract element | Requirement |
| --- | --- |
| Identity and delegation | Assistant service identity plus authenticated employee identity, role, store/entity scope, declared purpose, and expiring delegation token. |
| Allowed tools | Customer read/resolve only when scope and purpose allow; product/inventory recommendation reads; approved knowledge retrieval; Activity Engine draft/feedback commands. No direct database, SAP, Core-sync, price, order, or inventory-write tool. |
| Answer format | Clearly label **fact**, **recommendation**, **unknown**, and **next human step**. Cite stable lineage/knowledge references, facts' `as_of`, freshness/quality, and model confidence where relevant. |
| Safety behavior | Ask for an authorized customer context before revealing customer-specific data; mask sensitive values; refuse denied scope; explain stale/quarantined data; never claim an action was performed unless confirmed by a governed workflow receipt. |
| Audit | Log tool request/decision/references, assistant version, prompt/template version, employee and delegation context, and outcome. Do not log raw PII or unrestricted conversation content. |

Minimal response envelope:

```json
{
  "answer":"Recommendation: review 12 units with the inventory planner.",
  "labels":["recommendation","human_approval_required"],
  "evidence":[{"kind":"inventory_recommendation","ref":"reci_...","as_of":"2026-07-21T09:00:00Z"}],
  "next_steps":[{"type":"create_activity_draft","requires_human_confirmation":true}],
  "limitations":["lead time is unverified"]
}
```

---

## 6. Growth loop design

The learning loop improves relevance and operational usefulness while preserving human control and source truth.

```text
certified fact + approved knowledge
 → recommendation / activity proposal
 → employee review (accept, edit, reject, reason)
 → governed workflow outcome reference
 → outcome measurement and bias/quality checks
 → offline evaluation + approval gate
 → versioned model/rule rollout with rollback
```

1. **Capture:** Store immutable recommendation version, evidence snapshot/ref, policy decision, employee feedback, and an outcome reference. Do not infer that an employee saw or accepted a suggestion merely from delivery.
2. **Measure:** Evaluate coverage, suppression rate, acceptance/edit/rejection reason, stockout/overstock proxy outcomes, customer-service outcomes where consent permits, freshness, and disparity across authorized segments/stores.
3. **Learn offline:** Train/evaluate only from retained, permitted, de-identified/minimized data. Separate correlation from causal claims; prevent outcome leakage and retain dataset/model lineage.
4. **Govern release:** Data owner, business owner, privacy/security, and model-risk approval are required for material rule/model changes. Use a versioned canary/shadow evaluation and a documented rollback target.
5. **Monitor:** Monitor drift, calibration, quality, consent changes, recommendation fatigue, policy denials, and incidents. Automatically suppress unsafe/stale recommendations; this is a presentation safeguard, not an operational action.

No growth-loop metric authorizes changing SAP, Core production synchronization, or any operational record. The only automated behavior permitted by this design is data retrieval, recommendation generation, audit/feedback capture, and suppression/escalation of an advisory activity.

---

## 7. Data model and governance contract

| Entity | Key fields | Source/retention notes |
| --- | --- | --- |
| `customer` | `customer_id`, `tenant_id`, `status`, `created_at`, `merged_into` | Minimal pseudonymous record; source facts remain in owning systems. |
| `identity_alias` | `alias_id`, `customer_id`, `identity_type`, `token_ref`, `match_state`, `verification_ref` | Restricted vault; token/secret separation; never returned in standard APIs. |
| `customer_consent` | `consent_id`, `customer_id`, `purpose`, `state`, `captured_at`, `evidence_ref`, `expires_at` | Append-only history, effective-state view; legal retention applies. |
| `retail_fact_ref` | `fact_ref`, `subject_type`, `subject_id`, `source_system`, `source_event_time`, `quality_state`, `lineage_ref` | Reference/curated fact metadata; SAP/ERP/POS/WMS remain authoritative. |
| `knowledge_asset` | `knowledge_id`, `version`, `owner`, `approval_state`, `classification`, `effective_from/to`, `source_ref` | Only approved/effective assets enter assistant retrieval. |
| `recommendation` | `recommendation_id`, `kind`, `subject_ref`, `model_version`, `reason_codes`, `confidence`, `evidence_refs`, `as_of`, `expiry` | Derived, immutable snapshot; not a business instruction. |
| `activity` | `activity_id`, `type`, `subject_ref`, `state`, `priority`, `assignee_ref`, `proposal_ref`, `audit_ref` | Workflow metadata only; state transition history is append-only. |
| `feedback_outcome` | `feedback_id`, `activity/recommendation_ref`, `actor_ref`, `decision`, `reason_code`, `outcome_ref`, `observed_at` | Separates human assertion from measured source outcome. |
| `access_audit` | `audit_id`, `principal`, `delegation`, `purpose`, `resource`, `policy_result`, `correlation_id`, `occurred_at` | Immutable security/audit record with minimized payload data. |

### 7.1 Required controls and acceptance criteria

- All API requests are authenticated, authorized, purpose-bound, rate-limited, and auditable; deny by default.
- Customer identity resolution never records raw identifiers in application logs, recommendation payloads, or analytics events.
- Every recommendation/activity response identifies evidence, freshness, quality, model/rule version, and `advisory_only` or `requires_human_approval` disposition.
- Stale, quarantined, consent-ineligible, or unauthorized data is denied/suppressed with an explainable code.
- Contract tests must verify field masking, tenant/store isolation, consent withdrawal, pagination limits, correlation/audit propagation, no-write API surface, idempotent activity proposal creation, and that no connector targets SAP or Core production synchronization for mutation.

## 8. Explicit exclusions

DATA-003 does **not** modify SAP; modify Core production synchronization; create/update/delete SAP, ERP, POS, WMS, inventory, prices, orders, customer source records, or production tasks; or automatically execute production operations. Any future write-back proposal requires a separate approved design, security review, workflow/approval contract, source-system owner approval, and auditable operational rollout.
