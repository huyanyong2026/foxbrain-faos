# Sprint007 SAP Data Import Foundation Summary

## Scope

Sprint007 adds the SAP Excel/CSV import foundation to the existing huyan.vafox.com FoxBrain FAOS codebase. It is an incremental upgrade on top of Sprint001-006 and does not build ai.vafox.com.

This sprint only imports SAP-exported files uploaded by users. It makes no production SAP connection and does not require any program installed on the SAP production server.

Real SAP field mapping is documented in `docs/SAP_REAL_DATA_IMPORT_MAPPING.md`.

## New Database Tables

- `sap_import_batches`
- `sap_sales`
- `sap_inventory`

The batch table records source document, import type, filename, status, row counts, mapping, creator, and timestamps. Sales and inventory rows retain normalized columns plus `raw_data` JSON for traceability.

## Supported Import Types

- `sales`
- `inventory`
- `employee_sales`
- `brand_sales`
- `category_sales`
- `purchase`

Non-inventory import types currently land in the normalized sales foundation table with original row data preserved in JSON.

## New Pages

- `/sap-import`
- `/data-import`

The page supports direct Excel/CSV upload and importing an existing Drive file as SAP data.

The importer now supports SAP `.xls` files that are actually GB18030/GBK encoded tab-separated text exports.

## API Interfaces

- `POST /api/sap/import`
- `GET /api/sap/import-batches`
- `GET /api/sap/import-batches/:id`
- `GET /api/sap/sales`
- `GET /api/sap/inventory`
- `GET /api/sap/summary`

## Drive Integration

- Drive file detail now includes SAP import batch status in the `sap_import` field.
- Excel/CSV files in the Drive list expose a “导入为 SAP 数据” action.
- Imported files are kept in Drive and linked to `sap_import_batches.document_id`.

## Dashboard Integration

Dashboard integration adds:

- SAP import batch count
- SAP sales row count
- SAP inventory row count
- Recent SAP import batches
- A core entry for SAP data import

## Search Integration

Search integration is included for imported SAP data.

Global Search now supports:

- `sap_batch`
- `sap_sales`
- `sap_inventory`

Search can match imported SAP batch filenames, import types, store names, employee names, brands, categories, product codes, product names, barcodes, and raw row data.

## Safety Boundary

- No direct connection to production SAP.
- No SAP server agent.
- No SAP database writes.
- No automatic business-data modification.
- All imported rows are traceable to a user-uploaded file and import batch.

## Test Results

Executed verification:

- Python syntax check for `portal_v2.py`
- Python syntax check for `tests/v6_smoke_check.py`
- Existing smoke test suite including Sprint001-007 assertions
- Real SAP package parse/import test against `sap数据.zip`

Real SAP import result:

- 10 priority files imported into a local temporary database.
- 10 import batches completed.
- 47,650 sales rows imported.
- 22,556 inventory rows imported.
- 0 failed rows.
- Full report: `SPRINT007_REAL_SAP_IMPORT_TEST_REPORT.md`

## Sprint008 Recommendation

Sprint008 should build on this foundation with import preview, column mapping confirmation, duplicate detection, validation reports, and business-safe approval for promoting imported data into higher-level operating analysis.
