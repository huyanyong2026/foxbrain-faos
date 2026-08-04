# VAFOX Huyan Portal V1.9 Supply Chain Intelligence Design Report

**文档类型：** 供应链分析设计报告（仅设计，不含代码实现）  
**版本：** V1.9  
**设计基线：** VAFOX Three Portal Architecture、Huyan V1.8 已完成模块  
**目标 Portal：** Huyan CEO Portal  
**状态：** 待数据合同、权限合同与验收条件确认后实施

## 1. 设计结论

V1.9 在 V1.8 的 CEO Today、经营分析、商品分析、库存分析、客户分析、组织分析及其统一导航、只读交互、数据溯源和可信空状态基础上，设计独立的“供应链分析”能力。范围包括供应链总览、供应商表现分析、品牌供应关系、采购协同分析、供应链风险分析和 AI 供应链建议。

本设计只在 Huyan Business Application Layer 增加一个**拟议的只读聚合合同**，不要求也不允许修改 SAP B1、SAP Mirror、Data Core、Auth 或 AI Runtime。数据流保持为：

> SAP B1 → SAP Mirror → Data Core → 既有 Core 只读能力 → Huyan Business Application Layer → Huyan CEO Portal

V1.9 不新增事实源，不直连 SAP B1、SAP Mirror 或 Data Core 存储，不写回采购、供应商、库存或商品数据，不执行下单、审批、催交、调拨、停供或供应商触达。所有建议均为只读决策辅助。

## 2. 设计原则与边界

1. **真实数据优先：** 只消费 Core 已发布且合同确认的 Supplier Master、采购数据和库存关联数据；不使用 mock、fixture、faker、本地快照、硬编码业务数字或猜测数据。
2. **服务端聚合：** 供应商、品牌、采购和库存的关联、口径计算及字段过滤必须在 Business Application Layer 完成，浏览器不拼接不同数据域。
3. **只读与可追溯：** 响应必须包含来源、更新时间、鲜度、完整性、只读标识和关联质量；页面必须展示数据状态。
4. **缺失即显式：** 缺少采购事实或采购数据未达到上游确认的完整状态时，不以销售、客户、库存变动或历史静态值代替采购事实。
5. **最小权限：** V1.9 页面及 API 仅供已认证 Huyan CEO 全域数据范围使用；前端传入的角色或范围不构成授权依据。
6. **域隔离：** 客户域与供应商域在输入、处理、响应、缓存、日志和 AI 上下文中保持隔离。
7. **不越过 Three Portal 边界：** Huyan CEO Portal 只获得面向管理层的供应链投影。其他 Portal 不继承该响应；如未来需要员工或供应商视图，必须另建经治理、按主体裁剪的合同和权限评审。

### 2.1 明确不在 V1.9 范围内

- 修改 SAP B1、SAP Mirror、Data Core、Auth、AI Runtime；
- 新建或回填 Supplier Master、采购、收货、库存或品牌事实；
- 供应商门户、供应商账号、供应商消息推送或把内部经营数据发给供应商；
- 采购单创建/修改/审批、收货确认、付款、退货、调拨或库存调整；
- 对缺失交期、质量、价格、合同、采购或库存字段进行推断；
- 将 AI 建议当作已批准业务指令或自动执行动作。

## 3. 用户、信息架构与页面状态

### 3.1 目标用户与入口

- **用户：** 具有 `VAFOX_CEO` 角色及 `ALL_DATA` 数据范围的 Huyan CEO Portal 用户。
- **入口：** 沿用 V1.8 一级导航中的“供应链分析”，不改变其他栏目顺序和既有模块行为。
- **视觉：** 沿用白色画布、浅灰分区、细边框卡片、VAFOX 橙色强调、数据溯源条、桌面表格及移动端单列/横向滚动规范。
- **交互：** 默认只读；支持已定义维度的筛选、排序、分页和刷新，不提供执行按钮。

### 3.2 统一页面状态

| 状态 | 触发条件 | 页面行为 |
| --- | --- | --- |
| 加载中 | 请求尚未完成 | 显示结构性加载状态，不显示占位业务数字 |
| 正常 | 权限通过，三个来源满足模块合同 | 展示真实聚合结果及溯源信息 |
| 采购同步中 | 采购来源缺失、上游声明未完成/不可用，或采购关联数据不足以形成可信分析 | 所有依赖采购事实的模块统一显示“**供应链数据同步中**”，不得生成排名、金额、趋势、风险或 AI 结论 |
| 局部治理中 | 采购数据可用，但特定非采购字段缺失 | 保留可信字段；受影响字段显示“数据待补齐”，并在 `limitations[]` 说明，不推断 |
| 空数据 | 来源完整且查询周期内确实没有记录 | 显示“当前范围暂无供应链数据”，与同步中严格区分 |
| 无权限 | 身份无效或缺少角色/范围 | `401/403` 专用状态，不泄露数据是否存在 |
| 服务异常 | 上游超时、合同异常或聚合失败 | 显示“供应链数据暂不可用”，允许重新加载，不使用本地回退 |

## 4. 数据来源与数据合同

V1.9 只读取以下三个受治理的数据产品。这里定义的是 Business Application Layer 所需的**逻辑字段**，不指定或修改 Data Core 的物理表、方法名或存储结构；实施前必须由 Data Core 负责人完成逻辑字段到既有只读合同的映射确认。

### 4.1 Supplier Master（供应商主数据）

| 逻辑字段 | 必需性 | 用途与规则 |
| --- | --- | --- |
| `supplier_id` | 必需 | 供应商内部稳定标识；用于服务端关联，禁止由名称代替 |
| `supplier_name` | 必需 | CEO Portal 展示名称 |
| `supplier_status` | 必需 | 上游定义的有效/停用等状态；不自行解释未知枚举 |
| `brand_ids[]` | 可选 | 仅当主数据已治理供应商—品牌关系时使用 |
| `updated_at` | 必需 | 鲜度和溯源 |

未在源合同中存在的供应商等级、账期、合同状态、联系人、地址、银行信息和质量认证不得补造，也不进入 V1.9 输出。采购事实中找不到 Supplier Master 的 `supplier_id` 时，该记录进入 `unmatched_supplier` 治理计数，不归给任何供应商。

### 4.2 采购数据

| 逻辑字段 | 必需性 | 用途与规则 |
| --- | --- | --- |
| `purchase_document_id` | 必需 | 采购业务单据的稳定标识；页面输出可使用脱敏展示标识 |
| `purchase_line_id` | 必需 | 去重与行级关联 |
| `supplier_id` | 必需 | 关联 Supplier Master |
| `sku_id` | 必需 | 关联品牌与库存 |
| `order_date` | 必需 | 周期筛选、趋势与采购频次 |
| `ordered_quantity` | 必需 | 采购量；只接受上游有效数值 |
| `ordered_amount` | 可选 | 采购金额；缺失时不得用销售价、库存价或猜测单价反推 |
| `expected_delivery_date` | 可选 | 交付及时性与到货风险依据 |
| `received_date` | 可选 | 已收货行的实际到货日 |
| `received_quantity` | 可选 | 到货率依据 |
| `document_status` | 必需 | 仅按上游确认状态分类，不自行推断取消/关闭 |
| `brand_id` | 可选 | 优先使用受治理商品主数据关系；不得从 SKU 名称猜品牌 |
| `updated_at` | 必需 | 鲜度和溯源 |

采购数据是供应商采购额、采购单量、到货率、准时率、未交数量、采购趋势和采购协同的唯一事实来源。未确认退货、取消、税额、币种折算及金额口径前，不将其纳入指标。

### 4.3 库存关联数据

| 逻辑字段 | 必需性 | 用途与规则 |
| --- | --- | --- |
| `sku_id` | 必需 | 与采购行关联 |
| `brand_id` | 必需（品牌分析） | 品牌供应关系；缺失时进入未关联桶 |
| `location_id` | 可选 | 已授权库存范围内的地点维度 |
| `on_hand_quantity` | 必需 | 当前库存数量 |
| `available_quantity` | 可选 | 仅在上游已定义时展示 |
| `inventory_amount` | 可选 | 仅在成本状态可信时展示 |
| `inventory_status` | 可选 | 只消费上游确认状态 |
| `updated_at` | 必需 | 鲜度和溯源 |

库存数据用于解释采购与库存协同，不反向证明采购曾发生。库存无供应商标识时，只能通过同一 `sku_id` 的受治理采购关系形成聚合关系；多供应商 SKU 必须展示多供应关系，不把全部库存归给任一供应商。

### 4.4 关联键、质量与禁止关联

合法关联路径仅为：

1. `purchase.supplier_id = supplier_master.supplier_id`；
2. `purchase.sku_id = inventory.sku_id`；
3. `purchase.brand_id = inventory.brand_id`，或经已治理的 SKU—品牌关系取得 `brand_id`。

禁止以供应商名称、商品名称、客户名称、地址、电话号码或模糊文本匹配建立关系。响应必须返回：

- `join_quality.matched_purchase_lines`；
- `join_quality.unmatched_supplier_lines`；
- `join_quality.unmatched_inventory_skus`；
- `join_quality.unmatched_brand_lines`；
- `join_quality.status`：仅接受上游/聚合层定义的 `complete | partial | unavailable`；
- `limitations[]`：明确哪些模块或字段受影响。

## 5. 指标口径

所有计算均为对真实、已通过合同校验记录的确定性聚合。比率分母为零时返回 `null` 和对应限制说明，不返回 `0` 伪装为已计算结果。

| 指标 | 计算口径 |
| --- | --- |
| 供应商数量 | 查询范围内存在有效采购事实的去重 `supplier_id` 数；另列 Supplier Master 总数，不混用 |
| 采购单量 | 去重 `purchase_document_id` 数 |
| 采购行数 | 去重 `purchase_line_id` 数 |
| 采购数量 | 合同有效采购行的 `ordered_quantity` 合计 |
| 采购金额 | 仅汇总存在可信 `ordered_amount` 的有效采购行；完整性不足时金额为 `null` |
| 已收数量 | `received_quantity` 合计 |
| 到货率 | `已收数量 / 采购数量`；仅对口径确认的非零分母计算 |
| 准时率 | 同时具有预计和实际到货日期的已收货行中，`received_date <= expected_delivery_date` 的行数占比 |
| 未交数量 | `max(ordered_quantity - received_quantity, 0)`；仅在两字段均可信时计算 |
| 供应品牌数 | 与有效采购行通过受治理关系关联的去重 `brand_id` 数 |
| 库存数量 | 查询范围内关联 SKU 的 `on_hand_quantity` 合计；多供应商 SKU 只在 SKU/品牌层展示，不重复计入供应商合计 |

“供应商表现”是事实指标集合，不设计综合分数、星级或主观优劣标签，避免未经确认的权重和阈值。

## 6. 六个分析模块

### 6.1 供应链总览

展示数据状态、活跃采购供应商数、采购单量、采购数量、可信时的采购金额、到货率、准时率、未交数量、关联品牌数，以及采购/库存更新时间。总览必须同时显示完整性和未关联计数，避免汇总数字脱离数据质量语境。

### 6.2 供应商表现分析

按供应商展示采购金额（可信时）、采购数量、采购单量、到货率、准时率、未交数量、供应品牌数和最近采购日期。支持对真实返回字段排序；缺失交付字段时不生成到货率或准时率，也不生成表现排名。

### 6.3 品牌供应关系

以品牌为主视角展示 `brand_id`、品牌名称（仅来自既有受治理品牌投影）、供应商列表、供应商数量、采购数量、可信采购金额、关联库存数量和最近采购日期。多供应商关系以数组原样保留；不推断“主供应商”、独家关系或依赖度。若业务未来需要依赖度，必须先单独确认金额完整性、时间窗和指标公式。

### 6.4 采购协同分析

展示按供应商/品牌组织的采购量、已收量、未交量、预计到货日期、实际到货日期、单据状态、到货率及与当前库存的并列视图。库存只提供决策上下文，不自动产生采购订单、催交通知或调拨动作。

### 6.5 供应链风险分析

V1.9 只输出能够由明确事实规则直接证明的风险项：

- 已超过 `expected_delivery_date` 且上游状态未关闭、可信未交数量大于零的采购行：`overdue_delivery`；
- 已收货且 `received_date > expected_delivery_date`：`late_delivery`；
- 采购行无法关联 Supplier Master：`supplier_link_missing`；
- 采购 SKU 无法关联库存或品牌：`inventory_link_missing` / `brand_link_missing`；
- 上游数据状态为部分或不可用：`data_quality`。

风险输出必须包含事实依据、涉及对象、日期/数量、数据来源和限制。缺少阈值时不得自行定义高/中/低风险，不预测断供、涨价、质量事故或供应商经营状况。

### 6.6 AI 供应链建议

AI 仅接收本 API 已授权、已白名单化、无客户字段的供应链聚合结果与事实风险；不得直连数据源或补充外部/猜测事实。每条建议固定采用以下结构：

```json
{
  "conclusion": "结论",
  "evidence": [
    {
      "fact": "依据",
      "source": "purchase | supplier_master | inventory",
      "reference_ids": ["受控内部引用标识"]
    }
  ],
  "recommendation": "建议"
}
```

页面中文标签固定为：

1. **结论**：对已提供事实的简洁归纳，不声明预测为事实；
2. **依据**：至少一项可回溯事实，标明来源和受控引用；
3. **建议**：只读、可供人工评估的下一步，不表述为已执行或已批准。

若依据为空、数据完整性不足或采购数据处于同步中，则 `ai_advice.items = []`，`ai_advice.status = "unavailable"`，页面显示“供应链数据同步中”，不得让模型补齐结论。AI 输出不得包含客户身份、客户行为、客户偏好、客户机会或由客户数据推导的供应商建议。

## 7. API 设计

### 7.1 总体合同

**拟议路径：** `GET /api/business/supply-chain-intelligence`  
**性质：** 只读、服务端聚合、Huyan CEO Portal 专用  
**说明：** 这是 V1.9 设计合同，不表示当前路由已经实现。实施只能复用既有 Gateway、Auth 和 Data Core 只读能力，不修改受保护系统。

不直接扩展既有 `GET /api/business/supplier-analysis` 作为 V1.9 完整合同：该接口仅适合作为 V1.4 供应商白名单投影，缺少采购、库存关联、完整性、风险和 AI 建议字段。实施时可保持其兼容性，但 V1.9 页面只请求上述单一新聚合合同，避免浏览器跨接口拼接。

### 7.2 输入

#### HTTP 请求头

| 输入 | 必需 | 规则 |
| --- | --- | --- |
| 既有认证凭证 | 是 | 由现有 Gateway/Auth 验证；请求体和查询参数不得声明身份 |
| 可信 Portal 上下文 | 是 | 必须解析为 `huyan.vafox.com` |
| 可信角色范围 | 是 | 必须包含 `VAFOX_CEO` |
| 可信数据范围 | 是 | 必须为 `ALL_DATA` |
| `X-Request-ID` | 否 | 用于链路与审计；不存在时沿用平台既有生成规则 |

`portal`、`role`、`permission`、`data_scope`、供应商访问范围均不得由浏览器查询参数覆盖。

#### 查询参数

| 参数 | 类型 | 必需 | 规则 |
| --- | --- | --- | --- |
| `date_from` | `YYYY-MM-DD` | 是 | 采购事实起始日期 |
| `date_to` | `YYYY-MM-DD` | 是 | 采购事实结束日期；不得早于 `date_from` |
| `supplier_id` | string | 否 | 精确筛选已授权供应商标识，不接受名称模糊关联 |
| `brand_id` | string | 否 | 精确筛选已治理品牌标识 |
| `location_id` | string | 否 | 仅限 `ALL_DATA` 下的已治理库存地点 |
| `page` | positive integer | 否 | 明细分页；默认值和上限由现有平台标准统一配置，不在本设计中猜测 |
| `page_size` | positive integer | 否 | 同上，服务端强制平台上限 |

输入非法返回 `400 invalid_request`；筛选不得扩大认证范围。V1.9 不接收客户标识、客户分层、客户偏好或任意自然语言筛选条件。

### 7.3 成功输出字段

```json
{
  "version": "1.9",
  "read_only": true,
  "domain": "supply_chain",
  "query": {
    "date_from": "YYYY-MM-DD",
    "date_to": "YYYY-MM-DD",
    "supplier_id": null,
    "brand_id": null,
    "location_id": null
  },
  "data_status": {
    "status": "ready | partial | syncing",
    "message": null,
    "sources": [
      {
        "name": "supplier_master | purchase | inventory",
        "status": "ready | partial | unavailable",
        "updated_at": "ISO-8601 timestamp"
      }
    ],
    "limitations": []
  },
  "join_quality": {
    "status": "complete | partial | unavailable",
    "matched_purchase_lines": 0,
    "unmatched_supplier_lines": 0,
    "unmatched_inventory_skus": 0,
    "unmatched_brand_lines": 0
  },
  "overview": {
    "supplier_count": 0,
    "supplier_master_count": 0,
    "purchase_order_count": 0,
    "purchase_line_count": 0,
    "purchase_quantity": 0,
    "purchase_amount": null,
    "received_quantity": null,
    "receipt_rate": null,
    "on_time_rate": null,
    "open_quantity": null,
    "brand_count": 0
  },
  "supplier_performance": [],
  "brand_supply_relationships": [],
  "procurement_collaboration": [],
  "risks": [],
  "ai_advice": {
    "status": "ready | unavailable",
    "items": []
  },
  "pagination": {
    "page": 1,
    "page_size": 0,
    "total_items": 0
  },
  "trace": {
    "request_id": "string",
    "generated_at": "ISO-8601 timestamp",
    "source_names": ["Supplier Master", "采购数据", "库存关联数据"]
  }
}
```

数组元素字段如下；所有可空字段必须返回 `null` 或省略，并在 `limitations[]` 说明，不用虚构值替代。

| 对象 | 输出字段 |
| --- | --- |
| `supplier_performance[]` | `supplier_id`, `supplier_name`, `supplier_status`, `purchase_order_count`, `purchase_quantity`, `purchase_amount`, `received_quantity`, `receipt_rate`, `on_time_rate`, `open_quantity`, `brand_count`, `last_purchase_date`, `limitations[]` |
| `brand_supply_relationships[]` | `brand_id`, `brand_name`, `supplier_count`, `suppliers[{supplier_id,supplier_name}]`, `purchase_quantity`, `purchase_amount`, `inventory_quantity`, `last_purchase_date`, `limitations[]` |
| `procurement_collaboration[]` | `purchase_document_ref`, `supplier_id`, `supplier_name`, `brand_id`, `brand_name`, `sku_id`, `order_date`, `expected_delivery_date`, `received_date`, `ordered_quantity`, `received_quantity`, `open_quantity`, `document_status`, `inventory_quantity`, `limitations[]` |
| `risks[]` | `risk_id`, `risk_type`, `supplier_id`, `brand_id`, `sku_id`, `purchase_document_ref`, `conclusion`, `evidence[]`, `source_names[]`, `limitations[]` |
| `ai_advice.items[]` | `conclusion`, `evidence[{fact,source,reference_ids[]}]`, `recommendation` |

响应中明确禁止客户字段，包括但不限于 `customer_id`、`customer_name`、联系方式、消费金额、订单、会员等级、偏好、Customer360 标签和客户机会。

### 7.4 同步中输出

采购数据不足时返回可识别的受控状态，不返回部分采购排名或 AI 猜测：

```json
{
  "version": "1.9",
  "read_only": true,
  "domain": "supply_chain",
  "data_status": {
    "status": "syncing",
    "message": "供应链数据同步中",
    "sources": [],
    "limitations": ["purchase_data_unavailable_or_incomplete"]
  },
  "overview": null,
  "supplier_performance": [],
  "brand_supply_relationships": [],
  "procurement_collaboration": [],
  "risks": [],
  "ai_advice": {"status": "unavailable", "items": []}
}
```

“不足”必须由真实上游可用性/完整性元数据、合同校验失败或必需关联键缺失确定，不得由开发者随意设置业务数量阈值。HTTP 状态按平台既有错误语义执行：可正常读取状态但尚未完成同步时可返回 `200` 加 `syncing`；真实上游读取失败或合同不可解析时返回 `503 supply_chain_data_unavailable`，页面仍显示“供应链数据同步中”并记录技术错误供运维排查。

### 7.5 错误与权限输出

| HTTP | `error` | 场景 |
| --- | --- | --- |
| `400` | `invalid_request` | 日期、筛选或分页参数非法 |
| `401` | `authentication_required` | 无有效身份 |
| `403` | `all_data_scope_required` | 非 Huyan CEO、缺少 `VAFOX_CEO` 或不是 `ALL_DATA` |
| `503` | `supply_chain_data_unavailable` | 真实来源不可用、超时或合同异常 |

错误体只返回 `error`、安全的 `message` 和 `request_id`，不返回上游凭证、SQL、堆栈、客户信息或内部网络信息。

### 7.6 权限、审计与缓存要求

- Gateway 使用既有可信身份映射；Business Application Layer 再校验 CEO 角色和 `ALL_DATA`，任一失败即拒绝。
- 只允许 `GET`；任何写方法返回不允许，不向上游发起写操作。
- 审计记录请求人、Portal、角色判定、数据范围、筛选范围、结果状态、来源鲜度、请求 ID 和时间，不记录采购行全文或客户数据。
- 缓存键至少隔离 Portal、授权主体/范围、日期与供应商/品牌/地点筛选；不得与客户分析或其他 Portal 共用响应缓存。
- 页面不得把 API 响应写入本地持久存储，也不得把完整供应链数据传给未授权前端分析服务。

## 8. 数据缺失与降级策略

### 8.1 采购数据不足（强制规则）

出现以下任一情况即进入“供应链数据同步中”：

- 采购数据产品未配置、不可访问、超时或上游明确标记 `unavailable`；
- 必需采购字段或唯一键缺失，无法通过合同校验；
- 上游明确标记本查询范围同步未完成；
- 采购行无法可靠关联 Supplier Master，导致供应商分析不可信；
- 返回的完整性元数据不能证明采购事实可用于当前范围。

此状态下：

1. 页面固定显示“**供应链数据同步中**”；
2. 不展示采购金额、供应商排名、品牌关系、协同指标或供应链业务风险；
3. 不以 Supplier Master 数量冒充活跃供应商数量；
4. 不以库存、销售、客户或旧缓存推测采购行为；
5. AI 不生成结论或建议；
6. 保留安全的来源状态、更新时间、请求 ID 和重新加载入口。

### 8.2 局部字段缺失

- 金额缺失：数量与单量仍可展示，所有金额及金额派生指标为 `null`；
- 预计/实际到货日期缺失：不计算准时率和交付类风险；
- 收货数量缺失：不计算到货率、未交数量及相关风险；
- 品牌关系缺失：记录进入 `unmatched_brand_lines`，不根据 SKU 文本猜品牌；
- 库存成本不可信：库存数量可展示，库存金额显示“成本数据治理中”；
- 来源时间不一致：分别展示每个来源的 `updated_at`，不得伪造统一更新时间。

### 8.3 零值、空值与无数据

真实的 `0` 保留为零；未知值使用 `null`；来源完整但周期内无记录使用空数组并显示“当前范围暂无供应链数据”。三者不得相互替换。

## 9. 数据隔离与 Three Portal 安全设计

### 9.1 客户数据禁止推供应商

以下规则是 V1.9 的不可放宽边界：

- 客户数据不得作为供应链 API 输入，不参与供应商表现、品牌供应关系、采购协同、风险或 AI 建议计算；
- 不得把客户订单、客户偏好、客户分层、Customer360、客户机会、客户联系方式或可识别客户的聚合结果推送、展示或传递给供应商；
- 供应商响应使用显式字段白名单；任何客户字段在服务端序列化前即拒绝/移除，并记录合同违规；
- AI 上下文构建器只接受 `domain = supply_chain` 的白名单字段，不得串接客户分析会话或客户缓存；
- 日志、导出、缓存和错误响应同样执行客户字段禁止规则；
- 即使客户数据可能解释销售需求，也不能借此推导供应商建议。跨域分析只有在未来获得单独的数据治理、用途、权限、最小化与输出合同批准后才能设计，V1.9 不预留隐式通道。

### 9.2 Portal 隔离

- Huyan CEO Portal 的 `ALL_DATA` 响应不得被供应商 Portal、客户 Portal或普通员工会话复用；
- URL、前端菜单可见性和客户端隐藏不是授权控制，服务端每次请求都必须鉴权；
- 若未来供应商需要查看自身采购协同信息，只能由独立 API 按认证供应商主体过滤，且不得包含其他供应商、客户或企业内部全局指标；
- V1.9 不设计任何供应商外发、下载共享或消息推送能力。

## 10. 验收设计

### 10.1 数据与口径验收

- 三个来源均可追溯，且页面/API 能分别展示其状态与更新时间；
- 聚合只使用稳定 ID 精确关联，未关联记录进入治理计数；
- 单量、数量、金额、到货率、准时率和未交数量符合第 5 节口径；
- 多供应商 SKU 不造成库存重复归属；
- `0`、`null`、空集合和同步中状态可区分；
- 不存在评分权重、风险阈值、供应商等级或采购金额的猜测。

### 10.2 API 与权限验收

- 合法 Huyan `VAFOX_CEO + ALL_DATA` 请求可读取单一只读合同；
- 未认证、错误 Portal、错误角色、非 `ALL_DATA` 分别返回 `401/403`；
- 前端伪造角色、范围或 Portal 参数不能提升权限；
- 非 GET 方法不能产生写入；SAP B1、SAP Mirror、Data Core、Auth、AI Runtime 均无变更；
- 上游不可用时不读取本地快照、不返回静态经营数据；
- 审计记录包含请求与结果元数据，但不包含客户数据或敏感采购全文。

### 10.3 缺失、隔离与 AI 验收

- 采购不足的所有路径均显示“供应链数据同步中”，六模块不产生猜测输出；
- 金额、交期、收货、品牌、库存字段的局部缺失按第 8.2 节单独降级；
- 在输入中注入客户字段时，字段不能进入供应商响应、缓存、日志或 AI 上下文；
- 供应链响应不能被其他 Portal 的身份读取；
- 每条 AI 输出均严格包含“结论 / 依据 / 建议”，依据可追溯且无客户字段；无依据时 AI 输出为空；
- 全量静态与运行时检查确认不存在 mock、fixture、faker、硬编码业务数字或猜测数据回退。

## 11. 实施前置条件与交付顺序

### 11.1 必须先确认

1. Data Core 负责人确认三个真实只读数据产品、逻辑字段映射、枚举、金额/币种/退货口径、更新时间和完整性语义；
2. 供应链业务负责人确认采购有效状态、收货口径、交付日期含义及风险事实规则；
3. 安全负责人确认现有 Auth/Gateway 能在**不修改 Auth**的前提下为新路由提供 `huyan.vafox.com + VAFOX_CEO + ALL_DATA` 的可信上下文；
4. 数据治理负责人确认 Supplier Master、SKU、品牌与库存的稳定关联键以及未关联治理流程；
5. AI 负责人确认现有 AI Runtime 可在**不修改 Runtime**的前提下接收白名单聚合上下文并按固定结构返回结果；否则 V1.9 首发关闭 AI 输出，不以替代实现绕过。

### 11.2 建议实施顺序（后续任务，不属于本次交付）

1. 冻结来源字段、完整性和权限合同；
2. 在 Business Application Layer 实现只读聚合、白名单与审计；
3. 完成有效、空、同步中、局部缺失、401、403、503、超时和隔离合同测试；
4. 接入供应链页面六模块及响应式状态；
5. 在无 AI 的事实模块通过验收后，再接入固定格式 AI 建议；
6. 完成安全、业务口径、数据治理及 CEO Portal UAT 后发布。

## 12. 最终范围确认

本报告只交付 V1.9 供应链分析设计，不开发代码。设计完整覆盖指定六个模块，明确 Supplier Master、采购数据、库存关联数据三个来源，定义 API 输入、输出字段和权限，固定采购不足时的“供应链数据同步中”状态，建立客户数据不得推供应商的强隔离边界，并将 AI 输出限定为“结论 / 依据 / 建议”。任何尚未由真实合同证明的数据均不展示、不推断、不模拟。
