# DATA-003.3：Employee AI Assistant 设计

**状态：** Design Phase / 仅设计，不部署  
**入口：** `ai.vafox.com`（员工已认证工作台）  
**上游设计：** `DATA003.1_CUSTOMER_IDENTITY_DESIGN.md`、`DATA003.2_RECOMMENDATION_ENGINE_DESIGN.md`  
**负责人：** Codex（开发设计）；WorkBuddy（环境）；Marvis（管理）；CTO（验收）

---

## 1. 目标、范围与不可突破边界

员工 AI 助手为门店员工提供受权限、可解释、由人确认的客户经营和销售辅助。它聚合 Customer Identity Foundation 的受控客户上下文、Recommendation Engine 的建议，以及 Core 的只读产品、库存和销售事实，帮助员工识别机会、准备方案和记录跟进。

本设计不是 CRM、订单、营销自动化或 SAP/Core 同步的替代品。SAP 仍是业务事实源，Core 仍是企业事实中心；助手只读取受治理数据并创建员工填写、可审计的跟进记录。

### 1.1 明确禁止

无论角色、模型输出或置信度如何，助手均**禁止**：

- 自动发送营销消息，或代表员工/客户向任何外部渠道发送消息；
- 自动成交、自动接受报价、自动生成或自动提交订单；
- 自动下单、预留库存、调拨库存、修改价格或向客户承诺库存；
- 修改 SAP；
- 修改 Core 生产同步；
- 将模型推断当作客户事实、成交事实或员工考核事实。

所有客户沟通、推荐展示、报价、成交和任何外部业务动作均由获授权员工在已批准系统和流程中独立完成。AI 助手不会调用这些操作接口。

---

## 2. Employee Assistant Architecture

```text
员工身份（认证、组织/门店/角色、用途）
                    ↓
客户查询（仅 customer_id 或受限的已授权检索）
                    ↓
客户画像（Customer Identity Foundation 的最小化授权投影）
                    ↓
AI 推荐（Recommendation Engine；附库存、证据、鲜度和限制）
                    ↓
销售建议（话术、方案和人工核实清单）
                    ↓
跟进记录（员工输入、审计、不可直接驱动外部动作）
```

### 2.1 组件职责

| 组件 | 输入 | 输出 | 约束 |
| --- | --- | --- | --- |
| Employee Access Gateway | 已认证会话、声明用途、委托主体、关联 ID | 已验证的员工上下文与短期访问令牌 | 每请求执行组织隔离、RBAC + ABAC、字段脱敏和审计；默认拒绝。 |
| Customer Query Service | `customer_id`、员工范围 | 授权客户的最小化查询结果 | 不使用原始手机号/微信号作为普通读取参数；不泄露未授权客户是否存在。 |
| Customer Context Composer | 客户主数据、画像、装备、关系、授权 | 面向员工的客户摘要 | 仅组合 DATA-003.1 已允许的服务/个性化字段，并保留来源、鲜度和缺失原因。 |
| Opportunity Service | 授权客户集合、门店、时间窗口 | 今日机会列表和优先级理由 | 只生成建议快照；不创建营销任务或自动触达。 |
| Recommendation Adapter | 客户需求、门店、预算、场景 | 产品方案、库存匹配、解释、限制 | 调用 DATA-003.2 只读推荐；库存不是预留或承诺。 |
| Sales Guidance Generator | 已批准知识、推荐事实、员工问题 | 可编辑销售话术和核实步骤 | 不编造产品、价格、库存或客户偏好；答案须标出数据源和更新时间。 |
| Follow-up Service | 员工显式提交的跟进内容 | 跟进记录、后续人工待办 | 仅写入本助手的受治理记录；不向 SAP/Core 生产同步或外部消息渠道写入。 |
| Audit & Policy Service | 每个读取/写入决策 | 不可变审计事件 | 日志不得包含原始身份标识、完整客户画像或自由文本全文。 |

### 2.2 请求信任链与数据流

1. `ai.vafox.com` 完成员工认证，网关从员工目录取得 `employee_id`、组织、门店、角色和有效权限，生成短时会话上下文。
2. 调用方必须传递 `Authorization`、`X-Correlation-Id`、`X-Purpose` 与 `X-Organization-Id`；服务端从令牌而非前端声称的角色决定范围。
3. Policy Service 先按组织、门店、客户关系和用途过滤，再从 Customer Foundation 读取最小字段；无关系、无同意或用途不匹配时返回安全的 `403 POLICY_DENIED`。
4. Opportunity/Recommendation 服务在已允许的客户上下文中生成只读建议；每张卡片带数据来源、事实时间、模型/规则版本、置信度、限制和 `advisory_only_requires_human_approval`。
5. 员工查看、编辑、拒绝或采纳建议后，才能手工提交跟进记录。该记录不触发外部消息、订单或任何生产同步。

---

## 3. Employee Context Model

员工上下文是每次请求重新计算的授权快照，不由浏览器持久化，也不以过期缓存替代权限决策。

| 字段 | 类型 | 来源/含义 | 安全规则 |
| --- | --- | --- | --- |
| `employee_id` | string | 员工目录的不可变引用。 | 由认证主体绑定，不接受客户端覆盖。 |
| `store_id` | string[] | 当前授权门店范围；可含当前工作门店。 | 必须属于同一 `organization_id`；请求目标门店须在范围内。 |
| `role` | enum/string[] | 如 `sales_associate`、`store_manager`、`executive`。 | 只由受治理目录/角色服务签发。 |
| `permissions` | string[] | 细粒度能力，如 `opportunities:read`、`customer:read`、`followup:write`。 | 权限不足即拒绝，角色名称不直接绕过字段策略。 |
| `assigned_customers` | reference[] | 有效的顾问/服务关系与客户引用。 | 员工逐客户读取必须命中有效授权关系或被显式授予。 |
| `sales_history` | aggregate/reference[] | 员工在授权范围内的销售聚合或受控事实引用。 | 用于辅助排序和经营分析；不得自动归因佣金或暴露无关客户明细。 |

推荐的运行时对象如下；其中 `authorized_customer_scope` 是策略求值结果，不是前端可枚举的客户主数据副本：

```json
{
  "employee_id": "emp_01J...",
  "organization_id": "org_vafox_cn",
  "store_id": ["store_nanshan"],
  "role": ["sales_associate"],
  "permissions": ["opportunities:read", "customer:read", "recommendation:generate", "followup:write"],
  "assigned_customers": [{"customer_id": "cst_01J...", "relationship_role": "primary_advisor", "valid_to": null}],
  "sales_history": [{"period": "2026-07", "metric_ref": "salesagg_..."}],
  "authorized_customer_scope": {"policy_snapshot": "pol_...", "evaluated_at": "2026-07-21T00:00:00Z"}
}
```

上下文失效、员工离职/调店、角色变更、客户交接或客户同意撤回后，后续请求必须重新求值；缓存键至少包含 `organization_id`、`employee_id`、`store_id`、声明用途和策略版本。

---

## 4. Customer Opportunity Dashboard

### 4.1 今日客户机会

仪表盘仅显示当前员工可访问的授权客户。默认按“今日”窗口展示，支持服务端固定时点 `as_of` 和游标分页；不允许前端通过筛选参数扩大客户范围。

| 展示字段 | 内容 | 来源与控制 |
| --- | --- | --- |
| 客户姓名 | 经策略允许的显示名；否则如 `张*`。 | Customer Master；按字段策略脱敏。 |
| 最近购买 | 商品/类目摘要和时间，不展示不必要订单明细。 | Core 受治理销售事实；无授权时省略。 |
| 最近互动 | 最近一次互动时间、渠道、结果码摘要。 | 受限互动引用；不返回完整聊天内容。 |
| 潜在需求 | 声明需求或带置信度的机会假设。 | 明确标记“客户声明”或“AI 推断”；无个性化同意时仅可使用非个性化场景。 |
| 推荐动作 | 如“邀约到店时确认徒步场景与尺码”“展示搭配方案”。 | 建议，不是消息、任务执行或销售指令。 |
| 优先级 | `high`、`medium`、`low` 及可解释理由。 | 基于授权事实的版本化排序；不得以敏感属性或未授权画像排序。 |

**示例卡片（设计示例，不表示真实客户或库存）：**

```text
优先级：高（近期到店互动 + 已授权装备升级机会；需人工核实）
客户：张先生
历史：KAILAS 冲锋衣（购买摘要）
AI 建议：秋季徒步裤 + 背包升级方案
推荐动作：先确认秋季徒步频率、容量需求和尺码；再核实本店库存
数据限制：库存快照 15 分钟前；建议仅供人工确认
```

### 4.2 优先级设计

机会优先级是可解释的队列排序，不是自动营销评分。输入仅包括：有效客户-员工关系、经授权且在鲜度阈值内的购买/互动摘要、客户主动表达需求、推荐覆盖度、库存可售状态和员工已记录的后续动作。排序结果必须返回 `reason_codes`、`model_or_rule_version`、`as_of`、`confidence` 与 `limitations`。

以下情形必须抑制个人机会或降级为通用服务建议：客户未授权个性化、身份冲突、关系失效、事实数据过期、库存不可用、画像质量不足或策略无法判断。系统不得使用姓名、手机号、年龄、性别等直接身份属性来抬高优先级。

---

## 5. Customer Assistant API

**基础路径：** `/api/employee`  
**共同请求头：** `Authorization`、`X-Correlation-Id`、`X-Purpose: customer_service|clienteling|analytics`、`X-Organization-Id`、`Accept: application/json`。  
**共同响应：** JSON、UTC RFC 3339、`correlation_id`、`policy`、`freshness`、`lineage`、`disposition`。所有端点由服务端推导员工身份；不得相信请求体中的 `employee_id` 或 `role`。

### 5.1 `GET /api/employee/opportunities`

读取当前员工在指定授权门店的今日客户机会。需要 `opportunities:read`；员工只能获取其 `assigned_customers` 范围，门店经理可获取本门店授权客户，管理层默认只能获取聚合结果。

**查询参数：** `store_id`（必填且须授权）、`date`（可选，默认当前门店业务日）、`priority`（可选）、`cursor`、`limit`（1–50，默认 20）、`as_of`（可选）。

```json
{
  "opportunities": [{
    "opportunity_id": "opp_01J...",
    "customer": {"customer_id": "cst_01J...", "display_name": "张*"},
    "recent_purchase": {"summary": "KAILAS 冲锋衣", "purchased_at": "2026-05-12T00:00:00Z"},
    "recent_interaction": {"occurred_at": "2026-07-20T09:30:00Z", "channel": "store", "outcome_code": "asked_hiking_gear"},
    "potential_need": {"kind": "inferred", "summary": "秋季徒步装备升级", "confidence": 0.72},
    "recommended_action": "确认徒步频率、容量需求和尺码后展示方案；先核实库存。",
    "priority": {"level": "high", "reason_codes": ["recent_interaction", "authorized_upgrade_opportunity"]},
    "limitations": ["inventory_requires_human_verification"],
    "disposition": "advisory_only_requires_human_approval"
  }],
  "page": {"next_cursor": null},
  "policy": {"decision": "allow", "customer_scope": "assigned_only"},
  "freshness": {"as_of": "2026-07-21T09:00:00Z"},
  "correlation_id": "corr_..."
}
```

### 5.2 `GET /api/employee/customer/{id}`

读取一个已授权客户的员工辅助包。需要 `customer:read`，以及所请求的画像/推荐字段权限；`{id}` 必须为 `customer_id`。服务按员工-客户关系、门店、用途、同意和字段策略过滤后，返回客户画像、推荐方案、销售话术和历史记录。未授权、客户不存在或禁止披露存在性时统一返回 `403 POLICY_DENIED`。

**查询参数：** `store_id`（必填）、`activity`、`budget_min`、`budget_max`、`include_history`（默认 `true`）、`as_of`。可选需求参数仅作为本次建议的显式上下文，不能静默写回客户画像。

```json
{
  "customer": {"customer_id": "cst_01J...", "display_name": "张*", "relationship_role": "primary_advisor"},
  "customer_profile": {"outdoor_level": "regular", "interest_tags": ["hiking"], "data_classification": "authorized_summary"},
  "recommendation_plan": {
    "recommendation_id": "rec_01J...",
    "products": [{"product_id": "prd_...", "name": "徒步裤", "reason": "与已确认徒步场景匹配"}],
    "inventory_match": [{"store_id": "store_nanshan", "availability": "sellable", "as_of": "2026-07-21T08:55:00Z"}],
    "confidence": {"score": 0.81, "level": "high"}
  },
  "sales_talking_points": [{"text": "可先确认您秋季徒步的频率和单日负重，再比较裤型与背负容量。", "evidence_refs": ["kb_..."], "requires_human_verification": true}],
  "history": {"purchases": [{"summary": "KAILAS 冲锋衣", "occurred_at": "2026-05-12T00:00:00Z"}], "followups": [{"followup_id": "fup_...", "occurred_at": "2026-07-10T10:00:00Z", "status": "open"}]},
  "policy": {"decision": "allow", "masked_fields": ["mobile"]},
  "freshness": {"profile_as_of": "2026-07-20T00:00:00Z", "inventory_as_of": "2026-07-21T08:55:00Z"},
  "lineage": [{"type": "customer_profile", "ref": "feat_..."}, {"type": "recommendation", "ref": "rec_01J..."}],
  "disposition": "advisory_only_requires_human_approval",
  "correlation_id": "corr_..."
}
```

### 5.3 `POST /api/employee/followup`

由员工显式保存一条跟进记录。需要 `followup:write`，且目标客户必须在提交时仍属于有效授权范围。此端点创建的是助手内部的跟进事实；不会发送消息、不会创建订单、不会修改 SAP、不会修改 Core 生产同步。

```json
{
  "customer_id": "cst_01J...",
  "store_id": "store_nanshan",
  "occurred_at": "2026-07-21T10:30:00Z",
  "customer_feedback": {"summary": "偏好 20–30L 背包，需周末再到店试背。", "sentiment": "interested"},
  "next_action": {"type": "employee_review", "due_at": "2026-07-25T10:00:00Z", "summary": "人工核实库存后准备试背方案。"},
  "deal_status": "open",
  "recommendation_refs": ["rec_01J..."]
}
```

成功返回 `201 Created`，包含 `followup_id`、员工/客户/门店引用、记录版本、审计引用和 `disposition: human_follow_up_only`。请求须使用 `Idempotency-Key` 防止重复提交。自由文本必须执行敏感数据最小化和保留策略；禁止写入原始手机号、支付信息、身份证明或不必要健康/敏感个人信息。

### 5.4 错误语义与审计

标准错误为 `400 INVALID_REQUEST`、`401 UNAUTHENTICATED`、`403 POLICY_DENIED`、`404 NOT_FOUND`（仅可安全披露时）、`409 CONTEXT_STALE`、`422 CONSENT_REQUIRED`、`429 RATE_LIMITED`、`503 DEPENDENCY_UNAVAILABLE`。审计至少记录主体/委托主体、组织与门店、声明用途、资源类别、策略结果、脱敏状态、关联 ID、数据/模型版本和时间；不得记录完整响应、原始身份标识或完整客户自由文本。

---

## 6. AI 销售辅助流程

```text
客户需求输入（员工录入或客户当面明确表达）
                    ↓
需求合法性、员工权限、客户授权与数据鲜度校验
                    ↓
Recommendation Engine（只读、可解释的产品/组合建议）
                    ↓
产品方案（适配理由、预算/场景限制、替代方案）
                    ↓
库存匹配（受授权门店的可售状态与快照时间）
                    ↓
销售话术（基于批准知识、可编辑、要求人工核实）
                    ↓
员工确认 / 编辑 / 拒绝 / 补问 → 仅后续人工沟通与跟进记录
```

1. **客户需求输入：** 员工输入本次可验证的场景、季节、预算、尺码/容量等需求。输入仅用于本次请求，除非员工单独按受治理流程记录为客户声明。
2. **Recommendation Engine：** 调用 DATA-003.2，传递最小化客户 ID、门店和需求；缺少个人化授权时返回通用、门店适用的方案，而不使用客户历史推断。
3. **产品方案：** 输出推荐商品、搭配/替代、理由、来源引用、置信度和限制。模型不能把未确认的“潜在需求”写成事实，也不能生成价格承诺。
4. **库存匹配：** 仅显示库存快照的状态和时间。库存过期、不可用或质量不合格时显示“请员工核实”，不得声称有货、锁货、跨店调货或保留商品。
5. **销售话术：** 以批准知识为证据，生成可编辑的问法、比较点和风险提示。每个业务答案至少呈现产品/门店/库存或答案值、数据来源和更新时间；知识不足时承认未知并提示人工查询。
6. **人工确认：** 员工可接受、编辑、拒绝或要求补充信息，并记录原因码。只有员工在独立授权流程中执行后续沟通或销售动作；助手没有自动执行权限。

---

## 7. Follow-up Management

### 7.1 跟进记录模型

| 字段 | 类型 | 规则 |
| --- | --- | --- |
| `followup_id` | UUID/string | 追加式记录标识；不复用。 |
| `customer_id` | string | 必须在提交时通过员工授权范围校验。 |
| `employee_id` / `store_id` | string | 从认证上下文绑定，保留当时快照。 |
| `communicated_at` | timestamp | 沟通时间，UTC RFC 3339；可与记录创建时间不同。 |
| `customer_feedback` | object | 客户反馈摘要和可选标准化结果码；最小化保存。 |
| `next_action` | object | 下一步人工动作、到期时间、负责人或状态；不是自动发送/自动执行指令。 |
| `deal_status` | enum | `open`、`interested`、`won_reference_pending`、`lost`、`no_response`、`closed`。成交仅可关联权威订单事实引用确认。 |
| `recommendation_refs` | string[] | 本次讨论的推荐快照引用，便于回放。 |
| `created_at` / `updated_at` | timestamp | 审计与版本控制。 |
| `audit_ref` | string | 不可变审计事件引用。 |

### 7.2 管理与质量控制

- 记录由员工明确提交；AI 可建议结构化字段但不得自行创建、关闭或改变成交状态。
- 修改采用版本化追加或保留前值的修订事件，记录修改人、时间和原因；不得静默覆盖原始沟通内容。
- “成交”必须等待受治理 POS/订单事实以引用方式确认；员工主观判断只能标为意向或待确认，不得写成已成交。
- 到期跟进仅显示在员工工作台中，属于人工待办提示；不向客户自动提醒或发送消息。
- 客户关系失效、授权撤回、离店交接或员工权限变化后，服务停止展示或写入超出新范围的记录，并保留受限审计/法定保留所需事实。

---

## 8. Permission Control

策略采用 **RBAC + ABAC**：先验证组织，再验证角色权限、门店归属、有效客户关系、声明用途、客户同意、字段分类和数据鲜度。任一条件不满足均默认拒绝；管理权限不自动授予逐客户 PII 访问权。

| 主体 | 可访问范围 | 可执行能力 | 关键限制 |
| --- | --- | --- | --- |
| 员工 | 自己被分配或被明确授权的客户，且在授权门店范围内。 | 查看机会、客户辅助包；提交本人跟进。 | 只能访问授权客户；无跨店浏览、批量导出或未授权 PII；不能发送消息/下单。 |
| 店长 | 所属门店的授权客户和门店机会队列。 | 查看门店队列、必要服务上下文、门店跟进质量汇总。 | 查看门店而非全组织；跨店逐客户访问必须单独授权；不能绕过客户同意。 |
| 管理层 | 所属组织/法人经营分析和去标识化指标。 | 查看门店/经营趋势、机会漏斗、接受率和数据质量。 | 默认不展示逐客户 PII、完整互动或个案画像；个案访问须明确理由和独立审批。 |
| 隐私/数据审核员 | 经分配的身份、同意或访问审核案件。 | 审核证据、策略和审计。 | 不能借审核权限进行销售、营销或日常客户浏览。 |
| 平台管理员 | 运行状态、策略配置所需元数据。 | 维护技术配置。 | 无默认业务 PII 权限；break-glass 限时、审批且全量审计。 |

所有访问审计应包含 `employee_id`、委托 AI 主体、角色、组织/门店、`customer_id`（或安全资源引用）、用途、策略决定、字段掩码、关联 ID、时间、数据版本和模型版本。导出、批量读取、权限提升和 break-glass 必须走独立审批流程。

---

## 9. Human Approval 与安全护栏

```text
AI 生成机会 / 方案 / 话术（只建议）
                    ↓
员工审阅：接受、编辑、拒绝或补问
                    ↓
员工核实客户需求、产品知识、尺码、价格和实时库存
                    ↓
员工通过已批准渠道自行沟通或在已批准系统中操作
                    ↓
员工记录结果；权威系统事实以引用方式回流
```

- 每个推荐和话术必须显示“仅供人工确认”、置信度、数据来源、更新时间及限制；低置信度、数据陈旧或依赖异常时自动抑制或降级。
- 员工必须对客户适配、库存、价格、促销资格和沟通内容承担最终判断；AI 输出不得被视为报价、合同、库存承诺或行动授权。
- 助手界面不提供“自动发送”“一键成交”“自动下单”“写入 SAP”或“修改 Core 同步”的能力，也不保留可被模型调用的对应工具。
- 对模型幻觉、提示注入、越权数据请求和不安全内容，系统拒绝执行、仅展示经批准知识/事实引用，并记录安全审计事件。

---

## 10. 验收标准

- [x] **Employee Context Model：** 定义 `employee_id`、`store_id`、`role`、`permissions`、`assigned_customers`、`sales_history`，并规定运行时重算和缓存隔离。
- [x] **Opportunity Dashboard：** 定义今日客户机会字段、张先生/KAILAS 示例、可解释优先级和受限展示规则。
- [x] **Customer Assistant API：** 定义 `GET /api/employee/opportunities`、`GET /api/employee/customer/{id}`、`POST /api/employee/followup` 的权限、请求、返回和错误语义。
- [x] **Follow-up Management：** 定义沟通时间、客户反馈、下一步动作、成交状态、版本化和权威事实确认规则。
- [x] **Sales Assistant Flow：** 定义从客户需求到推荐、产品方案、库存匹配、销售话术及人工确认的完整流程。
- [x] **Permission Control：** 定义员工仅限授权客户、店长查看门店、管理层查看经营分析，以及 RBAC + ABAC 审计控制。
- [x] **Human Approval：** 明确 AI 只建议、员工必须确认，并禁止自动营销、自动成交、自动下单、SAP 修改和 Core 生产同步修改。

本交付仅为设计文档；不包含部署、运行时配置、基础设施变更或生产数据操作。
