# VAFOX M4.1 Knowledge Domain Model

**Status:** design baseline for additive M4.1 knowledge modelling.  
**Scope:** enterprise knowledge structure for the seven VAFOX domains: `company`, `brand`, `product`, `sales`, `store`, `sop`, and `activity`.  
**Implementation boundary:** this document defines a contract over the existing M3 Memory and M4 read-only Knowledge API. It does **not** change SAP, Core, Dify configuration, or agent execution.

## 1. Design principles

1. **One governed knowledge item, many retrieval views.** A Knowledge Item is an active Memory item with controlled `metadata.knowledge`; the Memory item remains the record of storage, ownership, lifecycle, and ACL.
2. **Domain first, not document first.** Every item has exactly one primary domain and may link to other domain entities. This keeps a product launch procedure (`sop`) distinct from the product it concerns (`product`).
3. **Evidence before assertion.** A claim is usable only with at least one immutable source locator or an explicitly recorded human assertion. Derived knowledge preserves its upstream lineage.
4. **Authorization before context.** Search, detail, Dify context assembly, and Enterprise Agent retrieval all use the server-derived authorization context. Client-provided owner, organization, department, visibility, or role filters never grant access.
5. **Read, recommend, cite; never execute.** This model can support retrieval and decision support only. It neither modifies SAP/Core nor permits Dify or an agent to run business actions automatically.

## 2. Logical knowledge schema

`knowledge_id` is the existing immutable Memory UUID. The authoritative envelope is the M3 `memory_items` record; its `metadata.knowledge` object is the M4.1 domain payload. This avoids a second ACL or content store.

```text
MemoryItem (knowledge_id)
  ├── governance: organization_id, owner_id, department_id, role_scope,
  │              visibility, status, created_at, updated_at
  ├── content: storage_path + content type/size
  ├── retrieval: tags + vector chunks
  └── metadata.knowledge: KnowledgeDescriptor
        ├── identity: schema_version, domain, type, title, summary, language
        ├── scope: company_id, brand_id, product_id, store_id, sales_scope
        ├── business: entity_refs[], relations[], effective_period
        ├── quality: lifecycle, review, freshness, confidence
        └── provenance: source_records[], lineage[], content_hash
```

### 2.1 KnowledgeDescriptor contract

| Group | Field | Requirement and rule |
| --- | --- | --- |
| Identity | `schema_version` | Required; initially `"m4.1"`. Consumers reject unknown major versions. |
| Identity | `domain` | Required enum: one of the seven domains below. Exactly one primary value. |
| Identity | `type` | Required controlled subtype, for example `policy`, `fact_sheet`, `procedure`, `playbook`, `event`, or `analysis`. |
| Identity | `title`, `summary`, `language` | `title` required; summary is retrieval-safe abstract; language is BCP-47, default `zh-CN`. |
| Scope | `company_id`, `brand_id`, `product_id`, `store_id` | Stable business identifiers, optional unless required by the domain/type rule. IDs are references, not copied SAP master data. |
| Scope | `sales_scope` | Optional `{region, channel, period}` object for a sales item or a linked sales context. |
| Business | `entity_refs` | Array of `{entity_type, entity_id, label?}` for related business entities. |
| Business | `relations` | Array of typed outgoing relations (Section 3.2); relation targets are `knowledge_id` or an entity reference. |
| Validity | `effective_from`, `effective_to` | ISO-8601 timestamps; absent end means open-ended. `effective_from` must not exceed `effective_to`. |
| Quality | `lifecycle` | `draft`, `in_review`, `approved`, `deprecated`, or `archived`. Only `approved` and currently effective content is eligible as default AI context. |
| Quality | `review` | `{status, reviewed_by, reviewed_at, review_note?}`. High-impact procedures, policies, and derived analyses require an approved review. |
| Quality | `freshness` | `{review_after, source_observed_at?}`. A past `review_after` is a warning for retrieval, not an authorization override. |
| Quality | `confidence` | `high`, `medium`, or `low`; source-backed facts use source evidence, while human assertions record the reviewer. |
| Provenance | `source_records` | Non-empty array defined in Section 5. One record is marked `primary: true`. |
| Provenance | `lineage` | Ordered upstream knowledge IDs and transformation descriptors for summaries, translations, or analyses. |
| Provenance | `content_hash` | SHA-256 of the canonical content representation; supports change detection without exposing content. |

Required top-level Memory fields remain `organization_id`, `owner_id`, `visibility`, `status`, `source`, `metadata`, and timestamps. A producer must write the domain metadata atomically with the Memory item. A consumer must treat missing/invalid domain metadata as non-domain Memory, not as a permissive default.

### 2.2 Canonical payload example

```json
{
  "schema_version": "m4.1",
  "domain": "product",
  "type": "fact_sheet",
  "title": "VAFOX Aurora serum product fact sheet",
  "summary": "Approved product positioning and usage constraints.",
  "language": "en",
  "company_id": "company:vafox",
  "brand_id": "brand:aurora",
  "product_id": "product:aurora-serum-30ml",
  "entity_refs": [{"entity_type": "brand", "entity_id": "brand:aurora"}],
  "relations": [{"type": "governed_by", "target_knowledge_id": "<approved-policy-uuid>"}],
  "effective_from": "2026-07-01T00:00:00Z",
  "lifecycle": "approved",
  "review": {"status": "approved", "reviewed_by": "user:product-owner", "reviewed_at": "2026-07-01T09:00:00Z"},
  "freshness": {"review_after": "2027-01-01T00:00:00Z", "source_observed_at": "2026-06-30T00:00:00Z"},
  "confidence": "high",
  "source_records": [{"source_id": "doc:product-brief-v3", "source_type": "approved_document", "locator": "minio://knowledge/product-brief-v3.pdf#page=2", "observed_at": "2026-06-30T00:00:00Z", "captured_at": "2026-07-01T08:00:00Z", "content_hash": "sha256:<digest>", "primary": true}],
  "lineage": [],
  "content_hash": "sha256:<digest>"
}
```

## 3. Seven-domain model

| Domain | Purpose | Required scope | Typical types | Key entity references |
| --- | --- | --- | --- | --- |
| `company` | Corporate strategy, organization facts, policies, decisions, and governance. | `company_id` | `policy`, `decision`, `organization_profile` | company, department, role |
| `brand` | Brand positioning, visual/voice rules, campaign principles, and brand assets. | `company_id`, `brand_id` | `brand_book`, `campaign_rule`, `asset_guideline` | brand, product, activity |
| `product` | Product facts, specifications, claims, lifecycle, usage, and product-related constraints. | `company_id`, `product_id`; `brand_id` when branded | `fact_sheet`, `specification`, `faq` | product, brand, SOP |
| `sales` | Sales playbooks, channel rules, price guidance, market observations, and approved analyses. | `company_id`, `sales_scope` | `playbook`, `pricing_guidance`, `analysis` | channel, product, store, activity |
| `store` | Store profile, local operating knowledge, merchandising, and local exceptions. | `company_id`, `store_id` | `store_profile`, `local_guideline`, `incident_note` | store, region, SOP, activity |
| `sop` | Versioned, reviewable operating procedures and checklists. | `company_id`; linked process target required | `procedure`, `checklist`, `control` | product, store, sales channel, role |
| `activity` | Campaigns, events, launches, and their approved plans or post-event evidence. | `company_id`, `activity_id` | `campaign_plan`, `event_brief`, `retrospective` | activity, brand, product, store, sales channel |

Domain identifiers are opaque, stable business references owned by their source system. The knowledge model does not create or update those source entities. A missing referenced entity is represented as an unresolved reference and blocks promotion to `approved` when the reference is required.

### 3.1 Domain cardinality rules

* A `company` item may relate to zero or more brands, products, stores, SOPs, and activities.
* A `brand` may relate to many products and activities; each branded `product` references at most one primary `brand_id` and may have additional brand references in `entity_refs`.
* A `sales` item can span multiple channels/stores through `entity_refs`; a store-specific sales instruction also carries `store_id`.
* An `sop` has one controlled procedure version per `knowledge_id`; superseding content is a new item linked with `supersedes` and deprecates the older item after approval.
* An `activity` may involve many brands, products, stores, and sales channels; outcome claims must cite observations separately from plans.

### 3.2 Relation vocabulary

Allowed relation types are `applies_to`, `belongs_to`, `governed_by`, `implements`, `mentions`, `supports`, `supersedes`, `derived_from`, `evidenced_by`, `replaces`, and `conflicts_with`. Relation objects contain exactly one target (`target_knowledge_id` or `{target_entity_type, target_entity_id}`), optional `valid_from`/`valid_to`, and optional source-record references. Consumers must not infer a relation from co-occurrence alone.

## 4. Metadata design and lifecycle

### 4.1 Separation of concerns

| Layer | Owner | Examples | Retrieval consequence |
| --- | --- | --- | --- |
| Memory envelope | M3 | UUID, owner, organization, visibility, tags, content path, active/deleted status | Mandatory authorization and deletion checks. |
| Knowledge descriptor | M4.1 producer/reviewer | domain, scope, relationships, review, freshness, provenance | Domain filters and citation payload. |
| Chunk metadata | indexing pipeline | `chunk_id`, offsets, embedding model/version, indexed timestamp | Citation precision and re-index diagnostics. |
| Response metadata | Knowledge API/adapter | query ID, score, applied filters, warning flags | Never becomes source truth or is persisted as a source. |

Tags are discovery aids only; they cannot replace `domain`, scope IDs, lifecycle, or ACL. Free-form metadata may be added under `metadata.knowledge.extensions.<namespace>`, but it cannot override a reserved field.

### 4.2 State transitions

```text
draft -> in_review -> approved -> deprecated -> archived
                 \-> draft (review changes requested)
```

Promotion to `approved` requires a valid primary source, a review record where required, valid scope references, no invalid effective period, and a content hash. `deprecated` remains retrievable only when explicitly requested for historical analysis and is labelled as such. Deleted Memory records are never retrievable regardless of lifecycle.

### 4.3 Index and filtering contract

Index only non-deleted records. Index fields suitable for server-side filters are `domain`, scope IDs, `lifecycle`, `effective_to`, `source_type`, `confidence`, and ACL-derived Memory fields. Retrieval may over-fetch candidates for semantic ranking, but the Knowledge API must re-read the envelope, verify active status and ACL, then enforce domain and all requested filters before returning a result. This preserves correctness when vectors, metadata, or permissions are stale.

## 5. Source traceability

Every returned answer or context block must carry citations sufficient for a human to locate the originating evidence. `source_records` use this minimum contract:

| Field | Meaning |
| --- | --- |
| `source_id` | Stable identifier in the source system or managed document registry. |
| `source_type` | Controlled value such as `approved_document`, `sap_readonly_snapshot`, `meeting_minutes`, `manual_assertion`, `external_reference`, or `derived_knowledge`. |
| `locator` | Immutable or versioned URI/path plus optional page, section, row, or offset. SAP references are read-only snapshots, never a write target. |
| `observed_at` | When the source fact applied or was observed. |
| `captured_at` | When VAFOX captured the evidence. |
| `content_hash` | SHA-256 of captured source content/version. |
| `primary` | Exactly one primary source per Knowledge Item. |
| `access_hint` | Optional non-authoritative visibility hint; access is still checked against the Memory envelope. |

For derived content, `lineage` records `{upstream_knowledge_id, transformation, transformed_at, transformed_by, input_hash}` for every material input. Permitted transformations include `extract`, `summarize`, `translate`, and `aggregate`; an AI-generated synthesis is labelled `aggregate` and remains non-authoritative until human review. Citation output includes `knowledge_id`, `memory_id`, source ID/type/locator, chunk ID and offsets where available, source hash, and retrieval timestamp. Never expose a locator or source text to a caller who lacks access to its parent Knowledge Item.

## 6. ACL compatibility

M4.1 relies on the existing trusted `AuthContext`: organization ID, user/owner ID, optional department ID, and role scopes. The service derives this context from trusted gateway identity headers or a verified JWT, never from query/body filters. The compatibility decision matrix is:

| Condition | Result |
| --- | --- |
| Different `organization_id` | Deny. |
| Same organization and requester is `admin` | Allow. |
| Same organization and requester owns the item | Allow. |
| Same organization and `visibility=organization` | Allow. |
| Same organization, `visibility=department`, matching department | Allow. |
| Any other case, including private item owned by another user | Deny. |

`domain`, `brand`, `product`, `store`, tag, lifecycle, and source filters can only narrow an already authorized result set. A Dify adapter or Enterprise Agent receives a mapped, server-authenticated context and must call the same read-only API; it cannot pass a different owner or obtain direct storage/vector access. When an agent acts for a user, the user remains the effective subject and the agent identity is recorded only as an audit actor.

## 7. Future integration contracts

### Knowledge API

The current read API maps `metadata.knowledge.domain`, `title`, and scope fields onto search/detail results. M4.1 adds a stable producer/consumer contract without requiring API mutation: producers populate the descriptor; consumers can progressively use `type`, lifecycle, provenance, and relations. Future cursor/filter additions must preserve server-side ACL revalidation and return the citation envelope above.

### Dify

Dify integration is API-first and read-only: a service-identity adapter maps the caller's trusted authorization context to Knowledge API retrieval, converts authorized results to context blocks, and retains citations. Dify must not write this model, alter a Dify dataset/provider/workflow, connect directly to M3/Qdrant, or become the ACL authority. A separately managed one-way replica, if ever needed, is rebuildable and uses the same metadata/citation schema.

### Enterprise Agent

An Enterprise Agent may retrieve approved, effective, ACL-visible items by domain and scope, then present grounded answers with citations and freshness/lifecycle warnings. It may propose a draft, escalation, or human approval request, but it cannot write SAP/Core, promote knowledge, change permissions, alter a source, or execute an action automatically. All retrievals should log request ID, effective subject, agent actor, applied filters, returned knowledge IDs, and source hashes.

## 8. Acceptance checklist

- [x] Seven primary domains have controlled names, purpose, scope, and relation rules.
- [x] The schema separates Memory governance from Knowledge domain metadata and retrieval chunks.
- [x] Metadata covers identity, scope, relationship, validity, lifecycle, quality, and extensions.
- [x] ACL uses the existing server-derived context and makes all business filters narrowing-only.
- [x] Every item and returned context has source, locator, hash, lineage, and citation requirements.
- [x] Knowledge API, Dify, and Enterprise Agent compatibility is read-only and citation-preserving.
- [x] No SAP/Core modification or autonomous agent execution is introduced by this model.
