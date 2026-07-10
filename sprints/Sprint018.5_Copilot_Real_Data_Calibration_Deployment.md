# Sprint018.5: Copilot Real Data Calibration & Deployment｜Copilot真实数据校准与线上部署

Status: Ready for Codex
Target: huyan.vafox.com
Priority: P0
Depends on: Sprint018 Enterprise Copilot Foundation

---

## 1. Sprint Goal

Move Enterprise Copilot from local functional validation into real-business calibrated production use.

The goal is not to add more chat features. The goal is to verify that Copilot answers real Huohu Fox questions using trusted enterprise evidence.

```text
Real business question
↓
Intent understanding
↓
Trusted enterprise context
↓
Evidence collection
↓
Grounded answer
↓
User feedback
↓
Memory draft when approved
```

---

## 2. Safety Boundary

Must follow:

- Do not connect to SAP with write permission.
- Do not modify production SAP.
- Do not install programs on the SAP production server.
- Do not develop ai.vafox.com.
- Do not expose database credentials or secrets.
- Do not create permanent enterprise memory from test conversations automatically.
- Do not fabricate an answer when evidence is insufficient.

---

## 3. Production Deployment

Deploy latest `main` to `huyan.vafox.com`.

Verify:

```text
/
/copilot
/api/copilot/*
/api/dashboard/ceo
```

Production deployment report must include:

- repository commit
- deployed commit
- runtime directory
- service status
- route status

---

## 4. Real Data Calibration Questions

Run the following real-business questions against the production business database.

### 4.1 Enterprise Overview

```text
今天企业有什么主要风险？
```

Expected context:

- Daily Intelligence
- Business Health
- Decision Insights
- Business Rules
- Sync freshness

### 4.2 Osprey Inventory

```text
Osprey库存怎么样？有哪些风险？
```

Expected context:

- Inventory Intelligence
- Brand Intelligence
- SAP inventory
- SAP sales
- Business Rules
- Decision evidence

### 4.3 Kailas Performance

```text
Kailas销售和库存表现怎么样？
```

Expected context:

- Brand Intelligence
- sales contribution
- gross profit / margin when available
- inventory amount / quantity
- store distribution

### 4.4 Nanshan Store

```text
南山店经营情况怎么样？
```

Expected context:

- Store Intelligence
- sales
- margin
- inventory
- brand mix
- Decision Insights

### 4.5 Data Sufficiency

Run at least one question where evidence is incomplete.

Expected response:

```text
当前数据不足，无法形成可靠结论。
```

The answer must list what data is missing.

---

## 5. Evidence Requirements

Every answer must show:

- source type
- source record or entity
- metric or fact
- timestamp / freshness when available
- confidence

Evidence types may include:

```text
business_health
decision_insight
inventory_intelligence
brand_intelligence
store_intelligence
business_rule
daily_intelligence
enterprise_memory
knowledge_item
data_lake_record
sync_freshness
```

No answer should be presented as reliable when no evidence exists.

---

## 6. Answer Quality Rules

Each answer should use this structure:

```text
结论
原因
关键数据
风险 / 机会
建议
证据
数据更新时间
```

Rules:

- Separate fact from inference.
- Mark uncertainty clearly.
- Do not claim causal relationships without evidence.
- Do not recommend actions that conflict with approved Business Rules.
- Show stale-data warning when source freshness exceeds configured threshold.

---

## 7. Feedback Calibration

Test:

- helpful feedback
- not helpful feedback
- correction note
- missing evidence report

Store feedback for later quality improvement.

Do not let feedback directly modify business rules or enterprise memory.

---

## 8. Memory Draft Validation

For one validated Copilot answer:

- create an enterprise memory draft
- confirm status remains draft
- confirm evidence and source answer are linked
- delete or archive the test draft after validation

No test memory may remain active in the production knowledge system.

---

## 9. Test Data Cleanup

After validation, clean:

- test conversations
- test messages
- test feedback
- test memory drafts

Do not delete real user conversations or real enterprise memory.

Cleanup must be selective and auditable.

---

## 10. UI Calibration

Improve `/copilot` only where necessary for real use:

- evidence drawer
- data freshness indicator
- insufficient-data state
- answer confidence label
- feedback controls
- create-memory-draft confirmation

Do not redesign the whole product.

---

## 11. QA Acceptance

Sprint018.5 passes when:

- latest main is deployed to production.
- `/copilot` works with the real business database.
- all four calibration questions return grounded answers.
- every reliable conclusion contains evidence.
- insufficient evidence produces a clear data-insufficient answer.
- stale data is visibly warned.
- feedback is stored correctly.
- memory draft creation works and remains draft.
- test data is cleaned without affecting real data.
- no SAP write access is used.
- existing Sprint001-018 functions remain working.

---

## 12. Deliverables

Generate:

```text
SPRINT018_5_COPILOT_REAL_DATA_CALIBRATION_SUMMARY.md
SPRINT018_5_COPILOT_REAL_DATA_TEST_REPORT.md
SPRINT018_5_PRODUCTION_DEPLOYMENT_REPORT.md
SPRINT018_5_EVIDENCE_AUDIT_REPORT.md
SPRINT018_5_TEST_DATA_CLEANUP_REPORT.md
```

The evidence audit report must include the exact evidence categories used for each calibration question, but must not include secrets or sensitive raw credentials.

---

## 13. Codex Instruction

Incremental upgrade only.

Deploy only after local checks pass.

Do not enable SAP write access.

Do not invent missing business facts.

Do not leave test memory or test conversations active in production.
