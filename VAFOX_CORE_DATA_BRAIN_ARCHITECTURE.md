# VAFOX 2.0 Core Data Brain Architecture

**Domain:** `core.vafox.com`
**Positioning:** Enterprise Data Brain
**Document type:** Architecture design only; this document defines target principles, boundaries, and interfaces. It does **not** authorize or perform server access, server changes, database changes, or production operations.

---

## Architecture Overview

```text
gateway.vafox.com
        |
        v
huyan.vafox.com
CEO Control Plane / Decision Intelligence
        |
        v
AI Workforce Platform
        |
        | authorized, policy-evaluated data requests
        v
core.vafox.com
Enterprise Data Brain / Enterprise Fact Center
        ^
        |
SAP · ERP · business systems · store data · future system interfaces
```

**Core principle:** source systems retain ownership of their operational records; Core consolidates governed, traceable, versioned enterprise facts. Huyan and AI Workforce may reason over and act from authorized facts, but must not turn inference, conversation, or an Agent result into a replacement source of record.

---

## 1. Core Positioning

### 1.1 Definition

`core.vafox.com` is the **VAFOX Enterprise Data Brain**: the enterprise-wide fact center and governed data foundation. It converts fragmented source-system data into consistent, reusable business facts, while preserving each fact's origin, effective time, quality state, and access policy.

Core is not a replacement for SAP, ERP, or other transactional systems. Those systems remain authoritative for the business domains they own. Core provides the common data plane that allows authorized users, applications, AI Workforce, and Huyan to use the same validated view of enterprise reality.

### 1.2 Why Core is the enterprise fact center

Core is the enterprise fact center because it provides:

- **One governed meaning:** common business objects, identifiers, metrics, and semantic definitions across departments and systems.
- **Evidence before insight:** every material fact can be traced to a source, ingest time, transformation version, and quality result.
- **Time-aware truth:** source event time, effective time, load time, and correction/version history are retained so reports and decisions can be reproduced.
- **Controlled sharing:** data is exposed only through policy-enforced services rather than uncontrolled copies or direct database access.
- **Reusable foundation:** Huyan, AI Workforce, BI, operational applications, and future analytics consume shared facts instead of creating isolated data silos.

### 1.3 Architectural objectives

1. Establish a durable enterprise data contract without duplicating source-system business authority.
2. Make trusted facts discoverable, explainable, and reusable.
3. Support near-real-time events and governed batch ingestion according to each source's capability.
4. Enforce least-privilege access at the dataset, record, field, and purpose levels.
5. Keep AI outputs, recommendations, and derived predictions separate from source facts and clearly labeled.

---

## 2. Data Sources and Ingestion

### 2.1 Source scope

| Source | Typical facts | Integration posture | Authority boundary |
| --- | --- | --- | --- |
| SAP | finance, procurement, material, inventory, sales, supplier and master-data events | read-only approved API, export, event, or replication interface | SAP remains authoritative for SAP-owned transactions and master data. |
| ERP | orders, fulfillment, accounting, planning, inventory and master data | governed connector, scheduled extract, event subscription, or API | The originating ERP remains authoritative for its domain. |
| Business systems | CRM, POS, e-commerce, WMS, HR, workflow and customer-service events | documented API, event stream, file exchange, or approved connector | Each system owns its captured operational record. |
| Store data | store sales, inventory movement, staffing, local operations, devices and exceptions | store gateway/API, secure batch upload, or event feed | Store systems own local operational capture; Core standardizes enterprise use. |
| Future system interfaces | newly acquired systems, partner platforms, IoT, market data and new applications | versioned data contract and onboarding process | Authority, cadence, ownership, and quality rules are approved before activation. |

### 2.2 Ingestion contract

Every source integration must define an owner, business purpose, legal/retention classification, schema version, primary keys, change semantics, expected latency, quality thresholds, retry/idempotency behavior, and deprecation process. Core assigns an immutable ingestion identifier and captures source metadata for every accepted delivery.

Ingestion is **read-oriented**. A source-system correction remains a source-system responsibility; Core records the corrected version and its lineage rather than silently overwriting history. Write-back, if ever required, is a separately approved business workflow and never a side effect of a Core read or AI request.

### 2.3 Onboarding lifecycle

```text
Source owner approval
  → data contract and classification
  → connector security review
  → schema/quality validation in Raw
  → mapping and reconciliation in Clean
  → publish certified business objects in Analytics
  → expose governed Service API
  → monitor, audit, version, and review
```

---

## 3. Data Layer Model

```text
Sources
  ↓
1. Raw Layer          immutable captured evidence
  ↓
2. Clean Layer        standardized and reconciled enterprise data
  ↓
3. Analytics Layer    certified metrics, models, and decision-ready views
  ↓
4. Service Layer      policy-enforced APIs, data products, and event services
```

| Layer | Purpose | Permitted content and controls | Consumers |
| --- | --- | --- | --- |
| **1. Raw Layer** | Preserve original incoming evidence. | Source payload, source schema, receipt metadata, checksum, source event time, ingestion ID, and quarantine state. Append-only where feasible; access is tightly restricted. | Data engineering, governance, controlled reconciliation. |
| **2. Clean Layer** | Produce standardized, validated enterprise records. | Canonical IDs, normalized formats, deduplication, validation results, reference/master-data mapping, PII classification, and reconciliation status. Invalid or unresolved records remain visible as exceptions, not hidden. | Approved data products and analytics pipelines. |
| **3. Analytics Layer** | Provide certified, purpose-specific business understanding. | Curated subject areas, KPI definitions, aggregates, semantic models, feature sets, historical snapshots, and clearly labeled forecasts. Facts, derived measures, and AI predictions remain distinguishable. | Huyan, BI, approved workforce applications, analysts. |
| **4. Service Layer** | Deliver authorized data safely and consistently. | Versioned APIs, query services, event subscriptions, signed exports, catalog metadata, policy decision/enforcement, rate limits, and audit events. No consumer receives implicit database access. | Gateway, Huyan, AI Workforce, BI, future integrations. |

### 3.1 Cross-layer invariants

- Each record carries a source reference, data classification, owner, and lineage pointer.
- Transformations are deterministic, versioned, testable, and attributable to a release or approved rule version.
- Business facts are never relabeled as AI conclusions; predictions include model/version, input window, confidence, and generation time.
- A record can be restricted, masked, quarantined, superseded, or retired without erasing the audit trail required by policy.

---

## 4. Relationship Between Core and Huyan

Core and Huyan have distinct responsibilities:

| Core — Enterprise Data Brain | Huyan — CEO Control Plane |
| --- | --- |
| Supplies authorized, traceable enterprise facts and certified metrics. | Turns authorized facts into CEO-oriented situation awareness, prioritization, scenarios, and decision support. |
| Maintains data contracts, quality, lineage, access controls, and service interfaces. | Presents evidence, reasoning context, recommended decisions, and approval actions. |
| Does not make executive decisions. | Does not create independent business truth or bypass Core policies. |

The permitted decision path is:

```text
Core fact / metric / approved forecast
  → Huyan question, briefing, alert, or decision scenario
  → CEO review and approval where required
  → approved action through its governed operational workflow
```

Huyan must show the relevant fact timestamp, source/lineage reference, quality state, and any forecast or inference label. If Core reports incomplete, stale, or quarantined evidence, Huyan must surface that limitation rather than presenting a false certainty.

---

## 5. Relationship Between Core and AI Workforce

AI Workforce accesses Core only through the Service Layer using a declared identity, task purpose, scope, and authorization context. It receives the minimum data necessary to perform an approved task and must honor record-, field-, and purpose-level policies.

### 5.1 Authorized data-call flow

```text
AI Workforce Agent
  → declares agent identity, delegated user/role, task, purpose, requested data product
  → Core policy decision point evaluates RBAC + ABAC + data classification
  → Core service enforces scope, masking, filtering, rate and time limits
  → Agent receives authorized facts plus provenance and usage constraints
  → Agent produces a labeled output with evidence references
  → access and output-use events are audited
```

### 5.2 AI guardrails

- Agents cannot directly connect to Core storage or databases.
- An Agent cannot elevate its own role, reuse another user's entitlement, or access unrestricted exports.
- Retrieval is purpose-bound, time-bound, and revocable; sensitive fields are masked or denied unless explicitly authorized.
- AI-generated summaries, anomalies, recommendations, and predictions are **derived intelligence**, not factual source records.
- Any operational action requires the applicable workflow, approval, and source-system authority; an AI read must never imply write authority.

---

## 6. Data Agent Relationship

Data Agents are governed consumers and stewards of enterprise data, not alternate data stores or privileged backdoors.

```text
Data Agent
  ↓  validate, retrieve, reconcile, explain, and monitor within policy
Core
  ↓  authorized facts, evidence, certified metrics, and quality signals
Huyan CEO
  ↓  decision intelligence, prioritization, and human approval
Governed business workflow / source system
```

### 6.1 Data Agent responsibilities

1. Request only approved Core data products for an explicit task purpose.
2. Detect data-quality anomalies, schema drift, freshness issues, and reconciliation exceptions.
3. Produce explainable findings with Core evidence references and confidence/quality context.
4. Submit remediation suggestions or data issue tickets; it must not silently alter source or Core records.
5. Escalate material risks to Huyan with the affected scope, impact, evidence, and recommended human decision.

---

## 7. Data Permission Model

Core combines **RBAC** (who the requester is) and **ABAC** (what context, data attributes, purpose, location, time, and risk conditions apply). Access is deny-by-default and is granted through the Service Layer only.

| Principal | Default data scope | Typical rights | Explicit limits |
| --- | --- | --- | --- |
| **CEO** | enterprise-wide decision-ready views, subject to legal and highly sensitive-data controls | view certified enterprise facts, KPIs, exceptions, and authorized decision evidence | no implicit access to raw personal/sensitive data; no direct database change. |
| **Executive** | assigned business domain, legal entity, region, and management responsibility | view/manage approved domain analytics and controlled exports | cannot access unrelated domains or bypass classification/masking. |
| **Employee** | least-privilege role, task, team, and location scope | use operational data products required for approved work | cannot query enterprise-wide data, raw data, or restricted fields by default. |
| **Agent** | explicit delegated scope plus narrowly defined task purpose | retrieve approved fields through an API; generate labeled derived results | no standing broad access, direct storage access, privilege escalation, or autonomous data modification. |

### 7.1 Policy enforcement requirements

- Strong identity authentication and service-to-service authentication are required.
- Authorization decisions evaluate role, department, entity, region/store, data classification, purpose, consent/retention constraints, device/session risk, and time.
- Enforcement supports row-level filtering, column/field masking, aggregation thresholds, export controls, and step-up approval for sensitive use.
- Delegation to an Agent is explicit, bounded, attributable to the delegating principal, and automatically expires.
- Every access decision—allow, mask, filter, and deny—is auditable.

---

## 8. Data Governance

| Governance domain | Design requirement |
| --- | --- |
| **Quality** | Profile completeness, validity, uniqueness, consistency, timeliness, and reconciliation to source totals. Define owners, thresholds, exception queues, and remediation SLAs per data product. |
| **Version** | Version schemas, mapping rules, transformation code, business definitions, APIs, and data contracts. Preserve effective dates and approved change records; support compatibility and deprecation windows. |
| **Lineage** | Track source → ingestion → Raw → transformation → Clean → Analytics → Service consumer. Lineage must identify source record/batch, rule version, owner, and timestamps. |
| **Audit** | Record identity, purpose, policy outcome, data product/version, fields/scope, time, action, correlation ID, export/output reference, and administrative policy changes. Protect audit logs from alteration. |
| **Backup** | Back up data, metadata/catalog, policy configuration, keys/configuration references, and recovery runbooks on defined schedules. Test recoverability, not only backup completion. |

Data ownership is assigned per domain. A data steward owns definition and quality; a technical owner owns the pipeline and operational health; a security/privacy owner approves classification and sensitive-use controls; the source owner remains accountable for source correctness.

---

## 9. Security Boundaries

Core is a protected data plane, not an administrative access path. The following are prohibited for users, applications, Agents, and AI workflows unless a separately governed break-glass process explicitly authorizes an exceptional action:

- **SSH:** no SSH access is used as a data-consumption mechanism or granted to bypass Core APIs.
- **Server modification:** Core requests and AI tasks cannot modify servers, runtime configuration, operating systems, or infrastructure.
- **Direct database modification:** no direct database write, update, delete, DDL, or ad hoc administrative connection is allowed through Core consumption interfaces.
- **Permission bypass:** no shared credentials, hidden superuser path, direct storage access, token replay, policy override, or indirect access through another principal is permitted.

Additional boundaries:

- Network access is segmented; storage and internal processing services are private and not internet-facing.
- Secrets are managed outside application code, rotated, and never included in data payloads, prompts, logs, or exports.
- Service APIs authenticate callers, validate requests, enforce quotas, and return only policy-approved data.
- Sensitive data is classified and protected in transit and at rest; data minimization applies to prompts, caches, and AI context.
- Security events, denied requests, unusual export patterns, and policy changes feed monitoring and alerting.

---

## 10. Backup, Recovery, and Disaster Recovery

### 10.1 Backup strategy

| Asset | Strategy | Recovery objective design |
| --- | --- | --- |
| Raw data | immutable, encrypted snapshots plus source/batch manifests; retention by policy | restore evidence without losing source provenance. |
| Clean and Analytics data | scheduled full backups plus incremental/point-in-time recovery where supported | restore a consistent certified view and rebuild derived products when necessary. |
| Metadata and governance | catalog, schemas, lineage, policies, access configuration, transformation versions, and audit indexes backed up independently | restore the ability to interpret and govern recovered data. |
| Service configuration | version-controlled deployment/configuration references and protected secret references | rebuild service interfaces without exposing credentials. |
| Audit evidence | append-protected, independently retained audit archive | preserve investigation and compliance evidence. |

Backups follow encrypted storage, segregation from the primary failure domain, retention schedules, integrity checks, access control, and periodic restore testing. Exact RPO/RTO values are set per data product based on business criticality; they must be documented and approved before production onboarding.

### 10.2 Recovery flow

```text
Detect incident
  → declare severity and protect evidence
  → stop unsafe writes/ingestion as needed
  → select approved recovery point
  → restore platform metadata and access policies
  → restore Raw evidence and required curated data
  → rebuild/replay governed transformations
  → reconcile counts, checksums, quality rules, and source totals
  → validate Service Layer policy enforcement
  → business owner acceptance
  → resume in controlled stages and record post-incident review
```

Recovery must preserve data lineage and distinguish restored historical state from new post-recovery data. No recovery is complete until technical checks, security validation, and business reconciliation pass.

### 10.3 Disaster recovery

Disaster recovery uses a geographically/failure-domain separated recovery capability, documented dependency inventory, protected recovery credentials, replicated backups, and a tested runbook. DR exercises validate not only infrastructure availability but also identity/policy restoration, catalog/lineage availability, source re-ingestion, reconciliation, and safe reactivation of Huyan and AI Workforce consumers.

---

## 11. Future Expansion

Core 2.0 is designed as a stable enterprise data foundation for the following additions:

| Capability | Extension through Core |
| --- | --- |
| **BI** | Governed semantic models, certified KPIs, row/field-secured dashboards, and reproducible report snapshots. |
| **Data warehouse** | Scalable historical storage and workload separation while retaining Core contracts, lineage, and policy enforcement. |
| **Predictive models** | Versioned feature sets, training-data lineage, model registry, monitoring, bias/quality review, and prediction labeling. |
| **Supply-chain analytics** | End-to-end supplier, procurement, inventory, logistics, demand, service-level, and risk views with source evidence. |
| **Future domain intelligence** | New data products and agents can be added through versioned contracts without breaking existing consumers or weakening governance. |

All expansion paths preserve the separation of concerns: **Core holds governed enterprise facts; Huyan provides decision intelligence; AI Workforce performs authorized task intelligence; source systems remain the operational systems of record.**

---

## Target-State Acceptance Criteria

The VAFOX Enterprise Data Brain design is realized when:

1. Every onboarded data product has an approved owner, contract, classification, quality threshold, and lineage.
2. Core exposes data only through governed services—not direct database access—and authorization is enforced and audited.
3. Huyan can show CEO decision evidence with freshness, quality, and provenance context.
4. AI Workforce and Data Agents receive only task- and policy-authorized data, with no standing privilege to modify Core or source systems.
5. Backups, recovery, and DR are documented, monitored, and regularly tested against approved recovery objectives.
6. Security boundaries prohibit SSH-based data consumption, server modifications, direct database changes, and permission bypasses.
