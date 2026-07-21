# M4 Knowledge Foundation Report

**Status:** implemented and covered by automated tests.  
**Scope:** M4 adds isolated Embedding and Knowledge read services over the existing M3 Memory Retrieval/ACL boundary. No SAP, Core, or production Dify code or configuration was changed.

## Delivered services

### Semantic_v2 Embedding HTTP service

`services.embedding.app` provides a container-ready WSGI service:

| Endpoint | Contract |
| --- | --- |
| `GET /health` | Provider health plus model, version, and dimension. Returns `503` if the upstream provider is unhealthy. |
| `POST /embed` | Accepts `{"text":"..."}` and returns `vector`, `dimension`, `model`, `version`, and `latency_ms`. |
| `POST /embed_batch` | Accepts `{"texts":["...", "..."]}` and returns `vectors` plus the same model metadata. |

The service wraps the M3 OpenAI-compatible semantic embedding adapter using the named `semantic_v2` profile. `SEMANTIC_V2_TIMEOUT_SECONDS`, `SEMANTIC_V2_MAX_RETRIES`, and `SEMANTIC_V2_MAX_BATCH` configure upstream deadline, retry count, and request batch bound. Provider retry behavior is restricted to transient failures by the existing adapter.

Docker Compose adds `embedding-api` with the common service Dockerfile and `/health` container healthcheck.

### Knowledge API

`services.knowledge.app` provides the read-only endpoints:

* `GET /api/knowledge/search`
* `GET /api/knowledge/{id}`
* `GET /api/knowledge/recommend`

The API treats an active M3 `memory_items` record as its logical Knowledge Item. It reads controlled fields from `metadata.knowledge`, returns `content`, `source`, `citation`, `score`, and metadata, and validates the seven documented domain values. Search and recommendation call M3 `RetrievalService`; each candidate is then re-read from Memory and checked for active status and ACL before it is returned. This second check protects against index lag after deletion or permission changes.

Metadata filters (`domain`, `brand`, `product`, `store`, and tags) only narrow result sets. Tag lists are enforced as AND filters after retrieval. The detail endpoint authorizes before loading the Memory content.

## Authentication and ACL

The trusted `AuthContext` accepts either gateway-injected `X-VAFOX-*` identity headers or a verified HS256 JWT. Gateway verifies the JWT and forwards only its organization, subject, department, and role scopes; it does not forward client-supplied identity headers.

Client query/body values named `owner`, `organization`, `department`, `visibility`, or role fields are not used to build the context. Memory ACL retains organization isolation first, then permits only administrator, owner, organization-visible, or matching department-visible records as appropriate. The M4 tests include a private-record cross-user attempt with `owner=alice`, which remains denied for Bob.

## Deployment

New compose services are `embedding-api` (default host port `8083`) and `knowledge-api` (default host port `8084`). Gateway routes `/api/knowledge` to `knowledge:8080`. Both are additive services and use the existing shared Docker image, network, and healthcheck conventions.

## Validation

Executed:

```bash
PYTHONPATH=. pytest -q tests/test_m4_knowledge_foundation.py tests/test_embedding_provider.py tests/test_retrieval.py tests/test_memory_permissions.py
PYTHONPATH=. python -m compileall -q services packages
git diff --check
```

The focused suite verifies embedding health/single/batch contracts; Knowledge search; citation; authentication required behavior; private ACL behavior; detail authorization; and that a client `owner` filter cannot escalate Bob to Alice's access.
