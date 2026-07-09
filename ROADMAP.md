# FoxBrain Roadmap

## Current Priority

1. FoxBrain OS 2.0 compatibility-first master upgrade.
2. FoxBrain OS 3.0 AI Operations Center, AI Task Planner, approval-then-execute and business feedback loop.
3. FoxBrain OS 4.0 Enterprise Digital Workforce with governed AI digital employees.
4. FoxBrain OS 5.0 Enterprise Digital Brain with explainable, traceable and auditable AI recommendations.
5. FoxBrain OS 6.0 Enterprise AI Platform with plugin system, Integration Hub, API governance, multi-company and multi-brand readiness, developer docs and platform monitoring.
6. Minimal home page: keep the first screen as a clean entrance layer, then show content hierarchy after click-through.
7. Unified architecture and maintainability improvements without deleting existing capabilities.
6. Unified data service for SAP B1, archives, knowledge, memory, tasks and reports.
7. AI collaboration across Jarvis, AI CEO and specialist agents with cited evidence and approval gates.
8. Production stability: health checks, backup, rollback, deployment notes and smoke tests.
6. Cloud stable running.
7. SAP integration layer.
8. Enterprise knowledge platform.
9. CEO dashboard, command center and daily action board.
10. Security, backup and monitoring.

## FoxBrain OS 2.0 Direction

- Treat the V5 progress package as the overall FoxBrain OS 2.0 target.
- Preserve Pack 18 Growth Engine, Pack 19 Executive Command Center and Pack 20 Release 1.0 capabilities.
- Prefer additive APIs, compatibility wrappers and service extraction over rewrites.
- Keep AI recommendations separate from raw business data and require sources, limitations and approval boundaries.
- Continue producing documentation, tests, release notes and architecture review records for every major batch.

## FoxBrain OS 3.0 Direction

- Build AI Operations Center as the management console for AI plans, approvals, execution status and feedback.
- Build AI Task Planner to convert business goals into reviewable, risk-classified plans.
- Implement approval-then-execute for safe internal actions only.
- Keep all high-risk actions human-approved and blocked from automatic execution.
- Use business feedback as the loop for improving future AI plans and recommendations.

## FoxBrain OS 4.0 Direction

- Build Enterprise Digital Workforce as the governed registry for AI digital employees.
- Every digital employee must declare role, permissions, tool scope, approval rule, audit policy and performance policy.
- High-risk operations remain human-approved and cannot auto execute.
- Agent runs, operation plans and activity logs form the audit trail.
- Performance evaluation tracks output quality, safety, feedback and high-risk blocking.

## FoxBrain OS 5.0 Direction

- Build Enterprise Digital Brain as the explainable recommendation and decision-support layer.
- Keep SAP B1 as the core business data source.
- Require every AI recommendation to expose explanation, evidence, lineage, limitations and audit status.
- Connect digital workforce, AI operations, enterprise brain, decision engine and approval governance.
- High-risk operations remain human-approved and cannot auto execute.

## FoxBrain OS 6.0 Direction

- Build Enterprise AI Platform as the governed platform layer above OS 1.0 to 5.0.
- Complete plugin system, Integration Hub, API governance, multi-company and multi-brand readiness, developer documentation and platform monitoring.
- Keep the home page minimal: no deep hierarchy or explanatory small text on the first screen.
- SAP B1 remains the core business data source.
- High-risk plugin, integration, API, SAP writeback and external publishing actions require human approval.

## FoxBrain OS 6.1 Direction

- Upgrade the knowledge base with SAP smart knowledge generation.
- Generate AI-queryable knowledge cards from synced brands, products, stores, employees, customers and suppliers.
- Keep generated knowledge traceable to source table, source key, snapshot and audit log.
- Keep the flow read-only for SAP; no SAP writeback is allowed from knowledge generation.
- Improve page intelligence inside the knowledge section while keeping the home page minimal.

## FoxBrain OS Enterprise V1.0 Architecture Refactor

- Execute the Enterprise V1.0 upgrade as an architecture refactor, not a page-only update.
- Stage 0: audit the current V6 structure, risks and compatibility boundaries.
- Stage 1: add an Enterprise V1.0 architecture contract module and expose it through the platform API.
- Stage 2: extract SAP, knowledge and retrieval logic behind service contracts.
- Stage 3: extract AI Operations, approvals and Digital Workforce services.
- Stage 4: harden monitoring, release gates, developer docs and rollback procedures.
- Every stage must produce docs, tests and a stage result record.

## FoxBrain Enterprise Second Brain V1.0 Direction

- Productize FoxBrain as an Enterprise AI Operating System and enterprise second brain.
- Treat FireFox as the first complete landing case while preparing a reusable ai.vafox.com platform core.
- Establish the 12-book product specification system before expanding features.
- Build the five core engines: Object Engine, Knowledge Engine, Memory Engine, Decision Engine and Relationship Engine.
- Keep SAP Business One as the stable production system of record.
- Keep high-risk AI actions approval-gated, explainable, traceable and auditable.
- Use `/second-brain` and `/api/second-brain` as the protected product baseline surface.

## FoxBrain Enterprise Second Brain V1.1 Direction

- Upgrade FoxBrain Drive into Drive 2.0: Enterprise Knowledge Drive.
- Build Object Engine so company, store, brand, product, customer, document and memory share a canonical object model.
- Build Knowledge Pipeline: Document -> OCR -> Chunk -> Embedding -> Vector DB -> Graph -> AI Summary -> Knowledge Object -> Agent.
- Rework the root dashboard contract as CEO Home while keeping the visible home page to ten entries only.
- Add `/drive`, `/objects`, `/knowledge-pipeline` and `/ceo-home` as click-through details.
- Keep SAP as system of record and require review for sensitive AI summaries and high-risk operations.

## FoxBrain OS Enterprise V1.1 Direction

- Integrate AI Knowledge Brain into the existing Enterprise V1.0 architecture.
- Focus on SAP data understanding and enterprise knowledge base readiness.
- Add query planning so AI answers know when to retrieve SAP, knowledge or both.
- Keep existing routes and portal behavior compatible.
- Do not invent SAP facts; cite sources or show limitations.

## FoxBrain OS Enterprise V1.2 Direction

- Integrate Business, Inventory, Membership and Content agents into the existing Agent framework.
- Do not refactor the database; reuse existing Agent, approval and audit tables.
- All AI execution requests must create approval plans before any action.
- Keep SAP B1 as the core business data source and route AI context through SAP understanding and the knowledge brain.
- Continue Stage 3 service extraction while keeping legacy routes compatible.

## FoxBrain OS Enterprise V1.3 Direction

- Connect SAP daily sync, AI analysis, boss daily report, task center and approval flow into one automatic operation loop.
- Keep SAP production server independent and read-only.
- Generate reviewable daily loop plans instead of auto executing high-risk operations.
- Use existing `ai_operation_plans`, `/api/ai-task-planner`, `/api/tasks` and `/api/approvals` without rebuilding.
- Treat boss daily reports as AI drafts with SAP evidence and human review boundaries.

## FoxBrain OS Enterprise V1.4 Direction

- Build SAP Knowledge Engine as a data and knowledge service, not a page-first feature.
- Establish SAP read-only sync layers and downstream AI data warehouse contracts.
- Model product, sales, inventory and member knowledge with facts, relationships, AI use cases and approval boundaries.
- Do not directly connect to modify SAP production database and do not write back to SAP.
- Reuse existing SAP knowledge mappings, snapshots and knowledge generation foundation.

## FoxBrain OS Enterprise V1.5 Direction

- Improve knowledge-base quality through scoring, review readiness and retrieval readiness.
- Build AI learning as reviewed context learning, not autonomous model training.
- Deposit boss operating principles, decisions, preferences and feedback into governed memory.
- Use existing knowledge, memory, decision and feedback tables without rebuilding.
- Keep sensitive and high-risk content approval-gated before active AI use.

## FoxBrain OS Enterprise V1.6 Direction

- Establish a governed multi-agent collaboration system on top of the existing Agent framework.
- Let CEO, Business, Inventory, Product, Member and Content agents share SAP Knowledge Engine context.
- Use SAP Knowledge Engine, AI data warehouse and knowledge quality as the shared source context.
- Reuse existing `ai_operation_plans` and audit flow without rebuilding the database.
- Keep high-risk operations blocked until human approval and keep SAP production read-only.

## FoxBrain OS Enterprise V1.6.5 Direction

- Build Knowledge Fusion Engine instead of adding page-only features.
- Fuse SAP enterprise knowledge, reviewed external industry knowledge and reviewed boss experience knowledge.
- Let existing CEO, Business, Inventory, Product, Member and Content Agents retrieve fusion context.
- Treat SAP as the factual base, external industry knowledge as context and boss experience as reviewed operating logic.
- Keep high-risk recommendations approval-gated and keep SAP production read-only.

## Business Radar UI Rule

- Business Radar is an independent section at `/business-radar`.
- The home page must stay minimal and show Business Radar as an entry only.
- Do not expand Business Radar metrics, insights, actions or evidence on the home page.
- Business Radar data is served through `/api/business-radar`.

## FoxBrain OS Enterprise V1.6.6 Direction

- Build the Knowledge Training Rules Engine on top of V1.6.5 fusion knowledge.
- Convert SAP data, reviewed external knowledge and boss operating experience into training signals.
- Maintain an operating rule library for FireFox business, inventory, product, member, content and governance logic.
- Make AI recommendations follow FireFox operating rules, source priority and decision guardrails.
- Keep rule changes and high-risk execution approval-gated.

## FoxBrain OS Enterprise V1.7 Direction

- Upgrade FoxBrain from AI knowledge assistant to AI business management system.
- Add AI Business Center with daily report, sales forecast, inventory analysis, profit analysis, risk warnings, AI advice and AI task center.
- Persist forecasts, inventory analysis, risk alerts, business memory and AI recommendation history.
- Keep SAP as readonly source of truth and keep high-risk execution blocked until boss approval.
- Make the acceptance request `分析一下南山店最近经营情况` call SAP sales, SAP inventory, brand profiles and operating rules before generating problem, cause, advice and execution plan.

## FoxBrain OS Enterprise V1.8 Direction

- Upgrade FoxBrain from AI business analysis to AI workflow automation.
- Build Workflow Builder, AI task center, approval center, notification center, execution records and automation rules.
- Let AI discover problems, create tasks, notify owners, wait for approval, track execution and collect feedback.
- Upgrade AI digital employees with responsibilities, tool scope, approval rules, memory and performance metrics.
- Convert the knowledge base into an enterprise experience base through decision feedback and business cases.
- Keep all high-risk execution blocked until human approval.

## FoxBrain OS Enterprise V1.9 Direction

- Build Enterprise Knowledge Graph so AI understands company, stores, brands, products, suppliers, employees, customers, sales and activities as connected entities.
- Build Entity Center and relationship APIs on top of SAP, Knowledge Center, workflow records and task records.
- Build AI Permission Engine for employee, store manager, boss and admin data scopes.
- Upgrade AI digital employees with role-based knowledge, tools, workflows, memory and performance policies.
- Add Employee AI Assistant, Customer AI Assistant and Business Cockpit Map contracts.
- Run the Knowledge Graph Builder daily at 02:30 without SAP writeback.

## FoxBrain OS Enterprise V2.0 Direction

- Build AI digital employee teams and enterprise auto-operation system.
- Move from single-agent suggestions to coordinated AI teams with role permissions, shared graph context and workflow execution.
- Strengthen approval routing, KPI accountability, cross-agent task handoff and closed-loop learning.

## FoxBrain OS Enterprise V2.1 Direction

- Build FoxBrain Digital Twin to mirror company, stores, brands, products, employees, suppliers, customers, finance and operating rules.
- Add business simulation sandbox for discount adjustment, new store, brand mix, relocation and future order pickup.
- Add prediction models for cashflow, inventory, store operations, employee capability and investment payback.
- Add AI Strategy Agent and AI Board Assistant for strategic reports.
- Keep every simulation sandboxed; execution requires human approval.
- Add simulation feedback loop to compare prediction with actual results and improve model accuracy.

## FoxBrain OS Enterprise V2.2 Direction

- Build AI autonomous operations center and enterprise autopilot mode.
- Let AI inspect the company daily, detect problems, schedule tasks and escalate only key decisions to the boss.
- Add stronger monitoring, rollback, approval routing and business-result accountability.
- Add Business Health Score, Daily Inspection, Early Warning, Action Engine, Rule Evolution and Chairman Agent.
- Keep autopilot execution approval-gated while alerts, tasks, reports and learning records are persisted.

## FoxBrain OS Enterprise V2.3 Direction

- Build AI ecosystem connection center for ERP, CRM, Enterprise WeChat, supply chain, members and content platforms.
- Make FoxBrain the central brain across FireFox commercial ecosystem connections.
- Add connector health monitoring, data contract governance, cross-system identity mapping and event-driven sync.
- Add Enterprise Data Lake, WeCom CRM Agent, AI CRM Manager, ecommerce connector, AI Content Factory and API Gateway.
- Keep external sends, API permission changes and connector key changes approval-gated.

## FoxBrain OS UX 2.0 Direction

- Treat the 7.8 private AI upgrade suggestion as the product experience priority before adding more pages.
- Keep the home page as four first-layer entries only: Business, AI, Messages and Me.
- Move detailed dashboards, numbers, modules and explanations into click-through pages.
- Keep AI as an independent center, similar to a direct chat entrance, with knowledge, agents and tasks under it.
- Keep global search and the AI entrance fixed across logged-in pages.
- Keep mobile bottom navigation focused on Business, AI, Messages and Me.
- Remove explanatory small text from the home page.
- Follow one page one subject, at most eight entries per layer, and find anything within three steps.
- Keep Business Radar and other advanced capabilities as independent sections, not expanded on the home page.

## FoxBrain Owner/Enterprise OS 7.9 Direction

- Define `huyan.vafox.com` as FoxBrain Owner OS: the boss private enterprise brain for assets, contracts, structure, capital, decisions and private knowledge.
- Define `ai.vafox.com` as FoxBrain Enterprise OS: the employee-facing operating and collaboration system for stores, employees, members, WeCom, promotion and daily execution.
- Do not fully merge the two systems; use partial synchronization with explicit data boundaries.
- Allow summaries and operational views such as stores, brands, supplier profiles, contract summaries, employee basics, member summaries, sales data, rent summaries, inventory analysis and training policies.
- Block personal capital, equity structure, family company data, firewall company data, core contract originals, sensitive finance documents, executive decision records and owner operating notes from syncing to the employee system.
- Keep SAP on an independent server as original operating data, then sync read-only into the data middle platform before publishing permissioned views.
- Build role boundaries for owner, finance, store manager, employee and customer before connecting SAP, Enterprise WeChat, mini programs and official accounts.

## FoxBrain Owner OS V1 Foundation Direction

- Pause Enterprise OS implementation until the Owner OS foundation is stable.
- Position `huyan.vafox.com` as FoxBrain Owner OS: the owner's enterprise second brain and system of intelligence.
- Keep the Owner OS home page to ten fixed centers only: Enterprise, Assets, Archive, Knowledge, AI, Decision, Data, Projects, Strategy and System.
- Build ten Owner OS centers: Enterprise, Assets, Archive, Knowledge, AI, Decision, Data, Project, Strategy and System.
- Establish the FoxBrain Master Blueprint as the single highest design standard.
- Maintain four long-term documents: Product Constitution, Product Specification, Technical Architecture and Development Handbook.
- Keep SAP as the independent system of record; Owner OS reads synchronized copies and never installs AI or experiments on SAP.
- Use V1 Foundation for enterprise, asset, archive, knowledge and AI foundations before moving to memory, data and Enterprise OS execution.

## FoxBrain Owner OS V1.0 Master Blueprint Direction

- Stop feature-first development and complete the V1.0 blueprint before adding more pages.
- Treat the ten centers as permanent first-level architecture; do not add new first-level menus.
- Owner OS is not ERP: SAP owns sales, purchase and inventory transactions.
- Owner OS is not OA: employee routine execution belongs to Enterprise OS.
- Make every important object knowledge with archive, summary, risk, timeline, version and relationships.
- Make AI the default owner entry for asking questions with evidence, limitations and approval boundaries.

## FoxBrain OS Enterprise V2.4 Direction

- Build AI commercial growth engine and automatic sales system.
- Turn customer, product, content and channel data into proactive sales growth tasks.
- Add campaign simulation, lead scoring, offer recommendation, employee follow-up and revenue attribution.

## V6 Next Tasks

- Foundation Pack 01 alignment: repository standards, environment configuration, structured logging, authentication, authorization, agent registry, SAP connector abstraction, knowledge service, workflow scheduler, CI/CD, tests and documentation.
- Pack 02 SAP and AI framework: keep SAP as system of record, expose connector contracts, keep write-back disabled until explicit business rules are approved, and connect AI agents through a shared registry.
- Pack 03 enterprise knowledge platform: document ingestion, OCR interface, metadata, chunking, embeddings, hybrid search contract, governance, permissions, citations and knowledge graph relationships.
- Pack 04 unified multi-agent framework: shared runtime, role permissions, versioned tools, memory abstraction, approval gates and audit logging for all agents.
- Pack 05 unified dashboard framework: KPI data service, independent alert service, independent AI recommendation service and evidence-based management review.
- Pack 06 unified automation framework: scheduler, retry policy, approval routing, notification center, audit logs and high-risk action blocking.
- Pack 07 Enterprise Brain: permissioned enterprise memory, evidence-based decision engine, forecast/simulation contracts and AI Council skeleton.
- Pack 08 unified enterprise portal: SSO foundation, role-based navigation, shared responsive components, message center and task center.
- Pack 09 enterprise memory: long-term memory repository, timeline, permission-aware retrieval, decision history and AI Agent memory collaboration.
- Pack 10 Release 1.0 production readiness: integration validation, repeatable deployment, observability, rollback and production checklist.
- Pack 11 security governance: RBAC, audit export, data classification, backup recovery governance and approval controls.
- Pack 12 SDK marketplace: plugin-first extension design, versioned SDK contracts, marketplace registry and backward compatibility guarantees.
- Pack 13 data intelligence: unified KPI catalog, metrics service, data quality monitoring, trend APIs and evidence-based AI insights.
- Pack 14 digital twin: enterprise entity model, relationship graph, historical state engine, sandbox simulation and visualization contracts.
- Pack 15 decision engine: explainable recommendations, risk scoring, opportunity discovery and approval gates for high-risk operations.
- Pack 16 AI Strategy Center: KPI-linked OKRs, strategy models, multi-scenario comparison, expansion planning and strategic dashboard.
- Pack 17 FoxBrain University: enterprise learning catalog, role paths, AI Tutor, certifications, progress tracking and knowledge feedback.
- Pack 18 Growth Engine: traceable growth scoring for stores, brands, products and customers with executive scorecards.
- Pack 19 Executive Command Center: unified management entrance for cockpit, risk center, AI Command, system health and module monitoring.
- Pack 20 Release 1.0: architecture integration review, interface consistency, documentation, tests and production release gate.
- Replace placeholder worker jobs with real knowledge indexing and report generation.
- Add SAP incremental sync conflict detection.
- Add structured tests for key API routes.
- Split the current single-file portal into modules when safe.
- Add production monitoring and alert channels.
