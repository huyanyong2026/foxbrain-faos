# VAFOX PMO Three-Person Operating Model

Version: 2026-07-09
Project: VAFOX Enterprise OS
Repository: huyanyong2026/foxbrain-faos
Primary System: huyan.vafox.com

---

## 1. Team Model

VAFOX will be built by a compact AI-native team:

```text
Founder / CEO
   ↓
Chief AI Architect
   ↓
Codex Chief Engineer
```

There is no traditional programmer team. The system must therefore rely on clear architecture, strict Sprint documents, GitHub discipline, Codex execution, and repeated real-data validation.

---

## 2. Roles

### 2.1 Founder / CEO

Responsible for:

- Business direction
- Final product approval
- Real SAP data and business documents
- Operating judgment
- PR merge confirmation when needed

The CEO should not need to manage implementation details.

### 2.2 Chief AI Architect

Responsible for:

- Product architecture
- AI architecture
- Data architecture
- Sprint design
- Epic roadmap
- Business rules
- Data governance
- QA acceptance
- Codex prompts
- Review of Codex output

The architect must ensure VAFOX grows as a coherent Enterprise OS, not a set of scattered features.

### 2.3 Codex Chief Engineer

Responsible for:

- Code implementation
- Refactoring
- Tests
- Local validation
- PR creation
- Summary reports
- Following Sprint specs strictly

Codex must never rewrite the whole system unless explicitly instructed.

---

## 3. Working Loop

```text
Business Need
↓
Architecture Design
↓
GitHub Sprint Spec
↓
Codex Implementation
↓
PR
↓
CEO Merge Confirmation
↓
Architect Review
↓
Next Sprint
```

Every Sprint must have:

- GitHub design document
- Safety rules
- Database requirements
- API requirements
- UI requirements
- QA acceptance
- Summary report
- Test report

---

## 4. Asset Boundary

### GitHub owns system assets

GitHub stores:

- Code
- Product design
- Architecture
- Sprint plans
- Business rules
- Data models
- API specs
- QA reports
- Release notes

### VAFOX Drive owns enterprise assets

VAFOX Drive stores:

- SAP export files
- Contracts
- Store expense files
- Store photos
- Product materials
- Brand materials
- Training files
- Meeting notes
- Business reports

### Rule

```text
GitHub manages how VAFOX runs.
VAFOX Drive manages what Huohu Fox owns and knows.
```

---

## 5. Safety Rules

- Do not connect directly to production SAP.
- Do not install any experimental program on the SAP production server.
- Do not develop ai.vafox.com until huyan.vafox.com is stable.
- Do not store real private enterprise data in GitHub.
- Do not auto-create business objects without human confirmation.
- Preserve original files and raw data lineage.
- Every AI conclusion must be traceable to data, knowledge, memory, or business rule.

---

## 6. Development Philosophy

VAFOX is not a website.

VAFOX is an Enterprise Second Brain Operating System.

Every module must serve long-term enterprise memory, data understanding, and decision quality.

Do not build features for appearance only.

Build durable enterprise assets.

---

## 7. Current Epic Structure

### Epic001: Enterprise Data

Goal: trusted enterprise data foundation.

Includes:

- Drive
- Object Engine
- Knowledge Pipeline
- Search + Timeline
- CEO Dashboard
- Memory Engine
- SAP Import
- Data Lake
- Business Calibration

### Epic002: Business Knowledge Graph

Goal: connect brands, products, stores, employees, suppliers, contracts, sales, inventory, memory, and decisions into a business graph.

### Epic003: Decision Engine

Goal: help CEO understand why things happen and what to do next.

### Epic004: Enterprise Automation

Goal: scheduled SAP import, AI daily report, weekly business review, and proactive risk reminders.

### Epic005: Enterprise Agent Center

Goal: specialized agents for CEO, brand, inventory, store, supplier, content, and finance.

---

## 8. Definition of Done

A Sprint is done only when:

- Code compiles.
- Smoke tests pass.
- Existing features remain usable.
- Safety boundary is preserved.
- Real data validation is performed when applicable.
- Summary report is generated.
- Test report is generated.
- PR is reviewed and merged.

---

## 9. Immediate Focus

Current focus:

```text
Sprint008.5 Business Calibration
↓
Sprint009 Business Knowledge Graph
↓
Sprint010 Decision Engine
```

Do not rush to AI agents before business data, calibration, and graph are stable.

---

## 10. Long-Term Goal

VAFOX should become the system the CEO opens every day before SAP.

It should answer:

- What happened?
- Why did it happen?
- What is risky?
- What should we do next?
- Which data supports this conclusion?

The final product is:

```text
VAFOX Enterprise OS
The Enterprise Second Brain
```
