# VAFOX Memory Factory Phase 1B：AI Retrieval Layer 架构设计

> **状态：设计批准前（不部署）**  
> **范围边界：** 本文只定义 Memory Factory 的检索层契约、数据模型和上线前置条件。不得据此修改 Dify、SAP、Core 或生产 Compose/基础设施；Phase 1A 的上传、PostgreSQL、Redis、MinIO 和关键词搜索行为保持不变。

## 1. 目标、原则与非目标

### 1.1 目标

在已有 `memory_id`、对象存储和元数据的基础上，提供可过滤、可追溯、可重建的语义检索能力：

```text
Memory API / MinIO object
          │
          ▼
  Text extraction → normalization → chunking
          │                         │
          ▼                         ▼
   PostgreSQL chunk ledger     embedding provider
          │                         │
          └──────────────► Qdrant collection
                                      │
                                      ▼
                         Retrieval API / Dify adapter
```

1. PostgreSQL 是 Memory 元数据、任务状态和审计记录的事实来源；MinIO 是原始对象的事实来源；Qdrant 仅保存可再生的检索索引。
2. 每一个检索结果都必须能回溯到 `memory_id`、`chunk_id`、原始对象路径及文本偏移。
3. 所有向量查询都必须在 Qdrant **服务端 payload filter** 中应用所有者及其他授权范围，不能先检索再在应用层过滤。
4. 模型、维度、距离度量、切片器版本和文本规范化版本是索引身份的一部分；任一项变化时新建版本化 collection 并重建，绝不覆盖旧索引。

### 1.2 非目标

- 不在本阶段部署 Qdrant、embedding provider、worker 或队列消费者。
- 不改变 Phase 1A 的现有 REST 行为或 PostgreSQL 表结构；本文中的 SQL 是**未来迁移提案**，不是本次执行内容。
- 不直接让 Dify 写入或删除 Memory Factory 的 Qdrant collection，也不修改 Dify dataset、provider、工作流或 SAP/Core。
- 不承诺 OCR、复杂 Office/PDF 版面解析或 reranker 已经可用；它们以明确的接口和失败状态预留。

## 2. 推荐决策

### 2.1 模型选择

| 方案 | 优点 | 风险/限制 | 适用性 |
| --- | --- | --- | --- |
| **BGE-M3（推荐的默认生产候选）** | 可自托管，适合中英混合语料；避免将企业内容发送给第三方；可控制版本和成本。 | 需要 GPU/CPU 容量规划、模型服务运维和离线评测；不同部署实现必须固定 tokenizer/归一化规则。 | 企业私有资料、中文检索、数据驻留优先的场景。 |
| OpenAI `text-embedding-3-large` / `text-embedding-3-small` | 托管服务，集成和扩缩容简单；适合快速建立基准。 | 文本离开内网；依赖网络、配额、计费和区域/合规审批；模型升级须显式控制。 | 获得安全与采购批准后的受控 benchmark 或低敏感工作负载。 |
| Jina Embeddings v3 | 多语言和任务适配选项丰富，适合做备选评测。 | 同样需要第三方数据处理审批；task 参数、维度和 API 版本都须锁定。 | 需要对比多语言/检索任务表现时的候选 provider。 |

**结论：** Phase 1B 将 `BGE-M3` 作为默认设计基线，首个 collection 使用其部署时确认的输出维度（常见配置为 `1024`）和 cosine 距离。维度不是常量：创建 collection 前，由 provider capability 响应写入 `embedding_model_versions.dimension`，再以该值创建 collection。OpenAI `text-embedding-3-small` 和 Jina v3 作为经过数据合规审批后才可启用的 provider，用相同评测集比较 Recall@k、nDCG@k、p95 延迟、失败率和每千 chunk 成本；不得仅按模型名称切换。

### 2.2 模型抽象与 provider 切换

业务代码只依赖以下逻辑接口；实现可以是内部 HTTP 服务或同一进程适配器。provider 凭证仅在 provider adapter 的密钥管理中出现，永不写进 payload、任务参数或日志。

```python
class EmbeddingProvider(Protocol):
    def capabilities(self) -> EmbeddingCapabilities:
        """Return immutable model_id, model_version, dimension, max_input_tokens and distance."""

    def embed(self, request: EmbedRequest) -> EmbedResponse:
        """Embed ordered inputs; response preserves input ids and reports per-input failures."""

# EmbedRequest: {model_ref, inputs: [{id, text}], input_type: "query"|"document",
#                dimensions?: int, idempotency_key}
# EmbedResponse: {model_id, model_version, dimension, vectors: [{id, vector}], usage?, failures?}
```

`model_ref` 解析为受版本控制的 `EmbeddingProfile`，例如 `bge-m3@2026-07-20`。profile 固定：provider、endpoint、模型版本、维度、最大 batch token、最大输入 token、归一化策略和 Qdrant collection alias。一次 index run 只能使用一个 profile。切换流程为：注册 profile → capability 校验 → 建立新 collection → 用固定评测集验收 → 全量重嵌入 → 原子切换 collection alias → 保留旧 collection 至回滚窗口结束。禁止就地重嵌入或混合维度。

## 3. Qdrant 设计

### 3.1 Collection 与别名

每个 embedding profile 使用不可变 collection：

```text
memory_chunks__bge_m3__d1024__v1
```

应用只读写逻辑别名 `memory_chunks_active`；切换时原子地重新指向已验收 collection。collection 参数建议为 `vectors.size = profile.dimension`、`distance = Cosine`，并在容量验证后选择 HNSW 索引参数。所有写入使用确定性 point id（由 `chunk_id + embedding_profile_id` 生成 UUIDv5），因此 retry/upsert 是幂等的。

### 3.2 Vector schema

| 字段 | 值 |
| --- | --- |
| Point ID | `UUIDv5(namespace, "{chunk_id}:{embedding_profile_id}")` |
| Named vector | 初版单向量 `content`；值为 profile 输出的 `float32[dimension]`。未来多向量/稠密-稀疏混合必须使用新 collection。 |
| 距离 | cosine；输入向量须由 provider 按 profile 规范处理，不能由调用方任意归一化。 |
| 写入语义 | `upsert`，同时写入完整 payload；只有 PostgreSQL ledger 状态为 `ready` 的 chunk 才可写入。 |

### 3.3 Payload（metadata）schema

Qdrant payload 是检索过滤与 citation 的最小副本，不能存完整原文、访问令牌、任意 `metadata` 或敏感附件内容。

| Payload key | 类型 | 必填 | 用途/索引建议 |
| --- | --- | --- | --- |
| `memory_id` | keyword / UUID string | 是 | 回链 Memory；payload keyword index。 |
| `chunk_id` | keyword / UUID string | 是 | 唯一 chunk 回链；payload keyword index。 |
| `owner` | keyword | 是 | 授权边界；payload keyword index 且每次查询必过滤。 |
| `tags` | keyword array | 是（可空数组） | 业务过滤；payload keyword index。 |
| `source` | keyword | 是 | 来源过滤/观测；payload keyword index。 |
| `created_at` | RFC 3339 datetime | 是 | 时间范围过滤；datetime index。 |
| `memory_updated_at` | RFC 3339 datetime | 是 | 防止过期索引返回。 |
| `chunk_index` | integer | 是 | 原文顺序与相邻 chunk 扩展。 |
| `char_start`, `char_end` | integer | 是 | citation 定位。 |
| `content_sha256` | keyword | 是 | 去重、陈旧检测和审计。 |
| `embedding_profile_id` | keyword | 是 | 诊断与重建；必须等于 collection profile。 |
| `visibility` | keyword | 是 | 初版固定 `owner_only`；未来 ACL 扩展必须服务端过滤。 |

当 `memory_items.status = deleted` 时，索引 worker 必须删除所有对应 point；在删除完成前 Retrieval API 还必须以 PostgreSQL active 状态为最终校验，防止异步删除窗口泄露内容。

## 4. Chunk Pipeline

### 4.1 状态机与幂等性

```text
received → extraction_pending → extracting → extracted
         → chunking → embedding_pending → embedding → indexed
                                       ↘ failed (可重试/死信)
deleted ───────────────────────────────────────────→ purge_pending → purged
```

1. **触发：** Memory API 写入成功后，以 transactional outbox 写入 `memory.index.requested` 事件。不能以“上传 HTTP 请求仍在运行”作为处理任务。
2. **文本提取：** 按 MIME type 选择安全的 extractor；设定文件大小、页数、解压比、超时和字符数上限。无法提取的二进制对象进入 `failed`，错误代码如 `unsupported_media_type`、`extractor_timeout`，不产生空向量。
3. **规范化：** UTF-8、Unicode NFC、统一换行、删除 NUL；保留原始文本哈希与 extractor/version。不得悄然翻译、摘要或改变事实内容。
4. **切片：** 首版采用 tokenizer-aware recursive chunker：目标 512 tokens、overlap 64 tokens、hard max 640 tokens，优先按段落/句子边界断开。`chunk_id` 为稳定 UUID；内容、边界、token 数及 `chunker_version` 写入 PostgreSQL ledger。
5. **Embedding：** 对相同 `(content_sha256, embedding_profile_id)` 复用成功结果；按 provider token 上限 batch。使用 idempotency key `index_run_id:chunk_id`；指数退避且设置最大重试次数，随后死信并报警。
6. **Qdrant upsert：** 先确保 profile/collection 一致，再原子 upsert vector+payload。成功后才将 chunk 标为 `indexed`；重复事件可安全重放。
7. **删除与变更：** 更新内容或 owner/tags/source 时生成新 revision 并重新索引；删除事件先阻断查询（PostgreSQL status），再删除 Qdrant point，最后记录 `purged_at`。保留定期 reconciliation：比较 active chunk ledger 与 Qdrant scroll 结果。

### 4.2 建议的 PostgreSQL 未来数据模型

下表由 Phase 1B 独立 migration 创建；`memory_items`、`memory_tags` 与 `storage_objects` 保持 Phase 1A 定义不变。

| 表 | 关键字段 | 目的 |
| --- | --- | --- |
| `embedding_profiles` | `id`, `provider`, `model_id`, `model_version`, `dimension`, `distance`, `normalization_version`, `active`, `created_at` | 冻结模型能力与索引兼容性。 |
| `memory_extractions` | `id`, `memory_id`, `object_sha256`, `extractor`, `extractor_version`, `text_sha256`, `text_location`, `status`, `error_code`, `created_at` | 保存提取审计与文本（建议以受控 MinIO text sidecar 存储）。 |
| `memory_chunks` | `id`, `memory_id`, `extraction_id`, `revision`, `chunk_index`, `text_location`, `text_sha256`, `token_count`, `char_start`, `char_end`, `chunker_version`, `status`, `created_at`, `updated_at` | 检索的事实 ledger；唯一键 `(memory_id, revision, chunk_index)`。 |
| `chunk_embeddings` | `chunk_id`, `embedding_profile_id`, `point_id`, `content_sha256`, `collection_name`, `status`, `attempt_count`, `last_error_code`, `indexed_at` | 一个 chunk/profile 一条记录；唯一键 `(chunk_id, embedding_profile_id)`。 |
| `memory_index_outbox` | `id`, `event_type`, `aggregate_id`, `payload`, `idempotency_key`, `available_at`, `processed_at`, `attempt_count` | 可靠异步交接、重放和死信依据。 |

文本侧车对象建议使用 `memory-text/{memory_id}/{revision}/extracted.txt` 和 `.../chunks/{chunk_id}.txt`；使用与原对象相同的访问控制/加密策略。Qdrant payload 只保存定位字段，而 API 从 ledger/sidecar 读回实际片段，限制单条返回文本长度。

## 5. Retrieval API 设计（提案）

所有端点位于现有 Memory API 的认证/授权边界之后。本文的 `owner` 是 Phase 1A 已有 owner 字段；实际身份系统必须从已认证 principal 派生允许的 owner 集合，**不得信任客户端随意传入 owner 来扩大可见范围**。返回文本默认截断，且永不返回 MinIO 凭证或完整任意 metadata。

### 5.1 `POST /api/v1/search/vector`

语义检索已索引的 active chunks。服务先从身份上下文取得 `authorized_owners`，再将其与可选请求 filters 取交集并传给 Qdrant filter。

```json
{
  "query": "2026 年三季度的审批计划",
  "top_k": 10,
  "filters": {
    "owners": ["finance"],
    "tags_any": ["planning", "quarterly"],
    "source": "manual",
    "created_at_gte": "2026-01-01T00:00:00Z"
  },
  "include_text": true,
  "embedding_profile": "bge-m3@2026-07-20"
}
```

| 响应码 | 含义 |
| --- | --- |
| `200` | 查询完成，`results` 按 score 降序返回，允许空列表。 |
| `400` | 缺少/过长 query、无效过滤器、`top_k` 不在 1–50。 |
| `401` / `403` | 未认证或请求 owner 不在授权范围。 |
| `409` | profile 与 active collection 不兼容或索引尚未 ready。 |
| `429` | provider/query 限流。 |
| `503` | Qdrant 或 embedding provider 不可用；不降级为无过滤检索。 |

```json
{
  "query_id": "01J...",
  "embedding_profile": "bge-m3@2026-07-20",
  "results": [{
    "memory_id": "2f7c...",
    "chunk_id": "45ba...",
    "score": 0.83,
    "text": "...经截断的片段...",
    "citation": {"chunk_index": 3, "char_start": 1280, "char_end": 1910},
    "metadata": {"owner": "finance", "tags": ["planning"], "source": "manual", "created_at": "2026-07-01T...Z"}
  }],
  "next_cursor": null
}
```

`score` 只能与相同 collection/profile 内的结果比较。首版不承诺跨模型分数可比性；混合检索或 reranking 另行版本化 API。

### 5.2 `GET /api/v1/memory/{id}/related`

以指定 Memory 的已索引 chunks 聚合检索相似的**其他** memory。调用方必须先拥有该 memory 的读取权；查询同样应用 caller 的 owner filter，且排除原 `memory_id`。

Query 参数：`top_k`（1–20，默认 5）、`embedding_profile`（可选，默认 active）。响应为 `200 {"memory_id":"...","results":[{"memory_id","score","matched_chunk_id","metadata"}]}`；若 memory 不存在为 `404`，无权访问为 `403`，尚未 indexed 为 `409`。为避免 N×chunk 查询，worker/API 取最多 8 个代表 chunks，按每个候选 memory 的 maximum score 聚合并去重。

### 5.3 `POST /api/v1/embed`

这是受限的内部批量 embedding 契约，供 pipeline、诊断和经批准的适配器使用；不公开给浏览器或 Dify。网关须要求 service identity、model scope 和审计请求 ID。

```json
{
  "embedding_profile": "bge-m3@2026-07-20",
  "input_type": "document",
  "inputs": [{"id": "chunk-45ba", "text": "待向量化文本"}],
  "idempotency_key": "index-run-01J:chunk-45ba"
}
```

成功返回模型身份、维度和按 input id 对齐的 vectors；输入限制由 profile 施加。生产检索端点不得把完整向量返回给终端用户；如确需调试向量，使用受审计的内部环境并记录原因。

## 6. Dify 集成边界

```text
Dify Knowledge / RAG
        │  (approved read-only adapter; service identity)
        ▼
Memory Factory Retrieval API ──► Qdrant memory_chunks_active
        │                                │
        └──► PostgreSQL / MinIO citation  └──► vector payload only
```

推荐第一步是由一个**只读 Dify adapter**调用 `/api/v1/search/vector`，将结果转换为 Dify 上下文块并保留 `memory_id`、`chunk_id` 和 offsets 作为 citation metadata。这样 owner filter、删除保护、模型版本和审计仍由 Memory Factory 控制。Dify 不应直连本 collection，也不能使用其内部 dataset writer 向此 collection upsert。

如果未来必须让 Dify 直连 Qdrant：使用独立 collection/别名、最小只读 Qdrant API key、网络策略和相同 payload schema；将这种同步视为单向可重建副本。不得复用或修改已有 Dify knowledge collection，任何 Dify 侧 provider/model 配置均不在本 Phase 1B 变更范围。

## 7. 部署建议（仅供后续 staging 计划）

1. **拓扑：** staging 环境将 `memory-api`、index worker、Qdrant、PostgreSQL、Redis、MinIO 放在私有网络；仅批准的 API gateway 暴露 HTTPS。绝不暴露 Qdrant、PostgreSQL、Redis 或 MinIO 管理/数据端口到公网。
2. **职责拆分：** API 只接受请求和读取结果；独立 worker 消费 outbox；provider adapter 单独部署并实施 egress allowlist。Redis 仅用于队列/限流，不作为索引事实来源。
3. **密钥与网络：** Qdrant、MinIO、PostgreSQL 和外部 provider 凭证存于 secret manager；使用短期 service identity、mTLS/网络策略（可用时）及每服务最小权限。日志对 query、chunk text 和 Authorization 进行脱敏。
4. **持久化与恢复：** Qdrant 使用专属持久卷和快照；PostgreSQL/MinIO 保持现有备份并新增 ledger/outbox 恢复演练。灾难恢复顺序为 PostgreSQL → MinIO → Qdrant snapshot；若 Qdrant 不可恢复，从 active chunks ledger 可重建。
5. **容量起点：** 先在 staging 使用真实但脱敏的 corpus 测量 `chunk_count × dimension × 4 bytes`、HNSW 开销、payload 和副本数，再决定内存/磁盘与 replica。不得将这一估算直接视为生产容量承诺。
6. **可观测性：** 为 extraction 成功率、chunk 数/文档、embedding latency/错误、queue age、index lag、Qdrant upsert/search latency、filter 拒绝数、删除 backlog 和 retrieval 空结果率提供指标及 trace ID。审计记录 request identity、profile、collection、chunk ids、过滤器摘要和响应状态，而非全文。

## 8. 风险与控制

| 风险 | 影响 | 控制措施 |
| --- | --- | --- |
| 跨 owner 数据泄露 | 高 | 身份派生 owner 过滤；Qdrant 服务端 filter；PostgreSQL active/ACL 二次校验；授权负向测试。 |
| 模型切换导致维度不匹配或结果漂移 | 高 | 不可变 profile/collection；alias 蓝绿切换；固定评测集和回滚窗口。 |
| 异步写入造成陈旧/幽灵结果 | 高 | outbox、幂等 point id、状态机、删除优先阻断与 ledger/Qdrant reconciliation。 |
| 提取器处理恶意或超大文件 | 高 | MIME allowlist、沙箱、资源上限、反压、病毒扫描（如组织已有能力）和失败隔离。 |
| 第三方 embedding 的数据出境/成本不可控 | 高 | 默认自托管 BGE；DPA/区域审批；egress policy、配额、预算告警和 provider kill switch。 |
| Qdrant 是唯一事实来源 | 高 | PostgreSQL/MinIO 为事实来源；可重建索引、快照和恢复演练。 |
| 低质量检索被误当事实 | 中/高 | 离线 gold set、阈值/空结果策略、citation 强制返回、人工评审和明确的 RAG 提示约束。 |
| Dify collection 互相污染 | 高 | API-first read-only adapter；独立 collection/密钥；禁止写入既有 Dify collection。 |

## 9. 上线前设计验收清单

- [ ] 安全负责人批准 provider、数据分类、保留期和跨境处理方案。
- [ ] 为 BGE、OpenAI、Jina 在同一冻结评测集上记录 Recall@k、nDCG@k、p95、失败率和成本，并选择 profile。
- [ ] 验证 collection 的实际 dimension、distance、payload index 和 alias 仅指向已验收 collection。
- [ ] 覆盖 owner/tag/source/time filters、越权、删除竞态、重复事件、provider 超时、Qdrant 不可用和 profile 不匹配的集成测试。
- [ ] 验证从 PostgreSQL + MinIO 重建隔离 Qdrant collection，并完成快照恢复演练。
- [ ] 确认 Dify 仅通过 approved adapter 读取，且本次没有改动 Dify、SAP、Core 或生产基础设施。

