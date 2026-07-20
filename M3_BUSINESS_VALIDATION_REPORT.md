# VAFOX M3 Enterprise Memory Business Validation Report

**Validation date:** 2026-07-20  
**Repository:** `foxbrain-faos` (branch `work`)  
**Overall decision:** **BLOCKED — not ready for business acceptance**

## 1. Scope and acceptance rule

This validation covers the six requested M3 memory-chain checkpoints for the
following supplied business-source names:

1. `火狐狸简介.docx`
2. `连单和微信回复2023.xls`
3. `连单和微信回复2024.xls`

The acceptance rule is deliberately end-to-end: each source must be uploaded,
successfully indexed, embedded, and written to a live Qdrant collection; each
business question must then return an answer grounded in a retrieved source
chunk and a usable citation. Unit-test doubles are recorded as implementation
evidence only and are **not** treated as production/business acceptance.

## 2. Input and environment evidence

| Check | Result | Evidence | Impact |
| --- | --- | --- | --- |
| The three named source files are present in the workspace | **Blocked** | A filesystem search found no `.docx`, `.xls`, or `.xlsx` input files, including none with the requested names. | No authentic upload, extraction, index, or answer quality test can be run. |
| Local container runtime is available | **Blocked** | `docker` is not installed in this environment. | No live memory API, embedding endpoint, or Qdrant service can be started or inspected here. |
| Qdrant is declared for a production composition | **Pass (configuration only)** | `docker-compose.prod.yml` declares a `qdrant` service and `.env.production` configures `QDRANT_URL`. | Deployment remains unverified because no runtime is available. |
| Phase 1B automated checks | **Pass (implementation contract)** | 13 focused tests passed with `PYTHONPATH=.`. | Confirms tested contracts, not the requested business data flow. |

## 3. Six checkpoint results

| # | Checkpoint | Status | Validation result |
| --- | --- | --- | --- |
| 1 | Document upload | **Blocked** | The named documents are absent. The current memory receive API can store an uploaded object, but no requested source was available to submit. |
| 2 | Automatic index | **Blocked / gap found** | The index worker is asynchronous and idempotent for text-like content. Its extractor explicitly returns `extract_failed` for `.docx` and `unsupported_file_type` for `.xls`/`.xlsx`; therefore all three requested input formats cannot complete the current worker unchanged. |
| 3 | Embedding | **Not executed** | The embedding adapter supports OpenAI-compatible single and batch embeddings and validates configured vector dimension. No live endpoint/profile or extracted source text was available. |
| 4 | Qdrant write | **Not executed** | The adapter supports collection initialization, stable alias assignment, payload validation, and point upsert. No Qdrant runtime or source chunks were available for a live write. |
| 5 | Retrieval query | **Not executed** | Vector retrieval embeds the query, enforces authorized owners in the server-side Qdrant filter, and returns ranked points. No live index exists to query. |
| 6 | Citation return | **Not executed for source data** | Retrieval response construction includes `memory_id`, `chunk_id`, `source`, `page`, and `section` in each citation. The focused retrieval test verifies a chunk citation, but cannot establish citations for the three business documents. |

## 4. Implementation evidence (not a substitute for live acceptance)

The focused suite passed **13 tests**:

```text
PYTHONPATH=. pytest -q tests/test_embedding_provider.py \
  tests/test_memory_factory_phase1b.py \
  tests/test_index_pipeline.py \
  tests/test_retrieval.py
13 passed in 0.19s
```

The passing tests cover:

- OpenAI-compatible embedding requests, batch handling, retry behavior, and
  profile selection.
- Deterministic chunking, idempotent index-job creation, embedding-to-point
  construction, and Qdrant upsert invocation using test doubles.
- Qdrant collection/alias lifecycle, payload validation, owner filtering, and
  vector API authorization boundaries using test doubles.
- Retrieval response construction with a `chunk_id` citation and safe failure
  mapping when embeddings are unavailable.

### Material compatibility finding

The requested input formats are not merely unavailable in this workspace: the
current extractor does not parse them. It only decodes text-like files, raises
`extract_failed` for `pdf`/`docx`, and raises `unsupported_file_type` for
`xls`/`xlsx`. Consequently, copying the three files into the repository and
starting services would still not meet the six checkpoints until a DOCX parser
and spreadsheet parser/normalizer are integrated and covered by tests.

## 5. Business question set (25 questions)

The following questions meet the requested minimum of 20 and are ready for the
rerun. **All 25 are Not Executed** because the source documents and live index
were unavailable. For every question, acceptance requires: (a) an answer based
only on retrieved content, (b) at least one citation with source name and
chunk/location, and (c) no invented value when the source does not support it.

| # | Category | Test question | Status |
| --- | --- | --- | --- |
| 1 | 企业介绍 | 火狐狸是什么企业？请概括其主营业务与定位。 | Not executed |
| 2 | 企业介绍 | 火狐狸的成立背景、使命或愿景是什么？ | Not executed |
| 3 | 企业介绍 | 公司当前有哪些核心业务板块？ | Not executed |
| 4 | 企业介绍 | 火狐狸服务的主要客户或消费场景是什么？ | Not executed |
| 5 | 企业介绍 | 请列出企业介绍中明确提到的竞争优势。 | Not executed |
| 6 | 门店 | 2023 年连单记录涉及哪些门店？ | Not executed |
| 7 | 门店 | 哪些门店在 2024 年的连单记录中出现？ | Not executed |
| 8 | 门店 | 某一门店的客户微信回复中最常见的咨询主题是什么？ | Not executed |
| 9 | 门店 | 请比较 2023 与 2024 年门店连单话术的差异。 | Not executed |
| 10 | 门店 | 哪些门店/记录需要进一步确认归属信息？ | Not executed |
| 11 | 品牌 | 企业介绍中提到哪些品牌？各自定位是什么？ | Not executed |
| 12 | 品牌 | 某品牌适合向哪类客户推荐？ | Not executed |
| 13 | 品牌 | 品牌相关回复中，客户最关注的卖点或顾虑有哪些？ | Not executed |
| 14 | 品牌 | 不同品牌的话术应如何避免混淆？ | Not executed |
| 15 | 品牌 | 请给出有来源依据的品牌差异化介绍。 | Not executed |
| 16 | 产品 | 连单和微信回复中出现了哪些产品/品类？ | Not executed |
| 17 | 产品 | 客户询问某产品时，标准卖点是什么？ | Not executed |
| 18 | 产品 | 哪些产品信息在 2023 和 2024 的资料中均有出现？ | Not executed |
| 19 | 产品 | 哪些产品问题资料不足，必须转人工确认？ | Not executed |
| 20 | 产品 | 请按资料原意说明产品搭配或使用建议。 | Not executed |
| 21 | 销售话术 | 面对价格异议时，资料中有哪些可复用的回复？ | Not executed |
| 22 | 销售话术 | 面对“适不适合我”的咨询，应如何按资料回复？ | Not executed |
| 23 | 销售话术 | 面对售后、发货或库存问题，应如何回复且不超出资料？ | Not executed |
| 24 | 销售话术 | 请生成一条基于 2024 微信回复的首次跟进话术，并给出引用。 | Not executed |
| 25 | 销售话术 | 请生成一条连单后的加购/复购建议，并标明其来源记录。 | Not executed |

## 6. Required remediation and rerun procedure

1. **Provide the three original files** in an approved import location; preserve
   filenames, source version, sheet names, and any row identifiers.
2. **Add format support before upload testing:** parse DOCX paragraphs/tables and
   XLS workbooks/sheets into normalized text records while retaining source
   locations (document section or spreadsheet/sheet/row). Add positive and
   negative automated tests for each format.
3. **Deploy/configure the live dependencies:** a configured embedding profile and
   reachable embedding endpoint, Qdrant, the memory API, and the index worker.
4. **Run the evidence chain per source:** receive upload → create/retrieve index
   job → verify completed status and chunk count → verify embedding profile and
   vector dimension → inspect Qdrant collection/point count → run all 25
   queries using authorized owner claims.
5. **Record citations in the rerun report:** for each answer include the source
   filename, page/section or sheet/row, memory ID, chunk ID, retrieval score,
   and answer verdict (pass/fail). Redact customer personal data from the report.
6. **Accept only when all six checkpoints pass for all three files** and every
   answer has a traceable citation. Any unsupported claim, missing citation, or
   cross-owner retrieval is a failed question.

## 7. Final conclusion

M3 Enterprise Memory cannot be business-validated with the materials currently
available in this workspace. The code-level Phase 1B contracts are passing, but
the supplied source files are absent, a live runtime is unavailable, and the
current extraction layer rejects all three requested document formats. This
report therefore records a truthful **blocked** result rather than simulating
uploads, embeddings, Qdrant writes, retrievals, or citations.
