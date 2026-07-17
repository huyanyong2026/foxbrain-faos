# VAFOX Core Data Hub Architecture

Version: Genesis-Construction-002  
Domain: `core.vafox.com`  
Purpose: enterprise nervous system for trusted data, events, Digital Twin preparation, AI context, and memory support.

## 1. Foundation Rule

Core is infrastructure, not a business dashboard. It protects the existing foundation and keeps SAP as the authoritative business system where SAP is the system of record.

Canonical chain:

```text
SAP
  ↓
Enterprise Data Hub
  ↓
Enterprise Digital Twin
  ↓
FoxBrain Intelligence Engine
  ↓
Mission Engine
  ↓
Home Experience
```

No home, AI surface, automation, or future ecosystem application may bypass Core for enterprise data.

## 2. Responsibilities

Core owns:

- SAP data ingestion.
- Multi-source data ingestion.
- Data validation.
- Event generation.
- Digital Twin preparation.
- AI context preparation.
- Memory support.
- API and security boundaries for enterprise data.

Core does not own:

- Dashboard presentation.
- Manual report center UX.
- Duplicate SAP business logic.
- Direct production SAP modification.
- Uncontrolled AI access to raw data.

## 3. Data Flow

```text
Source Systems
  ├─ SAP read-only integration
  ├─ Product / inventory / order sources
  ├─ Customer / supplier / partner sources
  ├─ Operational tools
  └─ Approved manual reference data
        ↓
Ingestion Layer
        ↓
Validation + Normalization
        ↓
Canonical Enterprise Data Hub
        ↓
Digital Twin Preparation
        ↓
AI Context Preparation + Memory Indexing
        ↓
Mission Engine + Home Experience APIs
```

Validation gates:

- Schema validation.
- Source authorization.
- Timestamp and freshness validation.
- Entity identity matching.
- Duplicate detection.
- Data lineage capture.
- Sensitive field classification.

## 4. Event Flow

Core emits events when trusted enterprise state changes.

```text
Data Change
  ↓
Validation Passed
  ↓
Canonical Entity Updated
  ↓
Event Generated
  ↓
Digital Twin Updated
  ↓
Mission / AI Context Invalidated or Refreshed
  ↓
Home Experiences Receive Updated Context
```

Event categories:

- Identity and relationship events.
- Organization and role events.
- Product, inventory, order, and finance events.
- Risk and anomaly events.
- Mission lifecycle events.
- Memory refresh events.

Every event must include:

- Event ID.
- Source system.
- Entity reference.
- Timestamp.
- Freshness level.
- Permission classification.
- Lineage reference.

## 5. API Boundary

Core exposes infrastructure APIs, not page-specific dashboard APIs.

API groups:

- Identity context API for Gateway.
- Enterprise entity API for trusted canonical entities.
- Event API for consumers and mission triggers.
- Digital Twin API for prepared enterprise state.
- AI context API for FoxBrain retrieval.
- Memory support API for approved memory reads and writes.

Boundary rules:

1. Homes request context, not raw source-system dumps.
2. AI retrieval must pass VID, role, permission snapshot, and purpose.
3. Mutating actions must go through workflow and runtime governance.
4. SAP production writes are out of scope for this foundation package.
5. API contracts must be versioned.

## 6. Security Boundary

Security layers:

- Gateway authenticates and resolves VID.
- Core authorizes enterprise data access.
- Runtime Governance AI-OS-V5.1 validates sensitive AI or automation behavior.
- Workflow handles approvals for material actions.
- Audit logs preserve lineage from source to answer to action.

Core must enforce:

- Default deny.
- Row / entity / field-level permission.
- Tenant or business-unit scoping when applicable.
- PII and confidential data masking.
- Prompt-context minimization for AI.
- Immutable audit trails for security decisions.

## 7. Data Freshness

Core publishes freshness metadata with every context response.

Freshness levels:

| Level | Meaning | Example Use |
| --- | --- | --- |
| Live | Near real-time or current operational event | urgent risk, order exception |
| Recent | Refreshed within accepted operational window | daily workforce home |
| Snapshot | Point-in-time trusted snapshot | CEO briefing |
| Stale | Outside freshness threshold | warning only, no autonomous action |
| Unknown | No verified timestamp | blocked from decision use |

Homes and AI answers must show or internally account for freshness when freshness affects decisions.

## 8. Digital Twin and AI Context Preparation

Core prepares enterprise state into structures usable by the Enterprise Digital Twin and FoxBrain Intelligence Engine:

- Canonical entity graph.
- Time-series business signals.
- Relationship maps.
- Risk indicators.
- Opportunity indicators.
- Mission-ready context packages.
- Permission-filtered AI retrieval chunks.

The Digital Twin is not a replacement for SAP. It is the operating representation of the enterprise used by FoxBrain, Mission Engine, and Home Experiences.
