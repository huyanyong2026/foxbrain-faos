# VAFOX M4.2 Brand Knowledge Base Report

**Status:** implemented and covered by automated tests.  
**Boundary:** This delivery adds a read-only brand knowledge asset layer to the Knowledge service. It does **not** modify SAP, Core, or execute autonomous agents.

## Phase-one brand assets

The starter catalog contains **KAILAS**, **MAMMUT**, and **OSPREY**. Each `BrandEntity` carries the required contract:

| Field | Purpose |
| --- | --- |
| `brand_id`, `brand_name` | Stable machine identifier and display name. |
| `positioning`, `origin`, `target_user` | Brand identity and intended customer. |
| `product_lines`, `scenarios`, `selling_points` | Product and use-case discovery. |
| `competitors`, `sales_tips`, `recommendations` | Comparison and assisted sales guidance. |

The starter content is deliberately retailer-facing and concise. Brand-document evidence is returned alongside claims so additional authorized source material can supersede or enrich the starter catalog.

## Knowledge import flow

`BrandKnowledgeStore.import_document(path, brand_id, context, visibility)` accepts:

* **Markdown** (`.md`, `.markdown`) with line citations.
* **DOCX** (`.docx`) with paragraph citations, using standard-library ZIP/XML parsing.
* **PDF** (`.pdf`) with page citations when the optional `pypdf` extraction dependency is installed; a clear `pdf_import_requires_pypdf` error is returned otherwise instead of silently ingesting empty content.

Every import automatically produces SHA-256 content metadata, MIME type, original filename, importer, UTC timestamp, deterministic document ID, and citation locations. ACL is derived from the trusted `AuthContext`: organization is always required, department documents additionally require a matching department (unless owner/admin), and private documents remain owner/admin-only.

## Brand Retrieval API

All endpoints require the existing gateway/JWT-derived auth context:

| Endpoint | Use |
| --- | --- |
| `GET /api/brands/search?query=...&brand_id=...` | Brand and document-evidence search with citations. |
| `GET /api/brands/compare?brands=kailas,mammut` | Compare two or three brands across positioning, products, scenarios, selling points, sales tips, and recommendations. |
| `GET /api/brands/recommend?scenario=...` | Scenario recommendation based on the same evidence-aware search contract. |

The API is read-only. Import is an explicit trusted application/service operation; it is not exposed as an agent action or an unauthenticated HTTP write endpoint.

## Test coverage

`tests/test_m4_brand_knowledge.py` contains 20 parametrized brand questions spanning positioning, product lines, scenarios, and sales guidance. It additionally verifies required schema fields, Markdown and DOCX metadata/citation generation, department and organization ACL isolation, comparison output, and authentication requirements.

## Validation

Executed:

```bash
PYTHONPATH=. pytest -q tests/test_m4_brand_knowledge.py tests/test_m4_knowledge_foundation.py
PYTHONPATH=. python -m compileall -q services tests
git diff --check
```
