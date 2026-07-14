# Sprint017: Daily Intelligence Engine｜每日经营智能引擎

Status: Ready for Codex
Target: huyan.vafox.com
Priority: P0
Depends on: Sprint015.5 CEO Brain, Sprint016 Sync Engine, Sprint016.5 SAP Readonly Rollout

---

## 1. Sprint Goal

Build VAFOX Daily Intelligence Engine.

Goal:

Transform overnight enterprise processing into a CEO-ready daily briefing.

```text
SAP Sync
↓
Data Processing
↓
Rules
↓
Health
↓
Decision
↓
CEO Daily Intelligence
```

---

## 2. Core Experience

Every morning CEO should see:

- What happened yesterday?
- What changed?
- What risks appeared?
- What opportunities appeared?
- What should be done today?

---

## 3. Daily Intelligence Report

Create:

## daily_intelligence_reports

Fields:

```text
id
report_date
summary
health_summary
decision_summary
risk_summary
opportunity_summary
execution_summary
evidence_json
status
created_at
```

## daily_intelligence_items

Fields:

```text
id
report_id
item_type
severity
title
description
entity_type
entity_id
evidence_json
recommended_action
created_at
```

---

## 4. Generation Pipeline

Daily generation flow:

```text
Sync Freshness Check
↓
Business Health Calculation
↓
Decision Rebuild
↓
Inventory Analysis
↓
Brand Analysis
↓
Store Analysis
↓
Daily Report Generation
```

---

## 5. CEO Brain Integration

CEO homepage should display:

- Today's Intelligence
- Top 3 risks
- Top 3 opportunities
- Recommended actions
- Data freshness

Every item must link to evidence.

---

## 6. Scheduling

Create scheduler foundation only.

Default:

```text
DISABLED
```

Support later:

```text
22:00 Sync
23:00 Analysis
07:30 Report Ready
```

Must require manual approval before activation.

---

## 7. API Requirements

Add:

```text
GET /api/daily-intelligence/latest
GET /api/daily-intelligence/history
POST /api/daily-intelligence/rebuild
GET /api/daily-intelligence/items/:id
```

---

## 8. UI Requirements

Add:

```text
/daily-intelligence
```

Display:

- Daily summary
- Risks
- Opportunities
- Recommended actions
- Evidence
- Historical reports

---

## 9. Memory Integration

Important daily events can become enterprise memories.

Examples:

- Major decision
- Important risk
- Business turning point

---

## 10. QA Acceptance

Sprint017 passes when:

- Daily report can be generated.
- Report contains evidence.
- CEO homepage displays latest intelligence.
- History can be viewed.
- Scheduler remains disabled by default.
- Existing Sprint001-016.5 functions remain working.
- No production SAP write access.

---

## 11. Codex Instruction

Incremental upgrade only.

Do not rewrite architecture.

Do not develop ai.vafox.com.

Do not enable automatic production schedules without approval.

Deliver:

```text
SPRINT017_DAILY_INTELLIGENCE_SUMMARY.md
SPRINT017_DAILY_INTELLIGENCE_TEST_REPORT.md
```
