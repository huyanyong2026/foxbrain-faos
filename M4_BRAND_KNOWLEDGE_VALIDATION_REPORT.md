# M4.2 Brand Knowledge Base Validation Report

**Validation date:** 2026-07-21  
**Result:** PASS — KAILAS, MAMMUT, and OSPREY complete the M4.2 brand-knowledge acceptance loop.  
**Validation boundary:** Read-only Knowledge service assets and APIs only. This validation does not write to SAP/Core and does not invoke autonomous agents.

## Acceptance summary

| Acceptance item | Result | Evidence |
| --- | --- | --- |
| 1. Brand Schema | PASS | The schema has 12 required fields, including identity, positioning, user, product, scenario, sales, comparison, and traceability fields. |
| 2. Brand-material import | PASS | Markdown and DOCX imports create deterministic document IDs, SHA-256 metadata, MIME metadata, importer/time metadata, ACL metadata, and source locations. PDF page extraction remains supported through the pinned `pypdf` dependency. |
| 3. Brand Retrieval | PASS | Authenticated search and scenario-recommendation routes return matching KAILAS, MAMMUT, or OSPREY records and enforce document organization/department isolation. |
| 4. Citation | PASS | Seeded results expose versioned source/location traceability; imported Markdown/DOCX results expose line/paragraph locations. The 24-question suite asserts a `source` and `location` for every matching result. |
| 5. Brand tests | PASS | 24 retrieval/recommendation questions across all requested sales dimensions, plus schema, import, ACL, authentication, and citation tests, passed. |
| 6. Brand Comparison Test | PASS | All three two-brand combinations return the requested records, comparison fields, and brand-level traceability. |

## Validated brand records

| Brand | Positioning | Primary customer/use focus | Retrieval citation location |
| --- | --- | --- | --- |
| KAILAS 凯乐石 | Professional mountain outdoor brand | Mountaineering, climbing, hiking, trail-running users; high-altitude and technical mountain activity | `brand:kailas` |
| MAMMUT 猛犸象 | Professional alpine, safety-oriented outdoor brand | Mountaineering, climbing, snow and exposed-environment users with safety-performance needs | `brand:mammut` |
| OSPREY | Outdoor-pack brand centered on carry systems | Hiking, travel, camping, and comfort-focused users; fit, load, capacity, and organization needs | `brand:osprey` |

## Brand Schema validation

The catalog contains exactly the three required phase-one brand IDs: `kailas`, `mammut`, and `osprey`. Every record was validated against the required contract:

`brand_id`, `brand_name`, `positioning`, `origin`, `target_user`, `product_lines`, `scenarios`, `selling_points`, `competitors`, `sales_tips`, `recommendations`, and `source_traceability`.

The traceability entry provides a source, stable brand location, and version for seeded claims. This makes a response distinguishable from imported evidence and provides a source-replacement path when approved brand material is added.

## Brand-material import and citation validation

| Material | Citation granularity | Validation result |
| --- | --- | --- |
| Markdown (`.md`, `.markdown`) | Line | Imported a KAILAS Markdown document and verified `line:1`, SHA-256 metadata, and department ACL. |
| DOCX (`.docx`) | Paragraph | Imported a MAMMUT DOCX document and verified `paragraph:1`. |
| PDF (`.pdf`) | Page | Supported by the import implementation via the pinned `pypdf` dependency; page citations are emitted for non-empty extracted pages. |

ACL validation used a department-scoped OSPREY document. A same-organization user in another department and a user in another organization could not retrieve the document; a user in the importing organization and department could retrieve it. This confirms retrieval does not expose imported evidence across the tested organization/department boundaries.

## Brand Retrieval and sales-question validation

The automated suite executed **24** questions. Every row required an HTTP 200 response, the expected brand in the result set, and a non-empty citation `source` and `location` on each matching item.

| # | Coverage | Question intent / query | Expected brand | Result |
| ---: | --- | --- | --- | --- |
| 1 | Brand positioning | Professional mountain positioning | KAILAS | PASS |
| 2 | Brand positioning | Swiss origin | MAMMUT | PASS |
| 3 | Brand positioning | Carry-system focus | OSPREY | PASS |
| 4 | User profile | Hiking enthusiasts | KAILAS | PASS |
| 5 | User profile | Safety-performance-focused users | MAMMUT | PASS |
| 6 | User profile | Carry-comfort-focused users | OSPREY | PASS |
| 7 | Product line | Trail running | KAILAS | PASS |
| 8 | Product line | Hardshell apparel | MAMMUT | PASS |
| 9 | Product line | Hydration reservoirs | OSPREY | PASS |
| 10 | Product line | Snow equipment | MAMMUT | PASS |
| 11 | Use scenario | High-altitude mountaineering | KAILAS | PASS |
| 12 | Use scenario | Ice and snow | MAMMUT | PASS |
| 13 | Use scenario | Multi-day camping | OSPREY | PASS |
| 14 | Use scenario | Travel | OSPREY | PASS |
| 15 | Competitor comparison | KAILAS record naming MAMMUT | KAILAS | PASS |
| 16 | Competitor comparison | MAMMUT record naming KAILAS | MAMMUT | PASS |
| 17 | Competitor comparison | OSPREY record naming DEUTER | OSPREY | PASS |
| 18 | Sales advice | Layering advice | KAILAS | PASS |
| 19 | Sales advice | Exposed-environment assessment | MAMMUT | PASS |
| 20 | Sales advice | Torso-length measurement | OSPREY | PASS |
| 21 | Sales advice | In-store fit adjustment | OSPREY | PASS |
| 22 | Scenario recommendation | High-altitude mountaineering recommendation | KAILAS | PASS |
| 23 | Scenario recommendation | Technical mountaineering recommendation | MAMMUT | PASS |
| 24 | Scenario recommendation | Multi-day hiking recommendation | OSPREY | PASS |

## Brand comparison validation

The authenticated comparison endpoint was validated for each pair, with both requested IDs present and every returned record retaining its stable `brand:<id>` traceability location.

| Comparison | Result | Decision-useful dimensions available |
| --- | --- | --- |
| KAILAS vs. MAMMUT | PASS | Positioning, origin, product lines, scenarios, selling points, sales tips, recommendations |
| KAILAS vs. OSPREY | PASS | Positioning, origin, product lines, scenarios, selling points, sales tips, recommendations |
| MAMMUT vs. OSPREY | PASS | Positioning, origin, product lines, scenarios, selling points, sales tips, recommendations |

Unauthenticated comparison was separately rejected with HTTP 401.

## Commands and results

```bash
PYTHONPATH=. pytest -q tests/test_m4_brand_knowledge.py tests/test_m4_knowledge_foundation.py
# 35 passed in 0.18s

PYTHONPATH=. python -m compileall -q services tests
# passed

git diff --check
# passed
```

## Acceptance conclusion

All six requested acceptance areas passed. The three brands now have a validated, citation-bearing, ACL-aware retrieval and comparison loop, with a 24-question suite covering positioning, target users, product lines, scenarios, competitors, and sales advice.
