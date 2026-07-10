# Sprint016.5 Real Data Reconciliation Report

## Current Status

Real SAP read-only source has not been connected yet. This report records the simulation reconciliation result and the expected real-run report format.

## Simulation Reconciliation

| Domain | Source Count | Staged Count | Accepted | Rejected | Duplicate | Null Key | Status |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| sales | 3 | 3 | 3 | 0 | 0 | 0 | matched |
| inventory | 3 | 3 | 3 | 0 | 0 | 0 | matched |
| products | 4 | 4 | 4 | 0 | 0 | 0 | matched |
| brands | 4 | 4 | 4 | 0 | 0 | 0 | matched |
| stores | 4 | 4 | 4 | 0 | 0 | 0 | matched |

## Sales Totals Required For Real Run

The real dry-run report must include:

- sales rows
- sales amount
- sales quantity
- gross profit when available
- earliest source timestamp
- latest source timestamp
- rejected rows
- duplicate rows
- null-key rows

Any unexplained difference blocks publish.

## Inventory Totals Required For Real Run

The real dry-run report must include:

- inventory rows
- inventory quantity
- inventory retail amount
- inventory cost amount when available
- earliest source timestamp
- latest source timestamp
- rejected rows
- duplicate rows
- null-key rows

Any unexplained difference blocks publish.

## Real Data Status

Not executed. Waiting for approved read-only replica or safe export source.
