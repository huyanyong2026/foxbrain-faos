# FoxBrain Enterprise OS Master Blueprint

Version: 2026-07-13
Targets: `core.vafox.com`, `ai.vafox.com`, `huyan.vafox.com`
Current product surfaces: Enterprise Data Core, Enterprise AI, FoxBrain CEO Brain

## 1. Positioning

FoxBrain Enterprise OS is the enterprise second brain and AI operating system for Huohu Fox.

It is not an ERP replacement, a normal website, a BI dashboard, or only an AI chat page.

FoxBrain connects enterprise data, files, objects, knowledge, memory, graph relationships, rules, decisions, workflows and AI agents into one operating system.

Current operating boundary:

```text
core.vafox.com  = enterprise facts and read-only replicas
ai.vafox.com    = AI collaboration, agents, knowledge, tasks and feedback
huyan.vafox.com = CEO decisions, private memory and enterprise governance
```

AI suggestions must carry evidence and receive human confirmation before they become tasks, knowledge or CEO decision inputs.

## 2. Core Boundary

SAP Business One remains the core business data source and system of record.

FoxBrain is the system of intelligence:

- Reads SAP exports or read-only synchronized SAP data.
- Stores raw data and import history.
- Builds business objects, knowledge, graph relationships and decision evidence.
- Gives explainable, traceable and auditable recommendations.
- Does not directly modify SAP production data.
- Does not auto-execute high-risk business actions.

High-risk actions must go through human approval.

## 3. System Architecture

```text
FoxBrain Enterprise OS

|-- Enterprise Drive
|-- Enterprise Data Lake
|-- Object Engine
|-- Knowledge Engine
|-- Memory Engine
|-- Knowledge Graph
|-- Decision Engine
|-- Business Rule Engine
|-- Dashboard Engine
|-- AI Agent Center
|-- Workflow Engine
|-- Automation Engine
`-- Plugin Platform
```

## 4. Enterprise Data Flow

```text
SAP Data
  -> Enterprise Data Lake
  -> Business Calibration
  -> Object Engine
  -> Knowledge Engine
  -> Knowledge Graph
  -> Decision Engine
  -> Memory Engine
  -> CEO Dashboard
  -> Human Approval
  -> Workflow / Task / Execution Feedback
```

## 5. Engine Responsibilities

## Enterprise Drive

Enterprise asset entrance.

Stores and manages:

- SAP files
- Contracts
- Reports
- Photos
- Videos
- Training materials
- Business documents

Rule: every file is preserved and can become knowledge.

## Enterprise Data Lake

Raw enterprise data foundation.

Responsibilities:

- Save original files.
- Save import batches.
- Save row-level raw data.
- Save field mappings.
- Save source time.
- Preserve history without overwriting.

Rule: raw data is never destroyed.

## Object Engine

Enterprise cognition model.

Objects include:

- Company
- Store
- Brand
- Product
- Employee
- Customer
- Supplier
- Contract
- Project
- Decision
- Memory

Rule: do not randomly auto-create important business objects. Use Object Match Center for suggestions and human confirmation.

## Knowledge Engine

Turns enterprise information into searchable knowledge.

Sources:

- Documents
- SAP data
- Training content
- Business rules
- Reports
- Boss experience

Rule: knowledge must keep source, visibility, status and traceability.

## Memory Engine

Stores enterprise experience.

Examples:

- Decisions
- Meeting conclusions
- Reasons
- Risks
- Historical events
- Boss operating logic

Rule: accepted decision insights generate memory drafts, not silent irreversible execution.

## Knowledge Graph

Connects enterprise relationships.

Examples:

```text
Store 鈫?Sales 鈫?Product 鈫?Brand 鈫?Supplier
Brand 鈫?Inventory 鈫?Risk 鈫?Decision 鈫?Memory
Employee 鈫?Store 鈫?Customer 鈫?Purchase History
Document 鈫?Knowledge 鈫?Object 鈫?Decision
```

Rule: every graph relationship must have a source.

## Decision Engine

Provides evidence-backed CEO decision support.

Capabilities:

- Risk detection
- Inventory recommendations
- Brand recommendations
- Store recommendations
- Data quality warnings
- Decision actions

Rule: every decision insight must have evidence. AI must not invent business conclusions.

## Business Rule Engine

Stores visible, editable and auditable operating rules.

Examples:

- Inventory age rules
- Gross margin rules
- Brand dependency rules
- Data quality rules
- Approval rules

Rule: rules must not be hidden only in code.

## Dashboard Engine

CEO operating cockpit.

Displays:

- Business Health
- Decision Insights
- Inventory Intelligence
- Brand Intelligence
- Store Intelligence
- AI Ask Enterprise
- Recalculation entry

Rule: homepage should be simple. Details appear after click-through.

## AI Agent Center

Future digital employee foundation.

Agents include:

- CEO Agent
- Inventory Agent
- Brand Agent
- Store Agent
- Finance Agent
- Content Agent

Rule: every AI agent must have role, permission, tools, audit and evaluation.

## Workflow Engine

Turns decisions into execution.

Supports:

- Task creation
- Approval
- Notification
- Execution tracking
- Feedback

Rule: high-risk execution must wait for human approval.

## Automation Engine

Runs scheduled operations.

Examples:

- SAP read-only sync
- Data import jobs
- Business health calculation
- Decision rebuild
- Inventory analysis
- Daily report

Rule: automation may analyze and prepare tasks, but must not execute high-risk business changes automatically.

## Plugin Platform

Future integration layer.

Targets:

- SAP
- Enterprise WeChat
- CRM
- Ecommerce
- Content platforms
- API Gateway

Rule: integrations must have API governance, logs, permissions and rollback path.

## 6. Current Sprint Baseline

Completed baseline:

- Sprint001 Drive Foundation
- Sprint002 Object Engine
- Sprint003 Knowledge Pipeline
- Sprint004 Global Search + Timeline
- Sprint005 CEO Dashboard
- Sprint006 Memory Engine
- Sprint007 SAP Data Import Foundation
- Sprint008 Data Lake 鈫?Business Object Pipeline
- Sprint008.5 Business Calibration
- Sprint009 Knowledge Graph Foundation
- Sprint010 Decision Engine Foundation
- Sprint011 Business Rule Engine
- Sprint012 Business Health Engine
- Sprint013 Inventory Intelligence
- Sprint014 Brand Intelligence
- Sprint015 Store Intelligence
- Sprint015.5 Visible CEO Experience Upgrade

## 7. CEO Home Standard

The CEO homepage must show visible business value immediately.

Required visible sections:

- FoxBrain CEO Brain
- Business Health
- Decision Insights
- Inventory Intelligence
- Brand Intelligence
- Store Intelligence
- AI Ask Enterprise
- Recalculation entry
- Ten Owner OS entries

The homepage must not become a large menu tree. Deep hierarchy belongs inside each module.

## 8. Ten Owner OS Entries

The first-level owner home keeps ten entries:

- Enterprise
- Assets
- Archive
- Knowledge
- AI
- Decision
- Data
- Projects
- Strategy
- System

No additional first-level home category should be added without updating this blueprint.

## 9. Development Rules

Every sprint must be:

- Incremental
- Compatible
- Testable
- Deployable
- Reversible
- Documented

Every change must preserve:

- Existing login system
- Existing data
- Existing routes unless explicitly retired
- SAP production independence
- Human approval for high-risk actions
- Evidence for AI suggestions

## 10. GitHub and Deployment Flow

```text
GitHub
  鈫?Master Plan
  鈫?Epic
  鈫?Sprint
  鈫?Codex
  鈫?Branch
  鈫?PR
  鈫?User Confirmation
  鈫?Merge to main
  鈫?Server Pull
  鈫?Database Migration / Init
  鈫?Service Restart
  鈫?Smoke Test
```

## 11. Production Deployment Rules

Production directory must run the correct repository:

```text
/opt/foxbrain-faos
```

Production service:

```text
firefox-portal.service
```

Production deployed app:

```text
/opt/firefox-portal/portal.py
```

Before declaring deployment complete, verify:

- Current branch
- Current commit
- Service active
- Homepage reachable
- Key module pages reachable
- Login protection still works

## 12. Safety Rules

- Do not connect directly to production SAP for write operations.
- Do not install programs on the SAP production server unless explicitly approved.
- Do not auto-execute discount, purchase, inventory, price, finance or HR actions.
- Do not create decision recommendations without evidence.
- Do not hide business rules only in code.
- Do not delete existing capabilities during upgrade.
- Keep `ai.vafox.com` separate from the CEO private vault and from Data Core.
- Do not allow AI suggestions to bypass human approval.

## 13. Next Architecture Direction

Recommended next phases:

1. Make CEO Brain visibly useful every day.
2. Strengthen real SAP read-only sync into Data Lake and intelligence engines.
3. Improve Object Match Center human confirmation.
4. Build richer graph relationship pages.
5. Add task/approval workflow from accepted decision insights.
6. Prepare AI Agent Center with role, permission and audit.
7. Prepare plugin platform only after core CEO workflow is stable.


