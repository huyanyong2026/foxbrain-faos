# Sprint019.1: VAFOX Usability & Intelligence Polish｜易用性与智能体验完善

Status: Ready for Codex
Target: huyan.vafox.com
Priority: P0
Depends on: Sprint018.5 and Sprint019 CEO Experience 2.0

## 1. Goal

Make huyan.vafox.com feel like a coherent CEO workbench rather than a collection of engineering modules.

The user should be able to:

- understand the company in 30 seconds;
- reach any important task within two clicks;
- ask the enterprise directly from every key page;
- see why a conclusion exists;
- know what to do next;
- use the system smoothly on desktop and mobile.

## 2. Current Problems to Fix

Treat these as product defects:

- too many first-level entrances and engine names;
- pages feel disconnected;
- homepage shows modules rather than priorities;
- information density is inconsistent;
- loading and rebuild actions feel abrupt;
- Copilot is separated from the business pages;
- empty states look unfinished;
- evidence is technically present but hard to understand;
- users do not know whether data is current;
- recommendations do not always lead to a next action;
- mobile navigation is difficult;
- some pages expose development terminology to the CEO.

## 3. Product Information Architecture

Reduce the visible primary navigation to:

1. 首页
2. 经营
3. 企业档案
4. AI 助手
5. 行动中心

Put technical and administration pages under a secondary “系统管理” menu.

Do not remove existing routes. Reorganize the visible navigation only.

### 3.1 首页

Homepage must show only:

- greeting and data freshness;
- current period sales, gross profit, expenses, profit;
- business health;
- top three risks;
- top three opportunities;
- today’s recommended actions;
- Daily Intelligence summary;
- a prominent Copilot input.

The homepage must not expose raw Engine names in the main visual area.

### 3.2 经营

Use five business tabs:

- 总览
- 门店
- 品牌
- 库存
- 利润质量

Each tab should show conclusions first, details second, evidence third.

### 3.3 企业档案

Group:

- 门店
- 品牌
- 产品
- 供应商
- 员工
- 顾客
- 文件与知识
- 企业记忆

### 3.4 AI 助手

AI assistant page should include:

- current conversation;
- suggested questions;
- recent questions;
- cited evidence drawer;
- “create action”, “create memory draft”, and “open related page” actions.

### 3.5 行动中心

Unify:

- high-risk decisions;
- pending approvals;
- failed rebuilds;
- stale data warnings;
- unresolved quality issues;
- user-created follow-ups.

## 4. Universal Copilot

Add a persistent Copilot launcher on every authenticated page.

Requirements:

- desktop: fixed right-side launcher;
- mobile: bottom action bar;
- page-aware context;
- show current page and entity context;
- allow questions such as “解释这个品牌为什么风险高”; 
- preserve conversation when moving between pages;
- do not automatically include unauthorized or unrelated records.

## 5. Answer Design

Every Copilot answer should use the same structure:

1. 结论
2. 为什么
3. 关键数字
4. 风险与不确定性
5. 建议行动
6. 数据来源与更新时间

If evidence is insufficient, explicitly show:

- what data is missing;
- which analysis needs rebuild;
- a safe next step.

Never fabricate a conclusion.

## 6. Data Freshness Experience

Create one shared data-freshness component used everywhere.

Show:

- last SAP copy time;
- last Data Lake publish time;
- last intelligence rebuild time;
- status: current / stale / incomplete / failed;
- action button when rebuild is safe.

Avoid showing timestamps without interpretation.

## 7. Loading and Performance

Improve perceived and actual responsiveness:

- measure server response time for top routes;
- add skeleton loading rather than blank pages;
- cache read-only dashboard summaries safely;
- avoid repeated full-table queries on homepage;
- paginate large tables;
- lazy-load evidence and history drawers;
- show progress for rebuild actions;
- prevent duplicate submits;
- keep the old result visible while a new analysis is running;
- display friendly error messages with retry actions.

Target:

- homepage first meaningful render under 2 seconds in normal production conditions;
- Copilot request immediately shows progress state;
- navigation feedback under 200 ms.

## 8. Intelligent Empty States

Every empty page must explain:

- what this page is for;
- why there is no data;
- what input or rebuild is needed;
- the exact next action.

Do not show empty tables as the only state.

## 9. Evidence UX

Replace technical evidence dumps with readable evidence cards.

Each card should show:

- source type;
- source name;
- date range;
- key value;
- freshness;
- link to the related business page;
- optional raw-data expansion.

Evidence should be collapsed by default and readable by non-technical users.

## 10. Profit Quality Presentation

For 2026 current metrics:

- SAP profit already includes the Osprey rebate 964,798.03 and Kailas rebate 79,919.75;
- do not add these amounts again;
- display them as profit composition only;
- mark rebate income as policy-dependent and non-guaranteed;
- explain sustainability risk without changing SAP profit.

Display:

- SAP profit;
- rebate portion included in SAP profit;
- profit excluding identified rebates;
- rebate dependency ratio;
- clear warning that historical rebates do not guarantee future rebates.

## 11. Actionable Recommendations

Every major risk or opportunity card should support:

- view evidence;
- ask Copilot;
- create action item;
- assign owner later;
- mark reviewed;
- archive after resolution.

Recommendations without a next action should not appear as final cards.

## 12. Visual System

Create a consistent design system:

- one page header pattern;
- one card system;
- one status badge system;
- one spacing scale;
- one typography scale;
- consistent Chinese business terminology;
- no exposed internal technical labels in CEO-facing pages;
- clear contrast and large click targets;
- accessible keyboard focus states.

Use restrained enterprise styling. Avoid decorative dashboards and excessive gradients.

## 13. Mobile Experience

Mobile acceptance routes:

- /
- /copilot
- /daily-intelligence
- /decision
- /business-health
- /inventory-intelligence
- /brand-intelligence
- /store-intelligence
- /action-center

Requirements:

- no horizontal page overflow;
- tables transform into cards or compact lists;
- bottom navigation for five primary sections;
- prominent back and home actions;
- Copilot input usable with mobile keyboard;
- evidence drawer readable on a phone.

## 14. Analytics and Feedback

Add lightweight internal UX telemetry without third-party tracking:

- route load time;
- failed page loads;
- Copilot response duration;
- most-used primary entrances;
- abandoned rebuilds;
- explicit helpful / not helpful feedback.

Do not store sensitive question contents in analytics events beyond existing approved conversation storage.

## 15. Safety

- no SAP write access;
- no SAP production modification;
- no ai.vafox.com development;
- no secret committed to GitHub;
- preserve all existing routes and data;
- back up production code and database before deployment;
- do not delete real conversations, memories, decisions, or evidence.

## 16. QA Acceptance

Required acceptance:

- all existing smoke tests pass;
- homepage shows current 2026 metrics consistently;
- rebate is not double-counted;
- primary navigation has five items;
- all key pages expose Universal Copilot;
- evidence cards are readable and linked;
- empty states provide next actions;
- rebuild progress is visible;
- duplicate rebuild requests are prevented;
- top pages work on desktop and mobile;
- production service remains active after deployment;
- test data is cleaned without touching real data.

## 17. Deliverables

Generate:

- SPRINT019_1_USABILITY_INTELLIGENCE_POLISH_SUMMARY.md
- SPRINT019_1_USABILITY_INTELLIGENCE_POLISH_TEST_REPORT.md
- SPRINT019_1_PRODUCTION_DEPLOYMENT_REPORT.md
- SPRINT019_1_ROUTE_PERFORMANCE_REPORT.md
- SPRINT019_1_MOBILE_ACCEPTANCE_REPORT.md
- SPRINT019_1_PROFIT_QUALITY_VALIDATION_REPORT.md

## 18. Deployment Order

1. Inspect current production UX and route performance.
2. Produce a short before-state report.
3. Implement locally on a new branch.
4. Run regression and mobile checks.
5. Back up production code and database.
6. Deploy to huyan.vafox.com.
7. Validate authenticated routes.
8. Confirm current metrics and rebate treatment.
9. Clean test data.
10. Push branch and open PR to main.
