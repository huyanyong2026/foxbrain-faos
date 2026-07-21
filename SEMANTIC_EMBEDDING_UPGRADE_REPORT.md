# VAFOX Semantic Embedding Upgrade Report

## Decision

`semantic_v2` is the new immutable embedding profile.  The production recommendation is **BGE-M3** (1024 dimensions, cosine distance) because it supports Chinese and English business terminology, long-context retrieval, and can be deployed privately.  The same unchanged `EmbeddingProvider` interface also supports DeepSeek-compatible and Hunyuan embedding gateways through OpenAI-compatible `/v1/embeddings` endpoints.  Provider credentials and endpoints remain deployment-injected through `EMBEDDING_PROFILE_REGISTRY`; no key is stored in source control.

Example profile registry entry:

```json
{
  "semantic_v2": {
    "provider": "bge-m3",
    "model_id": "bge-m3",
    "model_version": "v2",
    "dimension": 1024,
    "max_input_tokens": 8192,
    "endpoint": "https://embedding.internal/v1/embeddings",
    "api_key_env": "BGE_M3_API_KEY"
  }
}
```

## Reindex and cutover

1. Enumerate only active Memory records.
2. Re-chunk each document with the `semantic-v2-recursive-whitespace` profile (384-token target, 64-token overlap).
3. Create **`memory_chunks_v2`** and write the new vectors there.
4. Verify the exact Qdrant point count equals the generated chunk count.
5. Atomically move the existing retrieval alias to `memory_chunks_v2` only after verification succeeds.

The worker refuses to reuse `memory_chunks_v2`; it never overwrites or deletes the v1 collection.  A failed extraction, embedding, or count check leaves the live alias unchanged.

## Business validation (25 questions)

Run the 25-question validation set against both aliases before enabling the `switch_alias` flag.  Score a question correct only when an expected memory is returned in the configured top-k and retain query latency from the retrieval response.

| Area | Questions | v1 baseline | v2 release gate |
| --- | ---: | ---: | ---: |
| Sales talk tracks | 9 | 88% aggregate baseline | >=95% aggregate |
| Product combinations | 8 | 88% aggregate baseline | >=95% aggregate |
| Campaign recommendations | 8 | 88% aggregate baseline | >=95% aggregate |
| **Total** | **25** | **88%** | **>=95%** |

The release is **not approved** until all 25 results, their expected citations, and p50/p95 latency are attached to the deployment record.  This repository does not fabricate live evaluation results.

## Latency and cost assessment

Measure embedding batch p50/p95 and retrieval p50/p95 in the target environment.  The v2 chunk target may increase vector count relative to v1; calculate monthly embedding cost as `total reindexed tokens / 1,000,000 * provider price per million tokens`, and storage cost from the resulting Qdrant point count and 1024-dimensional vectors.  BGE-M3 self-hosting shifts this to GPU/operations cost; Hunyuan and DeepSeek-compatible gateways are billed according to the configured vendor contract.  Cutover requires no duplicate query path, so steady-state retrieval latency is limited to the selected vector collection.

## Rollback

Keep the v1 physical collection unchanged for the agreed retention period.  To roll back, atomically call `switch_alias` with the previous v1 collection name; no re-embedding is required.  Disable the `semantic_v2` profile only after traffic has returned to v1 and audit logs confirm the alias target.
