# Dify Read-only Adapter Integration

## Architecture and boundary
Configure a Dify Workflow **HTTP Request** node to call `POST /api/v1/adapters/dify/retrieve`. Dify calls Memory Factory; only Memory Factory's retrieval composition can reach Qdrant. Qdrant remains bound to `127.0.0.1`. The adapter exposes no delete, upsert, collection-init, reindex, or memory-mutation routes.

## Authentication
Inject a rotatable service credential via a secret/environment variable into Dify and send `Authorization: Bearer $DIFY_MEMORY_TOKEN`. The Memory Factory composition maps each credential to a fixed organization/owner tuple. The request has no owner field; token values are never logged.

## Request and response
Send `{ "query": "leave policy", "top_k": 5, "filters": {"tags": ["hr"], "source": "handbook"} }`. The response has `records`; every record provides content, score, title, source, metadata, and a citation retaining memory/chunk IDs, document title, source, page, section, and score.

## Test, rollback, and failures
Use a desensitized document and verify a hit, citation, empty `records` for no answer, invalid-token `401`, and upstream `503`. Roll back by removing the Workflow node or reverting this adapter commit; no Dify source/database change is made. No production deployment is included.
