# VAFOX M4 Knowledge Brain
## Knowledge Service Layer V1 设计

**状态：** V1 架构与 API 契约设计  
**范围：** 企业知识的统一读取、检索、引用和推荐服务  
**非目标：** 本版本不实现 Agent，不执行自动化动作；不修改 SAP、Core 或生产 Dify。

## 1. 目标与设计原则

M3 Enterprise Memory 已提供资料接收、对象存储、元数据、Embedding、Qdrant 检索、Citation 和 ACL。本设计在其上定义一个面向业务调用方的统一 Knowledge API：调用方不需要了解文件格式、Memory ID、向量集合或检索实现。

V1 的原则如下：

1. **Knowledge-first，而非 Agent-first。** API 只返回经权限过滤的知识和推荐结果，不做任务规划、工具调用、写入或自动执行。
2. **Memory Factory 是底座。** Knowledge Item 是对 M3 `memory_items` 及其索引 chunk 的业务投影，不复制原始文件或绕过既有 ACL。
3. **服务端权限优先。** 用户、组织、部门、角色范围由网关注入的可信身份上下文决定；请求参数不能扩大可见范围。
4. **可追溯。** 每条搜索或推荐结果都带有 source 与可定位的 citation；没有可用引用时不得伪造内容。
5. **渐进兼容。** 按新增适配层和新增元数据演进；不改变 M3 既有 Memory API、Qdrant collection、SAP/Core/Dify 生产配置。

## 2. 总体架构

```text
 DOCX / PDF / Excel / Markdown
              |
              v
   Ingestion / Extractor（格式解析、页/Sheet/Section 定位）
              |
              v
 Domain Classifier + Metadata Validator
              |
              v
 Memory Factory（对象存储、memory_items、tags、ACL）
              |
              +---------------------> Index Worker -> Embedding -> Qdrant chunks
              |
              v
 Knowledge Service Layer V1
   |- GET /api/knowledge/search
   |- GET /api/knowledge/{id}
   `- GET /api/knowledge/recommend
              |
              v
 Web / 移动端 / 业务服务 / 未来只读 Agent Context Adapter
```

### 2.1 组件责任

| 组件 | 责任 | 不承担的责任 |
| --- | --- | --- |
| Ingestion / Extractor | 识别允许的文件格式，提取文本和位置锚点，产生标准化输入。 | 直接公开文件或决定最终业务权限。 |
| Classifier | 将资料归入受控知识域，提出标签与实体值，保留人工可复核入口。 | 赋予 ACL、自动执行业务动作。 |
| Metadata Validator | 校验域、枚举、长度、实体引用与必填字段。 | 接受调用方声明的 owner/visibility。 |
| Memory Factory | 保存原件、Metadata、tags 和 M3 ACL；维护删除状态。 | 提供业务领域的公开 API。 |
| Retrieval | 以 M3 的 embedding、Qdrant、active 状态和 ACL 过滤返回排序 chunk。 | 绕过 PostgreSQL 活跃状态校验或 ACL。 |
| Knowledge Service | 将业务筛选翻译为受控 Metadata 过滤，整合内容、source、citation、score。 | 写入知识、自动 Agent 执行、SAP/Core/Dify 修改。 |

## 3. Knowledge Domain Model

`domain` 为必填的受控枚举，值必须使用以下稳定代码；显示名称可本地化，API 不使用自由文本域名。

| Domain code | 名称 | 典型知识 | 主要 Metadata |
| --- | --- | --- | --- |
| `company` | 企业知识 | 制度、组织规则、经营策略、通用政策 | tags、owner、visibility |
| `brand` | 品牌知识 | 品牌定位、视觉规范、品牌策略 | brand、tags |
| `product` | 产品知识 | 产品资料、配方/规格、卖点、生命周期 | brand、product、tags |
| `sales` | 销售知识 | 销售话术、渠道政策、客户经营方法 | brand、product、store、tags |
| `store` | 门店知识 | 门店运营、陈列、库存、区域实践 | store、brand、tags |
| `sop` | 流程知识 | 审核后的标准作业流程、检查表、职责说明 | brand、product、store、tags |
| `activity` | 活动知识 | 营销活动、复盘、物料规则、活动日历 | brand、product、store、tags |

分类器可以返回候选域和置信度，但只有通过 Metadata Validator 的单一 `domain` 才能发布为可检索 Knowledge Item。跨域资料保留一个主域；补充关系使用 tags 或将来的关联表，不复制同一原件。

## 4. 数据模型与 Metadata

### 4.1 Knowledge Item 逻辑模型

Knowledge Item 是基于 `memory_items` 的**逻辑读模型**。`knowledge_id` 与底层 `memory_id` 使用同一个不可变 UUID，避免映射错配；文件本体仍由 Memory Factory 对象存储管理。

| 字段 | 类型 / 约束 | 来源与说明 |
| --- | --- | --- |
| `knowledge_id` | UUID，必填，只读 | 等于 M3 `memory_items.id` / `memory_id`。 |
| `domain` | enum，必填 | 七个 Domain code 之一；存放于受控 metadata。 |
| `title` | string，1–240 字符，必填 | 面向业务的标题；缺省时由文件名规范化产生，需审核。 |
| `source` | string，必填 | M3 来源标识；应可用于追踪原始资料来源。 |
| `brand` | string/null | 品牌的稳定业务标识；不以显示名称承担关联。 |
| `product` | string/null | 产品的稳定业务标识。 |
| `store` | string/null | 门店的稳定业务标识。 |
| `tags` | string[]，去重、有序 | 复用 M3 `memory_tags`；用于多标签过滤。 |
| `owner` | string，必填，只读 | M3 `owner_id`；由可信身份上下文写入。 |
| `visibility` | `private`/`department`/`organization`，必填，只读 | M3 ACL 字段；由可信身份与角色范围派生。 |
| `created_at` | RFC 3339 时间戳，只读 | M3 创建时间。 |
| `updated_at` | RFC 3339 时间戳，只读 | M3 更新时间，同时是索引新鲜度判断依据。 |

底层还必须保留 M3 的 `organization_id`、`department_id`、`role_scope`、`status`、`storage_path` 与原始 `metadata`，但它们不是普通查询调用方可覆盖的 Knowledge Item 字段。`status != active` 的项目不可通过 Knowledge API 返回。

### 4.2 推荐的 Metadata 命名空间

为避免与既有任意 `metadata` 键冲突，Knowledge 专有字段置于 `metadata.knowledge`：

```json
{
  "knowledge": {
    "domain": "sop",
    "title": "门店晨检 SOP",
    "brand": "brand-fox",
    "product": null,
    "store": "store-shanghai-001",
    "schema_version": "knowledge-v1"
  }
}
```

`owner`、`visibility`、组织与部门字段不得从该 JSON 或请求体读取，而必须复用 Memory Factory ACL 写入结果。`tags` 继续放在 `memory_tags`，以兼容 M3 的检索及索引载荷。

### 4.3 物理演进建议（实施时）

V1 实施采用增量方式：对 `memory_items.metadata` 的 `knowledge` 对象建立校验与查询索引（或在读取模型中投影），而非新建与 M3 独立的文档表。建议为 `metadata->'knowledge'->>'domain'`、`brand`、`product` 和 `store` 建立表达式索引；任何索引迁移都必须是 additive、可回滚的。Qdrant chunk payload 仅复制过滤和 citation 所需的最小字段，例如 `memory_id`、`domain`、`brand`、`product`、`store`、`tags`、`source`、ACL 范围和定位锚点；不得复制原文全文、令牌或任意敏感 Metadata。

## 5. Knowledge Pipeline

```text
资料 -> 类型校验与提取 -> 分类 -> Metadata 校验 -> Memory -> Index -> Retrieval
```

1. **资料接收：** 接收 DOCX、PDF、Excel 或 Markdown，记录原始文件名、MIME 类型、来源和校验哈希。
2. **类型校验与提取：** 仅允许下节定义的格式；提取器输出标准化文本及可引用位置。解析失败时不得进入索引。
3. **分类：** 规则或人工复核为资料选择主 `domain`；生成候选 brand/product/store/tags，但不以推断值越权发布。
4. **Metadata：** 验证 Knowledge Item 必填项和受控枚举；使用网关注入的身份写入 owner、组织/部门和 visibility。
5. **Memory：** 将原件、受控 Metadata、tags 和 ACL 写入现有 Memory Factory；得到 `knowledge_id = memory_id`。
6. **Index：** 由既有异步索引链路分块、embedding 并写入 Qdrant；每个 chunk 保留页/段/Sheet/行等 citation 锚点。
7. **Retrieval：** Knowledge Service 先构建 ACL 约束，再叠加 domain、实体及 tags 的收窄过滤；最终由 M3 active 状态与 ACL 复核。

### 5.1 支持的来源与引用锚点

| 格式 | 接收策略 | Citation 最低定位 |
| --- | --- | --- |
| DOCX | 解析正文、标题层级与表格文本。 | `section`、`chunk_id`、字符范围。 |
| PDF | 提取每页文本；扫描件须经受控 OCR 流程后才可索引。 | `page`、`chunk_id`、字符范围。 |
| Excel (`.xlsx`) | 提取工作表、行/列和单元格文本，不执行公式或宏。 | `sheet`、`row`（可含 cell range）、`chunk_id`。 |
| Markdown (`.md`) | 解析标题、段落和代码块；代码块按原文保留。 | `section`、`chunk_id`、字符范围。 |

文件扩展名与 MIME 类型必须交叉验证；对加密、损坏、超限、含宏或无法提取引用位置的文件，返回明确的处理失败状态并保留审计记录，不能产生可检索知识。

## 6. 统一 Knowledge API

### 通用约定

* 所有端点均为只读 `GET`，由网关认证；身份上下文沿用 M3 ACL。
* API 路径为 `/api/knowledge`，作为 M3 `/api/v1/memory` 与 `/api/v1/search/vector` 之上的业务边界。
* 过滤器只能缩小结果。`owner`、`visibility`、组织、部门和角色范围不是客户端可控制的查询参数。
* 正常响应使用 `application/json`；时间为 RFC 3339；`score` 为排序分数，不等同于事实置信度。
* 推荐及搜索结果必须附带 `citation`。若没有 ACL 可访问的结果，返回 `200` 和空 `items`，不得以其他租户或已删除资料补齐。

### 6.1 `GET /api/knowledge/search`

按关键词/语义检索，并以业务 Metadata 收窄结果。

| Query 参数 | 必填 | 类型 | 规则 |
| --- | --- | --- |
| `query` | 是 | string | 1–4096 字符，去首尾空白后非空。 |
| `domain` | 否 | enum | 七个 domain code 之一。 |
| `brand` | 否 | string | 精确匹配稳定品牌标识。 |
| `product` | 否 | string | 精确匹配稳定产品标识。 |
| `tags` | 否 | comma-separated string | 每项为精确 tag；多项采用 **AND**，以持续收窄结果。 |
| `limit` | 否 | integer | 1–50，默认 10。 |

成功示例：

```json
{
  "query_id": "uuid",
  "items": [
    {
      "knowledge_id": "0b5e4d71-0f2f-4c59-b2f8-8f2f9a5c2bb1",
      "domain": "sop",
      "title": "门店晨检 SOP",
      "content": "开店前完成收银、陈列与冷链检查……",
      "source": "store-operations-manual-2026.pdf",
      "citation": {
        "memory_id": "0b5e4d71-0f2f-4c59-b2f8-8f2f9a5c2bb1",
        "chunk_id": "chunk-03",
        "page": 12,
        "section": "3.1 开店前检查",
        "char_start": 1280,
        "char_end": 1542
      },
      "score": 0.91
    }
  ],
  "next_cursor": null
}
```

`content` 是可显示的、长度受限的命中 chunk 文本，不是原始文件全文。客户端要读取受权限控制的详情，应调用详情端点。

错误：`400 invalid_query`（参数不合法）、`401 authentication_required`、`403 forbidden`（调用方无服务访问权限）、`503 retrieval_unavailable`。没有匹配项不是错误。

### 6.2 `GET /api/knowledge/{id}`

返回一个已授权且 active 的知识详情。`id` 为 `knowledge_id`（即 M3 `memory_id`）。服务必须先以 M3 `can_access` 进行 ACL 判断，之后才加载 Metadata、内容或引用。

```json
{
  "knowledge_id": "0b5e4d71-0f2f-4c59-b2f8-8f2f9a5c2bb1",
  "domain": "sop",
  "title": "门店晨检 SOP",
  "source": "store-operations-manual-2026.pdf",
  "brand": "brand-fox",
  "product": null,
  "store": "store-shanghai-001",
  "tags": ["opening", "inspection"],
  "owner": "user-123",
  "visibility": "department",
  "created_at": "2026-07-21T09:00:00Z",
  "updated_at": "2026-07-21T09:15:00Z",
  "content": "…受权限控制的规范化全文或受限详情…",
  "citations": [{"memory_id": "…", "chunk_id": "chunk-01", "page": 1, "section": "1. 目的"}]
}
```

返回 `404 knowledge_not_found` 用于不存在或非 active 项；对存在但调用者无权访问的项目返回 `403 forbidden`，且不泄露标题、source 或存在性之外的详情。`id` 非 UUID 返回 `400 invalid_knowledge_id`。

### 6.3 `GET /api/knowledge/recommend`

为已认证用户在明确场景中推荐已授权知识；它是**只读排序接口**，不生成回答、不调用工具、不创建任务。

| Query 参数 | 必填 | 类型 | 规则 |
| --- | --- | --- |
| `scenario` | 是 | string | 1–200 字符，如 `store_opening`、`sales_pitch`。 |
| `need` | 是 | string | 1–4096 字符的业务需求描述。 |
| `domain` | 否 | enum | 业务调用方希望收窄的域。 |
| `brand` | 否 | string | 稳定品牌标识。 |
| `product` | 否 | string | 稳定产品标识。 |
| `store` | 否 | string | 稳定门店标识。 |
| `limit` | 否 | integer | 1–20，默认 5。 |

服务从可信身份获得 `user`，不接受请求传入的用户 ID。推荐排序可以组合场景/需求检索相关度、Metadata 适配度、更新时间和人工设定的业务优先级；排序特征不得突破 ACL，且结果的 `score` 要说明为 `recommendation_score`。响应沿用 search 的 `items` 格式，并额外返回 `scenario` 与 `need` 的规范化回显。

## 7. 权限、隔离与审计

Knowledge Service 必须兼容并复用 Memory Factory ACL：

1. 从网关注入的 `organization_id`、`department_id`、`owner_id` 和 `role_scopes` 建立可信 `AuthContext`；不得相信 query/body 中同名字段。
2. 所有搜索/推荐请求都先应用组织边界，再按已有 private、department、organization 可见性规则过滤；管理员行为仍只在同组织内有效。
3. 向量检索必须将 ACL 约束与 domain/实体/tags 条件同时下推，并在返回前以 Memory 的 active 状态和 ACL 再次验证，覆盖异步删除或索引滞后窗口。
4. 详情读取先授权、后取内容；禁止先从对象存储读取后再判断权限，禁止生成可跨权限使用的原件 URL。
5. 审计仅记录请求 ID、调用者/组织摘要、端点、过滤摘要、返回数量、knowledge/chunk ID、响应状态和耗时；默认不记录全文、需求原文或访问令牌。需求文本可只保存不可逆 hash。
6. Metadata 中的 brand/product/store 是检索条件，不是授权维度；若未来需要按实体隔离，必须扩展服务端 ACL 模型并完成审计，而不能由客户端过滤模拟。

## 8. Future Agent Interface（未来接口，不在 V1 启用）

未来 Agent 仅可通过受控的只读 Context Adapter 调用 Knowledge API。建议预留以下内部契约，而不在 V1 暴露 Agent 执行能力：

```json
{
  "principal": "gateway-derived-only",
  "purpose": "sales_assist",
  "query": "…",
  "filters": {"domain": "sales", "brand": "brand-fox"},
  "max_results": 5,
  "require_citations": true
}
```

Adapter 必须把调用者身份和 `purpose` 传给 Knowledge Service，返回 citation-ready context blocks 及限制说明。它不得拥有写入、删除、reindex、SAP 调用、Core 修改、Dify 配置修改或自动执行权限。未来若增加知识草稿、反馈或 Agent 产物，必须进入单独的人工审核发布流程；未经审核的内容不能进入 `active` Knowledge Item 或推荐集。

## 9. V1 验收与边界

* 七个 domain code 和 Knowledge Item 所列字段均可校验、读取和返回。
* 四类来源均能产生符合最低定位要求的 citation，或以明确失败状态拒绝索引。
* 三个 GET API 都只返回 active 且 ACL 已授权的内容，且 search 结果包含 `content`、`source`、`citation` 和 `score`。
* 任意请求传入的 owner、visibility、组织、部门或角色字段不会扩大检索范围。
* 已删除、跨组织、跨部门或 private 无权限资料不能通过关键词、向量、推荐或详情端点泄露。
* 本设计及实施不修改 SAP、Core、生产 Dify，也不引入自动 Agent 执行。

