# Sprint019: CEO Experience 2.0｜友好智能体验重构

Status: Ready for Codex
Target: huyan.vafox.com
Priority: P0
Depends on: Sprint018.5

## Goal

把现有“功能很多但不好用”的系统，升级为老板每天愿意打开的 CEO 工作台。本 Sprint 不新增大型引擎，重点整合现有能力、简化导航、统一视觉、加强 Copilot 与行动引导。

## Product Principles

- 老板优先，不以技术模块为中心。
- 先结论，后详情；先今天，后历史；先行动，后菜单。
- 所有建议保留 evidence。
- 无数据时解释缺什么、为什么缺、下一步怎么做。
- 不删除现有能力，只把技术页面放到二级导航。

## Homepage `/`

第一屏必须在 30 秒内回答：企业怎么样、最重要风险、机会、今天先做什么。

首页结构：

1. 问候与数据更新时间。
2. 核心指标：企业健康、销售、毛利、费用、利润、库存风险、数据新鲜度。
3. 今天最重要的三件事。
4. AI 问企业输入框。
5. 今日行动：待处理、待审批、待重建、数据异常。
6. 最近日报与最近决策。

首页不要放几十张卡片，不显示技术 ID，不展示原始 JSON。

## Profit Composition

2026 SAP 利润已经包含品牌返点，禁止再次相加。

页面需要展示利润构成：

- SAP利润：1,723,487.13
- 其中 Osprey 返点：964,798.03
- 其中 Kailas 返点：79,919.75
- 返点合计：1,044,717.78
- 非返点利润：678,769.35
- 返点占利润约 60.6%

必须提示：品牌返点不是长期固定收益，利润质量存在依赖风险。

## Navigation

一级导航只保留：

- 首页
- 经营
- 企业资料
- AI助手
- 系统

经营：Daily Intelligence、Business Health、Decision、Inventory、Brand、Store、Profit Quality。

企业资料：Drive、Data Lake、Objects、Knowledge、Memory、Timeline。

AI助手：Copilot、CEO Workbench、推荐问题、最近会话。

系统：Sync Center、Calibration、Rules、Graph、诊断。

## Copilot `/copilot`

增加推荐问题：

- 今天企业最重要的风险是什么？
- 今年利润为什么看起来不错？
- 品牌返点对利润影响多大？
- Osprey库存风险在哪里？
- Kailas销售和库存表现如何？
- 南山店最近经营怎么样？

回答结构统一为：结论、关键原因、数据依据、风险与不确定性、建议行动、查看证据。

证据不足时显示：

“当前数据不足，无法形成可靠结论。”

并列出缺失证据和安全的下一步，例如“重新分析品牌智能”。

## Action Center

首页和 CEO Workbench 增加统一行动中心：

- 今日必须处理
- 待审批
- 待重建
- 数据异常
- 已完成

每条显示优先级、来源、原因、evidence 数量、建议动作和状态。

## Smart Empty States

禁止空白表格。每个空状态必须说明：这个页面做什么、为什么无数据、缺少什么、下一步如何处理。

## Design System

统一页面标题、卡片、间距、字体层级、状态标签、按钮和空状态。中文为主，英文仅作次级说明。风格简洁、克制、专业，不做密集开发者仪表盘。

## Mobile

首页、Copilot、日报、决策、行动中心必须适配手机：无横向滚动、按钮易点击、核心指标无需缩放、Copilot 输入框始终易用。

## Performance

首页优先加载核心摘要，重列表延迟加载；增加骨架屏；单个引擎变慢时不阻塞整个页面；部分数据可用时先显示部分结果。

## Friendly Language

把技术文案改成业务语言：

- No insight found → 暂无需要处理的经营提醒
- Rebuild engine → 重新分析
- Insufficient evidence → 当前证据不足，暂不能下结论
- Data freshness → 数据更新时间

## Safety

- 不增加 SAP 写权限。
- 不修改生产 SAP。
- 不开发 ai.vafox.com。
- 不提交密钥。
- 部署前备份代码和数据库。
- 不删除真实会话和真实企业记忆。
- 所有重建操作可审计。

## Acceptance

1. 首页 30 秒看懂企业状态。
2. 可看到三项最重要风险或机会。
3. 无需寻找菜单即可提问。
4. 利润与返点构成不重复计算。
5. 数据陈旧时明显提醒。
6. 数据不足时解释原因和下一步。
7. 手机可正常使用核心流程。
8. 高级模块仍可访问，但不压迫首页。

## Deliverables

- SPRINT019_CEO_EXPERIENCE_2_0_SUMMARY.md
- SPRINT019_CEO_EXPERIENCE_2_0_TEST_REPORT.md
- SPRINT019_PRODUCTION_DEPLOYMENT_REPORT.md
- SPRINT019_MOBILE_UX_TEST_REPORT.md
- SPRINT019_PROFIT_COMPOSITION_VALIDATION_REPORT.md

## Codex

从最新 main 创建 `sprint019-ceo-experience-2-0`，增量升级并保留 Sprint001-018.5 全部能力。先本地测试，再部署 huyan.vafox.com。部署后验证首页、CEO Workbench、Copilot、Daily Intelligence、Decision、Business Health、Inventory、Brand、Store、Sync Center。