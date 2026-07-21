# DATA-003.2：VAFOX Recommendation Engine MVP 设计

**状态：** Design Phase / 仅设计，不部署  
**上游设计：** `DATA003_ARCHITECTURE_DESIGN.md`、`DATA003.1_CUSTOMER_IDENTITY_DESIGN.md`  
**目标链路：** Customer Brain + Knowledge Brain + Retail Brain → 客户需求 → 产品方案 → 库存匹配 → 员工建议  
**系统边界：** 本文定义只读、可解释、人工确认的推荐能力。SAP/ERP、POS、WMS、CRM 是各自事实源；Core 是受治理的企业事实中心。推荐结果是派生建议，不是订单、报价、库存预留或业务指令。

---

## 1. 设计原则与 MVP 范围

### 1.1 原则

| 原则 | MVP 要求 |
| --- | --- |
| 先治理、后推荐 | 每次请求先验证身份、组织/门店范围、声明用途、同意、字段策略、数据质量和新鲜度；默认拒绝。 |
| 三脑协作、事实不搬家 | Customer Brain 提供最小授权客户上下文；Knowledge Brain 仅提供已审批、有效的产品/场景知识；Retail Brain 提供只读产品、库存和销售聚合事实。 |
| 证据优先 | 每项推荐必须带理由、数据依据、来源引用、事实时间、质量状态、规则/模型版本与置信度。 |
| 先库存、再呈现 | 不把缺货或不可售商品作为可成交首选；库存不确定时明确降级或抑制。 |
| 人始终在环 | AI 只能生成建议和草稿；员工确认后再与客户沟通，结果只作为反馈记录。 |
| 最小化与可回放 | 使用 `customer_id` 和授权聚合特征，不返回原始 PII、完整订单或原始会话；保存可复现的输入版本与引用。 |

### 1.2 非目标与禁止项

本 MVP **不部署**模型、服务、连接器或工作流，也不产生任何生产写操作。明确禁止：

- 自动销售、自动触达客户、自动发送微信/短信；
- 自动下单、报价、库存预留、调拨、补货或价格修改；
- 修改 SAP，或修改 Core 生产同步、来源事实、CRM/POS/WMS/ERP 记录；
- 以推荐分数替代员工判断、客户授权、库存确认或产品安全/合规说明；
- 在推荐载荷、日志或训练样本中泄露原始身份标识。

---

## 2. Recommendation Context Model

### 2.1 上下文对象

`recommendation_context` 是一次推荐的最小、时点化输入快照。调用方可给出活动/地点/预算等显式需求；服务仅在授权、质量合格且未过期时补充客户画像。缺失值必须保留为 `unknown`/`null`，不能猜测敏感属性。

| 字段 | 类型/示例 | 来源与使用规则 |
| --- | --- | --- |
| `customer_id` | `cst_01J...` | 必填的伪匿名客户键；须位于请求组织范围内。无个性化授权时仅用于策略与最小服务上下文，个人特征不参与排序。 |
| `activity` | `high_altitude_hiking` | 客户明确需求优先；可含强度、天数、天气、同行者等非敏感约束。 |
| `location` | `{city:"深圳", destination:"南山"}` | 目的地/服务门店/渠道；用于场景知识和可售库存范围，不据此推断居住地。 |
| `season` | `summer` / `{start,end}` | 由客户声明或请求日期计算，带规则版本；跨季或不确定时标记 `unknown`。 |
| `budget` | `{currency:"CNY", min:1000, max:3000}` | 客户表达的预算区间；不以历史消费额推断预算。 |
| `customer_level` | `newcomer|casual|regular|advanced|unknown` | Customer Profile 的授权户外等级，含置信度、有效期和来源。 |
| `brand_preference` | `[{brand:"Mammut", affinity:"high"}]` | 经授权的品牌偏好聚合/客户声明；不是排他规则，须允许适配度和库存覆盖。 |
| `purchase_history` | 聚合特征/引用 | 只读、用途允许的类目、时间窗、退换状态和购买频率；不返回完整小票。 |
| `equipment_profile` | 装备类目、等级、使用场景、关系状态 | 只读引用；共享、退货、转移或质量不足时不能当作客户确定拥有。 |

### 2.2 必备元数据与上下文生成规则

上下文还必须包含 `organization_id`、`store_scope`、`channel`、`purpose`、`consent_summary`、`as_of`、`freshness`、`quality_state`、`lineage_refs`、`correlation_id` 与 `context_version`。所有时间使用 UTC RFC 3339。

```text
显式客户需求 + 已授权 Customer Brain 特征 + 请求门店/渠道约束
                    ↓
             policy / consent / quality gate
                    ↓
      最小 recommendation_context（可回放、可过期）
```

- 个性化用途未获 `granted` 授权时，移除 `brand_preference`、`purchase_history`、`equipment_profile` 等个人特征，返回同门店/场景的非个性化建议，并标记 `personalization_applied: false`。
- 客户身份冲突、画像过期、来源隔离、质量为 `quarantined` 或范围越权时，拒绝或抑制受影响字段/推荐，不能以模型补全。
- 上下文的保存是派生快照或引用，不替代 Customer Master、订单、产品或库存事实。

---

## 3. Recommendation Engine Architecture

```text
Customer Context
      ↓  consent / policy / freshness / quality gates
Knowledge Retrieval
      ↓  approved, effective, cited product-and-scenario knowledge
Product Matching
      ↓  candidate products and compatible solution bundles
Inventory Validation
      ↓  authorized store availability, sales velocity, stock health
Recommendation Score
      ↓  ranked advisory proposals with evidence and limitations
Human Approval
      ↓
employee confirmation → customer communication → outcome feedback
```

| 阶段 | 输入 | 处理 | 输出/硬控制 |
| --- | --- | --- | --- |
| Customer Context | `recommendation_context` | 组织、角色、门店、用途、同意、字段掩码和质量校验。 | 最小授权特征；拒绝 `POLICY_DENIED`，或降级为非个性化。 |
| Knowledge Retrieval | 活动、季节、地点、产品类目 | 仅检索 `approved` 且处于有效期的知识资产：适用场景、技术参数、尺码/安全提示、搭配规则、品牌资料。 | 带 `knowledge_id`、版本、片段引用和适用限制；不把生成文本当政策。 |
| Product Matching | 上下文 + 知识 + 受治理产品目录 | 先满足硬条件（活动适配、安全/法规、预算、渠道可售、互斥/兼容关系），再计算候选得分。 | 产品候选及未入选/排除理由。 |
| Inventory Validation | 候选 + 门店范围 | 查询库存位置、可售状态、更新时间、销售速度和库存健康；不查询即预留。 | 可售门店候选、库存证据、缺货/陈旧抑制原因。 |
| Recommendation Score | 合格候选 | 以版本化、可解释的加权规则排序，并应用多样性、品牌公平和疲劳限制。 | 单品/组合、分项贡献、置信度、过期时间。 |
| Human Approval | 推荐卡片 | 员工接受、编辑、拒绝或要求补充信息；确认后才可沟通。 | 审批/反馈审计；没有任何自动业务执行。 |

MVP 可采用确定性规则和透明加权排序；未来机器学习模型只能在离线验证、隐私/业务/模型风险审批、版本化发布与回滚方案齐备后替换其中的排序器。

---

## 4. Product Recommendation Model

### 4.1 匹配因素与硬约束

| 因素 | 信号 | 使用方式 |
| --- | --- | --- |
| 客户画像 | 户外等级、兴趣标签、消费带、授权状态 | 在授权范围内评估复杂度与适合度；未知不得扣分或臆测。 |
| 活动场景 | 活动、地点、季节、天气/时长（如已提供） | 作为技术需求和产品类目筛选的主要依据。 |
| 产品知识 | 已审批的场景适配、材质、功能、兼容性、护理和限制 | 用于验证产品可解释地满足需求，并生成引用理由。 |
| 历史购买 | 已购类目、退换状态、购买窗口 | 用于避免不必要重复、补齐缺口或识别兼容搭配；绝不把购买记录等同于偏好。 |
| 品牌偏好 | 客户声明或授权亲和度 | 作为软偏好；当适配、安全、预算或可售性冲突时不得压过硬约束。 |
| 库存状态 | 门店可售、库存健康、销售速度、时间戳 | 候选必须通过库存校验，或明确作为“可替代/需调货人工确认”。 |

硬约束包括：知识资产未审批/失效、产品停售或渠道不可售、活动不适配、关键兼容性冲突、超预算（除非作为显式备选）、库存数据过期/隔离、访问越权。任何硬约束失败都不进入可推荐排序。

### 4.2 MVP 评分与组合规则

对于通过硬约束的商品 (p)，使用归一化分项：

```text
product_score(p) =
  0.30 × activity_fit
+ 0.20 × product_knowledge_fit
+ 0.15 × customer_profile_fit
+ 0.10 × purchase_history_fit
+ 0.10 × brand_preference_fit
+ 0.15 × inventory_fit
- penalties
```

- 每个分项范围为 `0.00–1.00`，并记录来源；`penalties` 包含预算偏离、低库存、低鲜度、重复购买风险、知识限制和数据质量风险。
- 缺少授权或可靠数据时，该项权重重新分配到活动/知识/库存等非个人项，并在响应中报告 `personalization_applied` 与 `scoring_adjustments`。
- `solution_bundle` 由一个主商品加经知识规则确认的互补商品构成（如硬壳 + 中层 + 防水配件）；不得通过捆绑规避预算、库存或产品兼容性规则。
- 并列时优先更高库存健康、更近授权门店、更高证据质量和更多样化的候选，不因品牌亲和度单独胜出。

`confidence` 不是成交概率。它衡量当前建议的证据完整性、输入鲜度、知识覆盖和规则稳定性；建议以 `high`（≥0.80）、`medium`（0.60–0.79）、`low`（<0.60）呈现。低置信度建议必须显示限制并要求员工补问或复核，严重缺失则抑制而不是展示。

---

## 5. Inventory Recommendation Integration

### 5.1 库存查询与门店推荐逻辑

```text
产品需求
   ↓
门店库存（on_hand / sellable / reserved reference / freshness）
   ↓
销售速度（授权时间窗的日均销量、异常标记）
   ↓
库存健康（覆盖天数、滞销/断货风险、质量）
   ↓
推荐门店（可售且健康的门店；人工确认后才可服务）
```

| 步骤 | 规则 | 输出 |
| --- | --- | --- |
| 产品需求 | 从产品匹配产生 SKU/变体、数量和可替代规则。 | `product_id`、变体、需求优先级。 |
| 门店库存 | 在调用者获授权的 `store_scope` 查询 Core 认证快照；区分 `on_hand` 与 `sellable`，不将任何数字视为预留。 | 每店可售状态、库存量区间/状态、`inventory_as_of`、血缘。 |
| 销售速度 | 使用版本化窗口（默认 30 天）的聚合销量；退货、促销异常和低样本须标记。 | `velocity_band`、样本充分性、销售事实引用。 |
| 库存健康 | 结合可售量、覆盖天数、补货在途引用、滞销/断货风险和质量状态。 | `healthy|watch|low|stale|quarantined` 与原因。 |
| 推荐门店 | 首选 `sellable` 且 `healthy/watch` 的门店；距离/便利性只有客户明确给出时才参与。 | 最多 3 个候选门店、替代品或人工确认提示。 |

库存数据超过定义 SLA、销售样本不足、质量隔离或库存状态未知时，系统返回 `INVENTORY_STALE`、`INSUFFICIENT_SALES_SIGNAL` 或 `INVENTORY_UNAVAILABLE` 的限制，降级为“请员工核实”，不得声称有货、锁货或建议跨店调拨。

### 5.2 门店排序示例

```text
store_score = 0.55 × sellable_availability
            + 0.25 × stock_health
            + 0.20 × sales_velocity_stability
```

门店排序仅用于建议员工优先核实的服务地点；不产生门店间库存移动、补货、预留或客户承诺。库存健康用作可持续供给信号，不应用来驱动自动清库存或强制销售。

---

## 6. Recommendation Explanation

每一条单品和组合建议都必须返回以下字段：**推荐理由**、**数据依据**、**来源引用**、**置信度**；同时返回事实时间、数据限制、规则/模型版本和 `advisory_only`。理由必须把“客户声明/来源事实/派生推断”清晰区分。

```json
{
  "recommendation_id": "rec_01J...",
  "product": {"product_id": "prd_mammut_shell_...", "name": "Mammut 硬壳"},
  "recommendation_reason": [
    "高海拔徒步场景与该硬壳的防风雨技术要求匹配",
    "客户已授权的户外品牌偏好包含 Mammut",
    "南山店库存状态为 healthy，快照仍在 SLA 内"
  ],
  "data_basis": [
    {"kind": "declared_activity", "value": "high_altitude_hiking", "as_of": "2026-07-21T09:00:00Z"},
    {"kind": "customer_brand_affinity", "value": "Mammut: high", "as_of": "2026-07-20T00:00:00Z"},
    {"kind": "inventory_snapshot", "store_id": "store_nanshan", "state": "healthy", "as_of": "2026-07-21T09:05:00Z"}
  ],
  "source_references": [
    {"type": "knowledge_asset", "ref": "kb_...", "version": "v3"},
    {"type": "customer_feature", "ref": "feat_..."},
    {"type": "inventory_position", "ref": "lin_..."}
  ],
  "confidence": {"score": 0.84, "level": "high", "basis": ["fresh inventory", "approved knowledge", "complete activity context"]},
  "limitations": [],
  "disposition": "advisory_only_requires_human_approval"
}
```

来源引用应为稳定的 ID/血缘引用，不在普通响应暴露原始订单、身份标识或受限知识全文。若客户偏好未获授权，解释只能写“按活动与库存的非个性化匹配”，不能暗示使用了个人历史。

---

## 7. API Contract

**基础路径：** `/api/recommendation`  
**认证与共同请求头：** `Authorization`、`X-Correlation-Id`、`X-Purpose`、`X-Organization-Id`；员工助手还需要员工身份、角色、门店范围和短时委托信息。所有接口返回 JSON、UTC RFC 3339 时间和 `advisory_only` 状态。

### 7.1 `POST /api/recommendation`

生成一次即时、只读的推荐快照；不是订单或任务创建接口。需要 `recommendation:generate` 权限，且 `purpose` 为批准的 `customer_service`、`clienteling` 或 `analytics`。

```json
{
  "customer_id": "cst_01J...",
  "activity": "high_altitude_hiking",
  "location": {"store_id": "store_nanshan", "destination": "高海拔山区"},
  "season": "summer",
  "budget": {"currency": "CNY", "min": 1000, "max": 3000},
  "channel": "store",
  "limit": 5,
  "include_bundles": true
}
```

成功响应至少包括 `recommendations`（推荐商品）、`bundles`（推荐组合）、`recommendation_reason`、`inventory_locations`、`source_references`、`confidence`、`freshness`、`policy`、`model`、`limitations` 和 `correlation_id`。`limit` 为 1–20，默认 5；不得接受原始手机号或微信号。

### 7.2 `GET /api/recommendation/{customer_id}`

读取该客户在调用者组织/门店范围内、仍未过期的推荐历史/当前快照；需要 `recommendation:read`。查询参数：`store_id`（必填）、`activity`（可选）、`status`（`active|expired|suppressed`）、`cursor`、`limit`（最大 20）、`as_of`。此接口不重新推断身份，亦不返回未经授权的个性化字段。

```json
{
  "customer_id": "cst_01J...",
  "recommendations": [{"recommendation_id": "rec_01J...", "rank": 1, "product": {"product_id": "prd_..."}, "recommendation_reason": ["..."], "inventory_locations": [{"store_id": "store_nanshan", "availability": "sellable", "as_of": "2026-07-21T09:05:00Z"}], "source_references": [{"type": "knowledge_asset", "ref": "kb_..."}], "confidence": {"score": 0.84, "level": "high"}}],
  "bundles": [],
  "policy": {"personalization_applied": true, "decision": "allow"},
  "freshness": {"context_as_of": "2026-07-21T09:00:00Z", "inventory_as_of": "2026-07-21T09:05:00Z"},
  "disposition": "advisory_only_requires_human_approval",
  "correlation_id": "corr_..."
}
```

标准错误：`400 INVALID_REQUEST`、`401 UNAUTHENTICATED`、`403 POLICY_DENIED`、`404 RECOMMENDATION_NOT_FOUND`（仅可安全披露时）、`409 CONTEXT_STALE`、`422 CONSENT_REQUIRED`、`503 DEPENDENCY_UNAVAILABLE`。审计仅记录主体、用途、范围、策略结果、引用、版本和关联 ID；不得记录完整 PII 或响应正文。

---

## 8. Human Approval Flow

```text
AI 只建议
   ↓
员工确认（接受 / 编辑 / 拒绝 / 补问）
   ↓
员工与客户沟通
   ↓
结果反馈（事实结果 + 员工评价）
```

1. **AI 只建议：** 推荐卡片明确显示适配理由、库存时间、置信度、限制和“需人工确认”。
2. **员工确认：** 获授权员工检查客户需求、尺码/技术适配、实时库存和知识限制，可接受、编辑或拒绝，并记录原因；高风险/低置信度情形要求经理或专业人员复核。
3. **客户沟通：** 仅由员工通过已批准渠道沟通；客户决定是否购买。推荐服务不发送任何消息、不创建任务、不做价格或库存承诺。
4. **结果反馈：** 员工录入建议是否有用、是否展示、客户回应和原因码；成交/退换等结果从受治理事实源以引用方式关联，不能由模型自行断言。

任何“确认”仅确认建议可被沟通，绝不授权自动销售、自动下单、修改 SAP 或修改 Core 生产同步。

---

## 9. Feedback Loop

```text
推荐
  ↓
成交（或未成交 / 退换 / 无反馈）
  ↓
结果记录
  ↓
优化模型/规则
```

| 环节 | 记录内容 | 控制 |
| --- | --- | --- |
| 推荐 | 推荐 ID、上下文/证据引用、排序版本、分数、库存快照、展示状态。 | 不保存超出保留策略的原始 PII；推荐快照不可静默改写。 |
| 成交 | 仅关联受治理订单/POS 事实的结果引用、观察时间与退换状态。 | “成交”与“因推荐成交”分开；不得把相关性当因果。 |
| 结果记录 | 员工接受/编辑/拒绝、原因码、客户反馈、缺货/尺码等限制。 | 由员工或权威来源记录；模型输出不是结果事实。 |
| 优化模型 | 覆盖率、库存准确性、接受率、编辑率、结果质量、鲜度、分群/门店公平性。 | 仅使用许可、最小化、去标识化数据离线评估；防止标签泄漏。 |

规则或模型更新必须经业务所有者、数据/隐私安全和模型风险审批，保留训练数据版本、评估报告、可解释性检查、灰度/影子评估和回滚版本。数据质量、同意变化、漂移、库存鲜度或异常公平性触发时，自动**抑制展示**或降级为人工核实；这不是任何业务系统操作。

---

## 10. 验收标准

- [x] **Customer Context：** 定义 `customer_id`、活动、地点、季节、预算、客户等级、品牌偏好、购买历史和装备档案，并包含授权、质量、血缘和新鲜度控制。
- [x] **Product Knowledge Retrieval：** 仅检索已审批、有效、可引用的场景与产品知识，并返回限制。
- [x] **Inventory Query：** 定义产品需求 → 门店库存 → 销售速度 → 库存健康 → 推荐门店链路及陈旧数据抑制。
- [x] **Recommendation Algorithm：** 定义硬约束、六类匹配因素、透明 MVP 加权评分、组合规则和置信度语义。
- [x] **Recommendation Explanation：** 每项建议包含推荐理由、数据依据、来源引用、置信度、限制和版本。
- [x] **Human Approval：** 明确 AI 建议、员工确认、客户沟通、结果反馈的责任边界。
- [x] **Recommendation API：** 定义 `POST /api/recommendation` 与 `GET /api/recommendation/{customer_id}` 及商品、组合、理由、库存位置、引用返回契约。
- [x] **Feedback Loop：** 定义推荐、成交、结果记录、离线优化及审批/回滚治理闭环。

本设计验收只验证设计契约完整性；不包含部署、生产数据接入、模型训练、SAP/Core 写入或自动化销售能力。
