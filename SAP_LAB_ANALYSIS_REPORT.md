# FoxBrain SAP Lab Phase 1 Analysis Report

## 1. Safety boundary

- Lab source: `192.168.10.107:1433`, database `2019`.
- Source account: dedicated `foxbrain_reference_reader`.
- Permission audit: `SELECT` allowed; `INSERT`, `UPDATE`, `DELETE`, and DDL rejected.
- The analysis issued SELECT statements only. Checkpoints, dictionaries, and hashes were written locally, never to SAP.
- No production SAP connection, production deployment, or scheduled task was involved.

## 2. Database structure

- SQL Server: 2008 R2 (10.50.1600.1), Data Center Edition.
- SAP company database size: approximately 2,817.81 MB.
- Tables: 2,113.
- Columns: 70,403.
- Estimated rows across base tables: 4,592,174.
- User-defined tables: 57.
- Master/header tables: 577.
- Detail/child tables: 1,101.
- Audit/archive tables: 277.
- System/support tables: 78.

The generated Business Dictionary contains table name, schema, row count,
classification, column order, data type, length, precision, scale, and nullability.
Runtime output is stored under the ignored `sap-lab-output/` directory so that
business metadata is not committed accidentally.

## 3. Core business objects

| FoxBrain object | Main SAP tables | Proposed relationship |
| --- | --- | --- |
| Company | OADM | Company profile |
| Store | OWHS | Warehouse/store master |
| Brand | OMRC | Manufacturer/brand master |
| Product | OITM, ITM1, OITW | Master, price list, warehouse inventory |
| Customer | OCRD | Filter business partners with `CardType='C'` |
| Supplier | OCRD | Filter business partners with `CardType='S'` |
| Employee | OHEM, OSLP | Employee and sales employee masters |
| Sales | OINV, INV1, ORIN, RIN1 | Invoice and credit memo headers/rows |
| Purchase | OPOR, POR1, OPCH, PCH1 | Purchase orders and A/P invoices |
| Inventory | OITW, OIVL, OILM | Balance, valuation, and movement evidence |
| Finance | OJDT, JDT1 | Journal entry header and rows |
| Contract | OOAT, OAT1 | Blanket agreement header and rows |

The analyzer produced 25 relationship suggestions. Every suggestion remains
`suggested` and requires human confirmation; it does not auto-create FoxBrain objects.

## 4. Business validation baseline

- Data period found in A/R invoices: 2024-01-01 through 2024-12-31.
- Non-cancelled A/R invoices: 22,204; gross document total: 37,996,901.40.
- Non-cancelled A/R credit memos: 1,978; gross document total: 3,202,303.73.
- Products: 80,446.
- Product/warehouse records: 965,352.
- Inventory quantity (`OITW.OnHand`): 48,172.
- Indicative inventory value (`OnHand * AvgPrice`): 11,927,016.75.
- Warehouses: 12.
- Customers: 16; suppliers: 112.

Amounts above are SAP Lab reference values, not current production operating
figures. Financial reporting must preserve SAP cancellation, currency, tax,
credit memo, and accounting-period rules before publication.

## 5. Copy-path and checkpoint test

The Phase 1 test validated the read/copy path for all 2,113 tables:

1. Loaded metadata for every table and all 70,403 columns.
2. Read up to two real rows from every table through the read-only account.
3. Serialized each sample and persisted a SHA-256 hash plus local checkpoint.
4. Stopped after an initial 25 tables, then resumed from the checkpoint.
5. A second interruption occurred during the full run; the next run resumed again.
6. Final state: 2,113 completed, 0 failed.
7. Second-pass verification: 2,113 hashes matched, 0 mismatched, 0 read errors.

This proves table discovery, type serialization, checkpoint persistence, resume,
and sample-level validation across all 2,113 tables. It does **not** mean that all
4,592,174 rows have been copied to the Core mirror. Full-row copying remains a
separate controlled phase with storage, duration, key strategy, and reconciliation
approval.

## 6. Implemented files

- `scripts/sap_lab_analyzer.py`: read-only dictionary, classification, checkpoint,
  sample-copy, hash verification, and object mapping tool.
- `tests/test_sap_lab_analyzer.py`: classification, mapping, hash, and checkpoint tests.
- `.gitignore`: excludes local `sap-lab-output/` evidence and checkpoint data.

Generated local evidence:

- `sap_business_dictionary.json`
- `sap_tables.csv`
- `sap_columns.csv`
- `foxbrain_object_mapping_suggestions.json`
- `sap_lab_checkpoint.db`
- `copy_validation_result.json`

## 7. Test results

- Python compile check: passed.
- Unit tests: 3 passed.
- Read-only permission audit: SELECT passed; INSERT/UPDATE/DELETE/DDL rejected.
- Dictionary coverage: 2,113/2,113 tables.
- Copy-path sample coverage: 2,113/2,113 tables.
- Resume test: passed across two interruptions.
- Hash reconciliation: 2,113 matched; 0 mismatched; 0 errors.

## 8. FoxBrain object recommendations

1. Use immutable source identity `database + schema + table + primary key` for SAP evidence.
2. Map OWHS to Store only after warehouse/store alias calibration; not every warehouse is a retail store.
3. Treat OMRC as a brand/manufacturer candidate, then reconcile it with existing FoxBrain Brand objects.
4. Use OITM.ItemCode as the product source key and OITW as inventory evidence, not as a second product.
5. Split OCRD into Customer and Supplier by `CardType`; preserve one source partner identity.
6. Keep OSLP and OHEM distinct until employee identity matching is manually confirmed.
7. Build sales facts from OINV/INV1 and subtract or separately model ORIN/RIN1 with cancellation evidence.
8. Link every generated metric and object relationship to source table, source key, extraction time, and batch ID.
9. Start full-row Lab copying with stable-key core tables before attempting all 2,113 tables.
10. Require row-count plus business-total reconciliation before any Lab procedure is promoted to Enterprise Data Core.

## 9. Next controlled phase

Run a full-row Lab copy for the core object tables first, using keyset checkpoints
where stable keys exist. Reconcile row counts, sales/credit totals, inventory
quantity/value, customer/supplier counts, and warehouse/product counts. Expand to
the remaining tables only after the core batch has zero unexplained differences.
