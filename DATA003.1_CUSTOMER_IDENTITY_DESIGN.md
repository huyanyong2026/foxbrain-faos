# DATA-003.1：Customer Identity Foundation 设计

**状态：** Design Phase / 仅设计，不部署  
**上游设计：** `DATA003_ARCHITECTURE_DESIGN.md`（DATA-003）  
**服务对象：** Customer Growth Brain、受授权的员工助手和管理分析界面  
**设计原则：** SAP 是业务事实源，Core 是企业事实中心；本设计建立受治理的客户身份、画像和关系投影，不创建替代性客户主数据源，也不产生业务写入。

---

## 1. Customer Master 数据模型

### 1.1 统一 Customer ID

`customer_id` 是 Core 签发的、不可变、不可重用、租户/组织隔离的 opaque UUID（例如 `cst_01J...`）。它不是手机号、微信号、会员号、订单号或任一来源系统主键。普通 API 和分析数据集仅使用 `customer_id`；原始身份标识只保存在受限 Identity Vault 中，并以加密引用或版本化 HMAC token 参与匹配。

每一个 Customer Master 只表示一个经过证据支持的自然人客户。企业采购客户若需建模，应以独立的组织主体和授权联系人关系处理，不能因同一企业微信而自动合并多个自然人。

### 1.2 `customer_master` schema

| 字段 | 类型 | 必填 | 说明与约束 |
| --- | --- | --- | --- |
| `customer_id` | UUID/string | 是 | Core 生成；不可变；不含业务含义。 |
| `name` | string（受限 PII） | 否 | 展示名/法定姓名，按角色脱敏；保留来源与可信度。 |
| `mobile` | string（受限 PII） | 否 | E.164 规范化后的受保护值；标准响应仅返回掩码；唯一性由有效、已验证的 token 在组织范围内约束。 |
| `wechat_id` | string（受限 PII） | 否 | 个人微信的受保护值/令牌引用，不作为单独的全局唯一依据。 |
| `enterprise_wechat_id` | string（受限 PII） | 否 | 企业微信外部联系人标识；必须连同 `organization_id`/企业微信租户解释。 |
| `member_id` | string（受限业务标识） | 否 | 会员体系编号及来源；可有多个历史关联，主表展示当前有效值。 |
| `source_channel` | enum | 是 | 首次/当前归因来源，如 `store`、`wechat`、`enterprise_wechat`、`member`、`ecommerce`、`order`、`service`。 |
| `advisor_id` | string | 否 | 当前主负责顾问的引用；完整多对多历史存于 `employee_customer_relationship`。 |
| `organization_id` | string | 是 | 数据隔离、授权和解析边界；不得跨组织自动合并。 |
| `status` | enum | 是 | `active`、`inactive`、`prospect`、`merged`、`restricted`、`deleted`；`merged` 仅用于退休 ID。 |
| `consent_status` | enum | 是 | 有效授权摘要：`granted`、`partial`、`denied`、`withdrawn`、`unknown`；详细目的授权在 `customer_consent`。 |
| `created_at` | timestamp (UTC) | 是 | Customer ID 创建时间，RFC 3339。 |
| `updated_at` | timestamp (UTC) | 是 | 可见投影的最后更新时间；不可替代审计事件时间。 |

**实现性约束（设计约束而非部署任务）：**

- `organization_id + customer_id` 是所有读取、匹配和审计查询的强制过滤条件。跨组织关联只能经数据保护负责人批准的、显式的受控流程完成。
- `mobile`、`wechat_id`、`enterprise_wechat_id`、`member_id` 的原始值不进入应用日志、推荐载荷或通用分析事件。主表可存密文/受限引用；匹配表存 token 与证据引用。
- `advisor_id` 是便利投影，不能覆盖关系历史；`consent_status` 是便利摘要，不能覆盖逐目的、可追溯的授权事件。
- 任何来源值均记录 `source_system`、`source_record_ref`、`observed_at`、`verification_state`、`lineage_ref` 和 `quality_state`，以支持可解释性与回放。

### 1.3 支撑实体

| 实体 | 关键字段 | 用途 |
| --- | --- | --- |
| `customer_identity_link` | `link_id`、`customer_id`、`identity_type`、`token_ref`、`source_system`、`source_record_ref`、`match_state`、`verification_ref`、`valid_from/to` | 记录每一个来源身份与 Customer ID 的证据化、可失效连接。 |
| `customer_merge_event` | `merge_id`、`survivor_customer_id`、`retired_customer_id`、`reason_code`、`decision_by`、`decision_at`、`evidence_refs` | 只追加的合并/撤销合并审计记录。 |
| `customer_consent` | `consent_id`、`customer_id`、`purpose`、`state`、`basis`、`evidence_ref`、`captured_at`、`expires_at`、`withdrawn_at` | 逐目的授权事实及其有效状态。 |
| `identity_review_case` | `case_id`、`candidate_ids`、`risk_reason`、`evidence_refs`、`state`、`reviewer_id`、`decision_at` | 人工审核队列与四眼复核证据。 |

---

## 2. Identity Resolution 设计

### 2.1 输入与标准化

解析服务接受微信、手机号、企业微信、会员、订单五类来源事实，并只在同一 `organization_id` 内工作。输入先经来源适配器进行格式验证、规范化、加密/令牌化，再进入候选查找；原始值不出现在普通服务日志中。

| 身份信号 | 规范化与候选键 | 可信使用方式 |
| --- | --- | --- |
| 手机号 | 解析为 E.164、去除格式字符、校验国家/地区码，然后生成版本化 HMAC token。 | 最高优先级的确定性个人标识，但仅限有效、已验证且未冲突的号码。 |
| 微信 | 保留来源类型和受保护 token；不以昵称、头像或模糊文本作确定性匹配。 | 与已验证手机号、会员或人工证据组合时提升置信度。 |
| 企业微信 | 以企业微信租户 + 外部联系人 token 为键。 | 仅说明某组织中的外部联系关系；不能跨企业微信租户推断同一人。 |
| 会员 | 会员系统 + 会员编号 token；校验卡状态、绑定证据和来源权威性。 | 可确定连接来源会员记录，不自动覆盖冲突手机号。 |
| 订单 | 订单来源 + 客户引用 + 支付/收货等经批准的受限证据引用。 | 订单是关系证据，不是独立的个人唯一标识；共享手机号/代购订单必须降级为候选。 |

### 2.2 决策流程与手机号优先规则

```text
接收来源身份 → 组织边界、格式、来源质量校验 → token 精确候选查找
                                                ↓
          已验证手机号的单一候选？ ─是→ 连接到该 customer_id，记录证据
                     ↓ 否
     其他已验证标识是否一致地指向一个客户？ ─是→ 建立已验证连接
                     ↓ 否
  存在冲突/多个候选/弱证据？ ─是→ 保留 probable 连接并创建审核案件
                     ↓ 否
                 创建最小化 prospect Customer ID（不擅自合并）
```

1. **手机号优先：** 同一组织内，已验证、有效且未标注共享/冲突的手机号精确 token 命中一个 `active` Customer ID 时，解析结果为该 ID；新微信、企业微信、会员或订单连接以来源和验证证据附加到该 ID。
2. **手机号冲突：** 一个手机号命中多个活跃 Customer ID，或来源声明与既有已验证手机号相矛盾时，禁止自动合并、禁止改写主号码；结果为 `probable`/`conflict`，进入人工审核。
3. **无手机号：** 微信、企业微信、会员和订单仅在多个独立、经批准的证据均指向同一候选且无冲突时，才可生成 `verified` 连接。单一微信、会员或订单信号默认只建立 `probable` 关系或创建最小 `prospect`。
4. **不允许的捷径：** 姓名、昵称、城市、年龄、顾问、设备、共同订单地址或模型相似度不能单独触发自动合并；它们至多作为审核辅助证据。
5. **来源权威性：** 来源系统仍拥有其原始记录。解析服务只维护链接、证据和投影，绝不回写 SAP、Core 生产同步或来源客户记录。

### 2.3 重复客户识别与人工审核

重复识别输出候选对及理由码，例如 `same_verified_mobile`、`member_to_phone_conflict`、`shared_contact_suspected`、`order_only_overlap`、`source_key_reused`。系统将候选分为：

| 结果 | 自动处理 | 人工处理 |
| --- | --- | --- |
| `verified` | 仅在上述确定性规则满足时创建身份连接，不改变来源记录。 | 例外抽检与可追溯纠错。 |
| `probable` | 保留候选和分数，不合并画像、同意或关系。 | 审核员核验受限证据后决定链接、拒绝或继续观察。 |
| `conflict` | 停止自动链接和个性化扩展；仅返回最小必要上下文。 | 指派隐私/数据管理员；涉及敏感同意或高风险合并时要求双人复核。 |
| `rejected` | 保留拒绝理由和证据版本，阻止同规则重复合并。 | 可基于新证据重新开启案件。 |

审核案件必须显示候选 Customer ID、脱敏标识、来源、证据、风险标签和建议，不展示不必要的完整 PII。审核决定必须记录审核人、时间、原因码、证据引用、前后状态和关联 `correlation_id`。模型可排序但不能自行将 `probable` 提升为 `verified`。

### 2.4 历史关系保留

合并采用 **survivor + redirect**：选定保留 `survivor_customer_id`，退休 ID 标为 `merged` 并写入 `merged_into`；旧 ID 在受授权读请求中可解析到保留 ID，同时返回重定向/审计元数据。所有原始 `customer_identity_link`、同意事件、订单/互动来源引用、顾问关系、画像版本均保留原始 `customer_id` 与有效时间，禁止物理覆盖或删除历史。

撤销合并只能由人工审核流程发起。撤销生成新的事件和有效时间区间，恢复各链接/关系的历史归属；已产生的访问审计、推荐和活动记录不得被静默改写。

---

## 3. Customer Profile 模型

`customer_profile` 是用于 Customer Growth Brain 的最小化、可解释的派生画像，不是身份决策的主键来源。每个属性都有来源、更新时间、质量、置信度、可使用目的和有效期；未获相应授权时，服务省略或聚合属性。

| 字段 | 类型/示例 | 形成规则 |
| --- | --- | --- |
| `customer_id` | UUID | 外键；组织边界必传。 |
| `city` | string / `深圳` | 经授权的地址、门店互动或客户声明的最新可信城市；不得将订单地址无条件认定为常住地。 |
| `age_band` | enum / `18_24`、`25_34`、`35_44`、`45_plus`、`unknown` | 仅返回年龄段，不返回生日；由经授权、可验证年龄推导。 |
| `outdoor_level` | enum / `newcomer`、`casual`、`regular`、`advanced`、`unknown` | 基于经授权的活动/装备/购买特征的版本化规则；附置信度。 |
| `interest_tags` | string[] | 如 `trail_running`、`hiking`、`camping`；客户声明、已授权互动或行为聚合产生，并注明来源。 |
| `brand_preferences` | object[] | `{brand, affinity_level, evidence_window_days}`；只使用允许目的内的聚合购买/互动事实。 |
| `spend_band` | enum | `unknown`、`low`、`medium`、`high`、`premium`；区间阈值版本化，不输出精确消费额。 |
| `activity_preferences` | object[] | 活动类型、强度/时段偏好、置信度；须遵循活动通知/个性化授权。 |
| `profile_version` | string | 特征和规则版本，支持回放。 |
| `as_of` / `expires_at` | timestamp | 画像快照时间和失效时间。 |

画像生成必须区分 **客户明确声明**、**来源事实** 与 **派生推断**，并向受权调用者提供对应的 `lineage_refs`。`unknown` 是合法值，禁止以缺失数据猜测敏感个人特征。撤回个性化/分析授权后，停止为相关目的生成或返回该画像，并按保留策略使相关派生数据失效。

---

## 4. Equipment Profile 模型

装备档案支持售后理解和经授权的成长建议；它不是库存、订单或产品主数据的权威来源。产品、品牌、类目和购买事实保留对 Core 受治理事实的只读引用。

| 字段 | 类型 | 规则 |
| --- | --- | --- |
| `equipment_profile_id` | UUID | 档案记录主键。 |
| `customer_id` | UUID | 必填；按客户授权和组织范围读取。 |
| `product_id` | string | 必填；指向 Core 产品事实，不复制或修改 SAP 产品主数据。 |
| `brand` | string | 产品事实快照/引用中的品牌。 |
| `category` | string | 产品事实快照/引用中的标准类目。 |
| `purchase_date` | date/null | 经授权的订单/会员购买事实日期；未知时为 `null`。 |
| `usage_scene` | string[] | 如 `urban_commute`、`day_hike`、`multi_day_trek`；客户声明优先，推断值必须标识。 |
| `equipment_level` | enum | `entry`、`standard`、`technical`、`professional`、`unknown`；规则版本化。 |
| `upgrade_opportunity` | object/null | `{state, reason_codes, confidence, evidence_refs, requires_human_review}`；仅建议，不生成报价、订单或销售动作。 |
| `source_refs` | string[] | 购买/保修/客户声明的血缘引用。 |
| `as_of` | timestamp | 档案快照时间。 |

共享购买、赠品、退货、换货、二手转移或来源质量不足时，装备与客户仅保留带状态的关系，不能把商品所有权或使用情况当作确定事实。`upgrade_opportunity` 仅在授权的个性化目的下计算；无授权时 API 可以返回通用产品知识，不返回针对个人的升级建议。

---

## 5. Employee Relationship 模型

客户与员工顾问是可变、多对多、带时间范围的关系；`customer_master.advisor_id` 仅投影当前主关系。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `relationship_id` | UUID | 关系记录标识。 |
| `advisor_id` | string | 员工目录的顾问引用；权限从员工身份和组织/门店范围实时取得。 |
| `customer_id` | UUID | 客户引用。 |
| `relationship_role` | enum | `primary_advisor`、`support_advisor`、`service_owner`、`former_advisor`。 |
| `interaction_history` | reference[] | 脱敏互动事件引用、时间、渠道、结果码；不在关系表复制完整对话或 PII。 |
| `sales_history` | reference[] | 经授权的订单/销售聚合引用；不作为自动归因或自动佣金结算依据。 |
| `follow_up_status` | enum | `none`、`suggested`、`pending_human_review`、`in_progress`、`completed`、`suppressed`；仅表示人工工作状态。 |
| `assigned_at` / `ended_at` | timestamp | 有效时间边界，保留交接历史。 |
| `source_ref` / `audit_ref` | string | 来源、交接和访问/修改审计引用。 |

顾问只能在其被授予的组织、门店和客户关系范围内读取必要信息。关系变更、交接和主顾问调整必须通过受治理的人工作流记录，且不会自动向客户发送消息、创建订单或执行任何销售动作。

---

## 6. Consent 与 ACL 权限设计

### 6.1 客户授权管理

授权按 **客户 + 组织 + 目的** 管理，而不是以单一勾选代替。最小目的集为 `service`、`analytics`、`personalization`、`marketing`；每次授权事件保存法律/业务依据、采集渠道、展示文本版本、证据引用、采集人/系统、时间、有效期和撤回时间。

| 授权状态 | 访问行为 |
| --- | --- |
| `granted` | 仅允许该目的、最小字段集和授权范围内的处理。 |
| `partial` | 仅按已同意目的与字段类别返回。 |
| `denied` / `withdrawn` | 拒绝新的营销与个性化读取/计算；服务所必需的最小处理须有独立合法依据与政策标记。 |
| `unknown` | 对营销、画像和个性化默认拒绝；不得把未选择当作同意。 |

撤回必须立即影响后续 API 决策、推荐和活动建议。下游删除、匿名化和法定保留由独立保留策略执行并留审计；不得以“历史数据”绕开撤回后的新用途限制。

### 6.2 ACL：RBAC + ABAC

所有请求需要已认证主体、`organization_id`、声明用途 `X-Purpose`、相关 `customer_id`/资源范围和 `X-Correlation-Id`。策略引擎在字段返回前执行：组织行过滤 → 角色权限 → 顾问/门店/客户关系属性 → 用途与同意 → 字段掩码 → 审计。默认拒绝。

| 角色 | 可访问范围 | 关键限制 |
| --- | --- | --- |
| 一线顾问 | 所属组织、获分配/明确授权的客户及门店范围。 | 默认脱敏身份字段；仅服务用途；无批量导出、无跨组织查询。 |
| 门店经理 | 所属门店授权客户的聚合及必要服务上下文。 | 不可查看其他门店的逐客户 PII；营销须另行授权。 |
| 客户运营/增长专员 | 被授予组织内、具备相应同意的分群与画像。 | 原始身份标识默认不可见；导出、批量操作受审批和水印审计。 |
| 隐私/身份审核员 | 为审核案件读取最小必要的受限身份证据。 | 不能借审核角色执行营销或销售操作；高风险合并双人复核。 |
| 管理层 | 所属组织/法人的聚合经营指标和去标识化分群。 | 默认无逐客户 PII、无原始互动内容；个案访问须明确业务理由和授权。 |
| 平台管理员 | 运行与策略配置所需元数据。 | 无默认业务 PII 读取权；break-glass 必须限时、审批和全量审计。 |

组织隔离由 `organization_id` 强制执行于令牌声明、查询谓词、缓存键、导出任务和审计检索中。管理层权限是“更广的聚合观察”而非“无限制客户查看”；任何越权、用途不匹配、授权失效或缺少关系范围的请求返回 `403 POLICY_DENIED`，且不泄露客户存在性。

### 6.3 审计与数据最小化

不可变 `access_audit` 至少记录主体、委托主体（如 AI 助手）、角色、组织/门店范围、目的、资源/字段类别、策略结果、脱敏状态、关联 ID、时间和血缘引用。审计日志不得记录原始手机号、微信号、完整 API 响应、自由文本互动内容或密钥/token。

---

## 7. API Contract 设计

**基础路径：** `/api/customer`  
**方法：** 以下接口均为只读 `GET`；所有时间戳为 UTC RFC 3339，响应为 `application/json`。  
**共同请求头：** `Authorization`、`X-Correlation-Id`、`X-Purpose`、`X-Organization-Id`；代表用户的服务还必须带短时有效的委托主体信息。  
**共同原则：** API 以 `customer_id` 查找，不能接受原始手机号/微信号作为读取替代；身份解析属于独立、受限的内部契约。所有响应都包含 `policy`、`freshness` 和 `lineage`，且默认脱敏。

| Endpoint | 必需权限与用途 | 返回内容 | 主要控制 |
| --- | --- | --- | --- |
| `GET /api/customer/{id}` | `customers:read`；`service` 或获批用途 | Customer Master 的授权字段、状态、授权摘要。 | `name`/`mobile`/微信/会员标识默认掩码；不返回 Identity Vault token。 |
| `GET /api/customer/{id}/profile` | `customers:profile:read`；画像/个性化须对应同意 | 城市、年龄段、户外等级、兴趣、品牌、消费、活动偏好及质量。 | 对未经授权或不可用字段省略；返回属性来源与版本。 |
| `GET /api/customer/{id}/equipment` | `customers:equipment:read`；服务或获批个性化用途 | 装备记录、来源引用和受控升级机会。 | 不返回原始订单明细；无个性化同意时抑制个人升级机会。 |
| `GET /api/customer/{id}/context` | `customers:context:read`；`service`/获批 `personalization` | 面向员工的最小综合上下文：安全展示信息、当前顾问关系、画像摘要、装备摘要、同意/限制和新鲜度。 | 不聚合被拒字段；明确 `advisory_only`，无写入或行动指令。 |

### 7.1 统一响应与错误语义

```json
{
  "customer_id": "cst_01J...",
  "organization_id": "org_...",
  "data": {},
  "consent": {"service": "granted", "personalization": "withdrawn"},
  "policy": {"decision": "allow", "masked_fields": ["mobile", "wechat_id"]},
  "freshness": {"as_of": "2026-07-21T00:00:00Z", "quality_state": "certified"},
  "lineage": [{"source": "core", "ref": "lin_..."}],
  "correlation_id": "corr_..."
}
```

标准错误载荷为：

```json
{"error":{"code":"POLICY_DENIED","message":"Access is not permitted for the declared purpose.","correlation_id":"corr_...","retryable":false}}
```

错误码包括 `400 INVALID_REQUEST`、`401 UNAUTHENTICATED`、`403 POLICY_DENIED`、`404 CUSTOMER_NOT_FOUND`（仅在可安全披露不存在时使用）、`409 IDENTITY_REDIRECT`（退休 ID，含受权重定向信息）、`422 CONSENT_REQUIRED` 和 `409/503 CONTEXT_STALE`。接口不提供 `POST`、`PUT`、`PATCH`、`DELETE`，也不提供批量 PII 导出。

---

## 8. 系统边界与明确禁止项

DATA-003.1 是 Customer Growth Brain 的受治理读取基础。它可以解析身份链接、计算受授权画像、返回事实/建议上下文、记录访问审计和产生人工审核案件；它不拥有来源客户、产品、订单或销售真相。

**明确禁止：**

- 修改 SAP，包括 SAP 客户、订单、库存、价格、产品或业务逻辑；
- 修改 Core 生产同步，包括同步规则、生产连接器或来源事实写入；
- 自动执行销售动作，包括自动发微信/短信、创建线索/订单/报价、分配任务、变更会员或客户资料；
- 未授权客户数据访问，包括跨组织读取、绕开同意、以管理层身份读取逐客户 PII、将原始身份标识写入日志或交给未获授权的 AI；
- 使用模糊相似度、共同设备/订单或模型分数静默合并客户；
- 将本设计中的 `upgrade_opportunity`、`follow_up_status` 或 API 上下文解释为销售指令。

未来任何来源写回、自动触达或生产同步变更均需要独立设计、安全/隐私评审、来源系统所有者批准、人工审批工作流与可审计上线方案；不属于 DATA-003.1。

---

## 9. 验收标准

| 验收项 | 完成定义 |
| --- | --- |
| ☑ Customer Master Schema | 已定义统一、不可变 `customer_id`、所需字段、组织边界、受限标识和支撑身份连接实体。 |
| ☑ Identity Resolution | 已定义微信、手机号、企业微信、会员、订单的规范化、手机号优先、冲突处理、重复检测、人工审核及历史保留规则。 |
| ☑ Customer Profile | 已定义城市、年龄段、户外等级、兴趣标签、品牌偏好、消费区间、活动偏好及来源/同意控制。 |
| ☑ Equipment Profile | 已定义 `customer_id`、`product_id`、品牌、类目、购买日期、使用场景、装备等级、升级机会和只读边界。 |
| ☑ Employee Relationship | 已定义顾问—客户多对多关系、互动/销售引用、跟进状态、有效时间与人工交接要求。 |
| ☑ Consent Management | 已定义逐目的授权、撤回即时生效、未知默认拒绝、证据和保留边界。 |
| ☑ ACL Permission | 已定义 RBAC + ABAC、员工范围、组织隔离、管理层聚合查看、字段脱敏和审计。 |
| ☑ API Contract | 已定义四个指定 GET Customer API、请求上下文、响应包络、错误语义和只读限制。 |
| ☑ SAP/Core Boundary | 已明确 SAP、Core 生产同步、自动销售动作和未授权访问均不在允许范围。 |

**设计完成判定：** 本文档完成 DATA-003.1 的设计交付；未包含数据库迁移、服务部署、连接器变更、生产数据回填或任何运营执行动作。
