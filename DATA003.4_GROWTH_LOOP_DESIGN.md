# DATA-003.4：VAFOX Growth Loop Design

**状态：** Design Phase / 仅设计，不部署
**前置设计：** `DATA003.1_CUSTOMER_IDENTITY_DESIGN.md`、`DATA003.2_RECOMMENDATION_ENGINE_DESIGN.md`、`DATA003.3_EMPLOYEE_AI_ASSISTANT_DESIGN.md`
**目标：** 在不改变 SAP、Core 生产同步或来源业务事实的前提下，建立可审计、可审核、以客户授权为前提的 VAFOX 客户户外成长与裂变闭环。

---

## 1. 设计原则与范围

1. **事实源不迁移。** SAP 是业务事实源；Core 是受治理的企业事实中心。Growth Loop 只读取经认证的购买、活动和内容事实，并维护自己的派生投影、审核记录与反馈事件。
2. **客户身份与授权优先。** 所有记录使用 DATA-003.1 的 `customer_id` 和 `organization_id`；原始手机号、微信号、媒体文件原始地址不得进入通用日志、积分事件或分享载荷。缺少所需用途授权时，拒绝或匿名化处理。
3. **人审优先。** 积分、等级、裂变归因和内容奖励均由规则计算出“待审核建议”；只有授权人员审核后才成为已入账事实。规则引擎不得直接发送营销消息、发券、改会员权益或创建订单。
4. **可解释、可回放。** 每项派生结果必须保留规则版本、输入事实引用、政策判定、审核决定、时间及 `correlation_id`。更正使用冲正/新版本事件，禁止静默覆盖历史。
5. **最小化与默认拒绝。** 所有接口强制认证、RBAC + ABAC、组织行过滤、用途检查、字段脱敏和不可变访问审计；无权限请求不得暴露客户是否存在。

**明确不在范围内：** 部署、自动营销发送、自动奖励发放无审核、修改 SAP、修改 Core 生产同步、操作库存/价格/订单、未授权访问或导出客户数据。

---

## 2. Growth Loop Architecture

```text
Customer
   ↓（经授权、受治理的购买事实）
Purchase
   ↓（活动报名/签到/完成等事实）
Activity
   ↓（客户主动提交、平台连接或审核导入）
Content
   ↓（规则计算 → 审核 → 已入账/冲正）
Points
   ↓（客户主动分享带归因链接；不自动触达）
Referral
   ↓（注册、到店、购买的受治理事实匹配）
New Customer
   └──────────────────────→ Customer（形成下一轮成长闭环）
```

| 环节 | 输入 | 产生的受治理记录 | 人工/政策闸门 |
| --- | --- | --- | --- |
| Purchase | Core 的只读订单/商品事实引用 | `growth_purchase_signal`、装备候选 | 退货、赠品、共享购买或来源质量不足时不自动计分。 |
| Activity | 报名、签到、领队确认、完成状态 | `outdoor_journey`、`activity_participation` | 仅已授权且状态可信的活动可进入成长计算。 |
| Content | 照片、视频、路线及平台互动摘要 | `content_record`、内容审核案件 | 隐私、肖像、版权、安全和虚假互动审核。 |
| Points | 已审核的合格行为事实 | `points_ledger`、余额投影 | 规则引擎仅提出入账建议；审批后写入不可变账本。 |
| Referral | 分享码、受邀人明确归因与阶段事实 | `referral_case`、奖励建议 | 防自邀、重复、作弊、撤销/退款及同意检查。 |
| New Customer | 经 DATA-003.1 解析的最小客户身份 | 新 Customer ID 或已有 ID 的受控关联 | 绝不以裂变线索自动合并身份或替代身份审核。 |

**反馈闭环：** 审核员和运营人员对每个“接受、修改、拒绝、冲正、争议”的决定附原因码。系统按规则版本分析通过率、争议率、退款/作弊率、内容质量、邀请阶段转化和活动完成率；分析只产生规则优化建议，经业务、隐私/安全和数据负责人审批后才可发布新规则版本。

---

## 3. Outdoor Journey Model

`outdoor_journey` 用于记录客户户外成长轨迹；它是客户声明与经审核活动事实的投影，不是定位、医疗或安全事故的权威系统。位置与媒体属于敏感上下文，应按最小精度、最短必要保留期和用途授权处理。

| 字段 | 类型 | 必填 | 定义与控制 |
| --- | --- | --- | --- |
| `journey_id` | UUID/string | 是 | 不可变轨迹记录 ID。 |
| `customer_id` | UUID/string | 是 | DATA-003.1 的受控客户引用。 |
| `activity_id` | UUID/string | 是 | 活动引擎活动引用；非官方行程可使用审核后的自建活动 ID。 |
| `location` | object | 否 | `{display_area, geohash_precision, source, visibility}`；默认仅城市/景区级，精确坐标不得在公开分享或普通响应中返回。 |
| `route` | object | 否 | `{route_id, name, distance_km, elevation_gain_m, safety_status, source_ref}`；路线文件受限存储，须通过安全审核。 |
| `difficulty` | enum | 否 | `easy`、`moderate`、`hard`、`expert`、`unknown`；以领队/路线标准为准，客户自报须标识。 |
| `equipment_used` | object[] | 否 | `{product_id, category, ownership_state, source_ref}`；仅引用 Core 产品事实，不主张所有权或改写订单。 |
| `photos` | media_ref[] | 否 | `{media_id, storage_ref, consent_state, moderation_state}`；不在 API 返回原文件地址。 |
| `videos` | media_ref[] | 否 | 同照片；视频封面、人物和音频需要独立隐私/版权检查。 |
| `achievement` | object[] | 否 | `{achievement_code, state, issued_by, evidence_refs, rule_version}`；可为“完成首条路线”等，`state` 为 `proposed/approved/revoked`。 |
| `occurred_at` / `recorded_at` | UTC timestamp | 是 | 区分活动发生时间与系统记录时间。 |
| `verification_state` | enum | 是 | `customer_reported`、`organizer_verified`、`reviewed`、`rejected`。 |
| `lineage_refs` | string[] | 是 | 活动、媒体、产品及审核输入的血缘引用。 |

**轨迹写入状态：** `draft → submitted → safety_or_privacy_review → verified → published_or_private`，可进入 `rejected`、`withdrawn` 或 `expired`。客户可撤回公开内容；撤回后停止新用途计算并使公开投影失效，已审计的事实按保留政策保存。

---

## 4. Points System

### 4.1 账本与来源

积分采用不可变双向事件账本 `points_ledger`，余额是可重建投影，不是可被客户端直接修改的字段。每项建议先写入 `pending_review`，审核通过后才记为 `posted`；撤销、退款、作弊或纠错以 `reversal` 反向事件处理。

| 字段 | 说明 |
| --- | --- |
| `ledger_entry_id`、`customer_id`、`organization_id` | 唯一账本事件和强制组织隔离键。 |
| `event_type`、`points_delta`、`state` | 来源/用途事件、正负积分与 `pending_review/posted/rejected/reversed/expired` 状态。 |
| `source_ref`、`rule_version`、`eligibility_snapshot` | 可回放的事实引用、规则和授权/去重判定。 |
| `reviewer_id`、`reviewed_at`、`decision_reason` | 审核责任；无审核人不可成为 `posted`。 |
| `expires_at`、`correlation_id`、`audit_ref` | 过期、链路追踪和不可变审计。 |

| 积分来源 | 合格事实 | 典型防护 |
| --- | --- | --- |
| 购买装备 | 已结算且过退换窗口的 Core 购买事实引用 | 排除取消、退款、赠品、代购/共享归属不明和重复订单。 |
| 参加活动 | 报名后签到且领队/主办方确认完成 | 仅报名、重复签到或活动取消不计分。 |
| 上传照片 | 与合格活动关联、通过内容审核的原创照片 | 哈希去重、肖像/版权/安全审查和每日上限。 |
| 上传视频 | 与合格活动关联、通过审核的视频 | 同照片，并限制时长/重复剪辑刷分。 |
| 分享路线 | 路线安全、版权与内容审核通过 | 不公开危险坐标；相同路线版本去重。 |
| 装备评价 | 已验证购买/使用关系下的有效评价 | 反垃圾、敏感词、利益冲突和重复评价检测。 |
| 邀请好友 | 受邀人完成定义的有效阶段 | 仅注册不发放最终奖励，见第 6 节。 |

### 4.2 积分用途

积分兑换创建 `redemption_request`，而不是直接变更外部系统：`requested → eligibility_review → approved → fulfillment_reference_recorded → completed`，可被 `rejected/cancelled/expired` 终止。所有权益库存、报名资格、会员状态及新品体验名额由各自权威系统决定。

| 积分用途 | 输出 | 必要检查 |
| --- | --- | --- |
| 商品权益 | 人工批准的权益/兑换申请草稿 | 余额、有效期、适用商品、资格、反欺诈；不创建订单。 |
| 活动报名 | 活动报名资格申请或候补建议 | 活动容量、风险要求、客户授权和主办方审核。 |
| 会员权益 | 权益资格建议 | 会员规则版本与人工/受权工作流确认；不直接改会员等级。 |
| 新品体验 | 新品体验候选资格 | 库存/样品、活动安全要求、目标人群及人工遴选。 |

积分余额响应应区分 `available_points`、`pending_points`、`reserved_points`、`expired_points`，并列出最近账本引用；不得仅凭客户端声称的余额兑换。

---

## 5. Outdoor Level 成长体系

等级是根据已审核的成长事实得到的**建议性**身份，不替代安全资质、领队执照或员工授权。等级重算由版本化规则进行，升级建议须审核；降级/撤销只可因经确认的资格失效、违规或事实冲正而发生，并保留原因与申诉入口。

| 等级 | 名称 | 升级规则（所有条件为已审核事实） | 权益规则（均为资格建议，需可用性与人工确认） |
| --- | --- | --- | --- |
| Lv1 | 户外新人 | 已完成账户与服务授权所需资料；或完成首个经验证户外活动。 | 新手安全知识、基础活动/装备内容和公开活动浏览资格。 |
| Lv2 | 徒步玩家 | Lv1 + 完成 ≥3 次活动或 ≥2 条不同路线；至少 1 条装备/内容有效贡献。 | 适配的徒步活动候选、装备使用课程与积分兑换优先级建议。 |
| Lv3 | 山野达人 | Lv2 + 完成 ≥8 次活动、≥4 条不同路线，且至少 2 次为 `moderate` 或以上；安全内容完成。 | 进阶路线内容、活动候补优先级建议和新品体验候选资格。 |
| Lv4 | 户外伙伴 | Lv3 + 完成 ≥15 次活动、持续 6 个月活跃，且经审核的路线分享/装备评价/内容贡献 ≥5 项。 | 社群共创、试用/活动共建候选与受邀客户同行活动资格建议。 |
| Lv5 | 火狐狸领队 | Lv4 + 完成 ≥25 次活动、≥10 条路线贡献，并由人工确认的领队能力/安全培训/组织授权。 | 领队活动候选、共创内容优先审核和领队专属权益建议；绝不自动授予带队权。 |

**共同规则：**

- 规则必须带 `level_rule_version`、生效时间、证据窗口和最低安全条件；“次数”按去重后的已完成活动计算。
- 购买金额、社交互动量或邀请人数不能单独升级，避免以消费或刷量替代户外经验与安全能力。
- 等级、权益和积分彼此关联但独立核算。权益可因名额、适用范围、授权、风险控制或政策变化被抑制，系统须返回解释码。
- 客户可查看自身等级依据摘要、申请纠错或撤回公开展示；员工只能在其组织和关系范围内查看最小必要摘要。

---

## 6. Referral Network

```text
老客户分享（自愿生成、可撤销的 referral_code/link）
        ↓
好友注册（明确归因 + 身份解析；不自动合并）
        ↓
好友到店（经授权的到店/签到事实）
        ↓
好友购买（已结算、过退换窗口的 Core 订单事实）
        ↓
积分奖励（规则建议 → 反作弊/审核 → 双方分别入账）
```

`referral_case` 至少包括 `referral_id`、`referrer_customer_id`、`invitee_customer_id`、`referral_code_id`、`registered_at`、`visited_at`、`qualified_purchase_ref`、`state`、`attribution_evidence`、`fraud_flags`、`reward_rule_version`、`review_ref` 和 `audit_ref`。状态为：`shared → registered → visited → purchased_qualified → reward_pending_review → rewarded`，或 `rejected/reversed/expired`。

**归因与反作弊：** 受邀人必须在注册/规定归因窗口内明确接受邀请或使用有效链接；同一受邀客户只保留一个经审核的归因。系统检查自邀、同一受限身份 token、同设备/支付/地址等高风险信号、批量异常、取消/退款、员工利益冲突和重复奖励。高风险只进入审核队列，不自动定罪；原始敏感信号不暴露给普通运营人员。邀请人和受邀人均须满足各自用途/活动授权，且不得因拒绝营销而失去已合法获得的服务性权益。

---

## 7. Content Sharing Model

内容连接至 **视频号、小红书、公众号、企业微信**。连接器仅在客户明确授权、平台许可及内容可见范围允许时读取或接收必要的发布/互动摘要；不抓取私密内容、不代客户自动发布、不自动私信或营销触达。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `content_id` | UUID/string | 内容记录唯一 ID。 |
| `customer_id` | UUID/string | 受控客户引用。 |
| `platform` | enum | `video_account`、`xiaohongshu`、`official_account`、`enterprise_wechat`。 |
| `activity` | object | `{activity_id, content_type, published_at, visibility, source_ref}`；关联活动和公开范围。 |
| `engagement` | object | `{views, likes, comments, shares, measured_at, quality_state}`；仅保存获准的聚合摘要，不将互动量视为事实性购买/兴趣。 |
| `reward` | object | `{proposed_points, state, rule_version, ledger_entry_ref}`；只能引用待审/已审积分账本。 |
| `moderation_state` | enum | `pending`、`approved`、`rejected`、`withdrawn`、`restricted`。 |

内容提交后执行格式/重复检测、版权/肖像/隐私检查、户外安全风险检查、平台条款及客户授权检查。发布链接只作为证据引用并按可见性保护；内容删除、平台授权撤回或审核失败时，停止新增奖励和公开展示，必要时发起待审冲正。

---

## 8. Activity Engine Integration

```text
活动（报名、签到、完成）
  ↓
装备推荐（DATA-003.2 的只读、可解释建议）
  ↓
购买（Core 经认证的事实引用）
  ↓
体验（Outdoor Journey + 已验证活动结果）
  ↓
分享（客户自愿内容/路线分享）
  ↓
积分（待审核建议 → 审核账本）
```

| 集成点 | 输入/输出 | 约束 |
| --- | --- | --- |
| 活动 → 推荐 | 活动类型、难度、路线和客户已授权装备摘要；输出装备建议及证据 | 仅建议，不保留库存、不发券、不下单；无个性化授权时仅给通用安全建议。 |
| 推荐 → 购买 | 可选的推荐引用与 Core 购买事实 | 购买是否发生由 Core 事实确认；不得把点击或推荐当成购买。 |
| 购买 → 体验 | 合格装备事实引用、活动完成与客户提交体验 | 装备归属不确定时仅记录候选；不得以购买金额决定安全等级。 |
| 体验 → 分享 | 经审核的轨迹/内容草稿 | 客户主动选择平台与可见性；精确位置和同行人信息默认不公开。 |
| 分享 → 积分 | 内容审核结论、去重和反作弊结果 | 积分只创建待审账本建议，审核通过后入账。 |

活动引擎保存 `activity_id`、状态转换、来源引用、规则版本、政策判定、人工反馈和结果引用。它不拥有客户/订单/库存主数据，也没有 SAP 或 Core 生产同步写入适配器。

---

## 9. Growth API Contract

**基础路径：** `/api/growth`；所有 JSON 时间为 UTC RFC 3339。
**共同请求头：** `Authorization`、`X-Organization-Id`、`X-Purpose`、`X-Correlation-Id`；代表客户/员工调用时另需短时有效委托主体。
**共同控制：** 认证后按组织过滤 → RBAC/ABAC → 客户关系与用途/同意 → 字段最小化/脱敏 → 审计。写入接口需要 `Idempotency-Key`，仅创建草稿/待审核记录，绝不产生自动奖励或外部业务写入。

| Endpoint | 权限与用途 | 请求核心 | 成功响应/状态 | 关键拒绝条件 |
| --- | --- | --- | --- | --- |
| `GET /api/growth/profile/{customer_id}` | `growth:profile:read`；`service` 或获批 `personalization` | 可选 `as_of` | 户外等级、积分摘要、经授权轨迹/内容/邀请摘要、`policy`、`freshness`、`lineage`；`200` | `403 POLICY_DENIED`、`404`（仅在已授权可知时）、`409 CONTEXT_STALE`。 |
| `POST /api/growth/activity` | `growth:activity:submit`；服务/活动目的 | `customer_id`、`activity_id`、路线/难度/装备/媒体引用、发生时间 | 创建 `outdoor_journey` 草稿或审核案件，`202 Accepted`，含 `review_state` 和 `journey_id` | 缺授权、越组织、无活动资格、危险路线/媒体审核失败、幂等冲突。 |
| `POST /api/growth/content` | `growth:content:submit`；内容处理授权 | `customer_id`、`platform`、`activity_id`、内容/互动摘要、可见性、证据引用 | 创建 `content_record` 与可选 `points` 建议，`202 Accepted`；奖励为 `pending_review` | 平台/肖像/版权授权不足、自动营销意图、重复/违规内容。 |
| `POST /api/growth/referral` | `growth:referral:submit`；客户自助/受权员工服务用途 | `referrer_customer_id`、`referral_code`、`event_type`、最小证据引用 | 创建或推进 `referral_case`，`202 Accepted`；绝不直接入账 | 自邀/重复/归因窗口失效、身份未解析、反作弊待审或用途不允许。 |

### 9.1 示例：读取成长档案

```json
{
  "customer_id": "cst_01J...",
  "outdoor_level": {"code": "lv2", "name": "徒步玩家", "rule_version": "growth-level-2026.07", "review_state": "approved"},
  "points": {"available_points": 180, "pending_points": 30, "reserved_points": 0, "last_ledger_refs": ["ple_..."]},
  "policy": {"decision": "allow", "masked_fields": ["exact_location", "media_storage_ref"]},
  "freshness": {"as_of": "2026-07-21T00:00:00Z", "quality_state": "certified"},
  "lineage": ["journey_...", "ple_..."],
  "disposition": "advisory_only"
}
```

### 9.2 统一错误语义与审计

```json
{
  "error": {
    "code": "REVIEW_REQUIRED",
    "message": "The submitted growth event is pending human review; no reward has been issued.",
    "correlation_id": "cor_...",
    "retryable": false
  }
}
```

标准错误码包括 `POLICY_DENIED`、`CONSENT_REQUIRED`、`REVIEW_REQUIRED`、`DUPLICATE_EVENT`、`FRAUD_REVIEW_REQUIRED`、`CONTEXT_STALE` 和 `VALIDATION_ERROR`。每次访问和提交必须写入最小化 `access_audit`/`growth_audit`：主体、委托主体、角色、组织、目的、资源类别、政策结果、规则版本、关联 ID、时间和血缘引用；禁止记录原始身份标识、完整媒体、访问令牌或完整响应体。

---

## 10. 权限与边界

| 角色 | 允许范围 | 明确限制 |
| --- | --- | --- |
| 客户 | 查看本人授权范围内的成长摘要、提交/撤回内容和自愿分享邀请链接。 | 不能查看他人轨迹、媒体、积分或邀请归因。 |
| 一线员工/领队 | 仅所属组织、活动和获授权客户的最小服务上下文；可提交核验意见。 | 无批量导出、无原始身份/媒体默认读取、无直接积分入账。 |
| 增长运营审核员 | 审核其组织内积分、内容、裂变案件与规则建议。 | 高风险奖励/领队资格须双人复核；不能绕过客户授权或发送自动营销。 |
| 管理层 | 去标识化的组织级漏斗、质量与反馈指标。 | 默认无逐客户 PII、精确位置、原始媒体或跨组织数据。 |
| 平台管理员 | 策略、规则版本及运行元数据。 | 不具备默认客户数据读取权；break-glass 需限时审批及全量审计。 |

以下禁止事项为强制边界，而非待优化项：

- **禁止自动营销发送**：分享、活动、内容和积分事件不得自动触发短信、微信、企业微信、公众号或任何营销触达。
- **禁止无审核自动奖励**：任何积分、权益、等级或邀请奖励须进入审核/反作弊流程；规则计算不是发放。
- **禁止修改 SAP**：无 SAP 写接口、无 SAP 业务逻辑或主数据修改。
- **禁止修改 Core 生产同步**：仅读取受治理事实引用，不改变生产同步、订单、库存、价格或客户来源记录。
- **禁止未授权访问客户数据**：缺少组织、角色、用途、关系范围或同意的请求默认拒绝并审计。

---

## 11. 验收标准

- [x] **Outdoor Journey Model**：定义了必填字段、媒体/位置保护、状态机、验证状态和血缘。
- [x] **Points System**：定义了七类来源、四类用途、待审账本、冲正、兑换申请和反作弊控制。
- [x] **Level System**：定义了 Lv1–Lv5 的可回放升级条件、权益建议、安全限制和审核规则。
- [x] **Referral Network**：定义了分享至购买奖励的阶段、归因证据、反作弊、审核和冲正。
- [x] **Content Sharing**：覆盖视频号、小红书、公众号、企业微信及内容记录、授权、审核和奖励关系。
- [x] **Activity Integration**：定义了活动→推荐→购买→体验→分享→积分的只读、人工控制集成。
- [x] **Growth API**：定义了四个指定端点、权限、输入/输出、幂等、错误和审计契约。
- [x] **Feedback Loop**：定义了审核反馈、质量/公平/作弊指标、离线评估、审批发布和回滚原则。

**交付边界确认：** 本文档仅为设计，未部署服务、未配置连接器、未创建生产数据、未执行任何 SAP 或 Core 写入。
