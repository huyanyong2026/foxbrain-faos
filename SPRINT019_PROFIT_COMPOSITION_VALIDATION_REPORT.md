# Sprint019 Profit Composition Validation Report

## Profit Composition Rule

The CEO homepage must not double-count brand rebates. SAP profit is treated as already including rebate values.

## 2026 Reference Values

- SAP profit: 1,723,487.13
- Osprey rebate: 64,798.03
- Kailas rebate: 979,919.75
- Rebate total: 1,044,717.78
- Non-rebate profit: 678,769.35
- Rebate share: approximately 60.6%

## UI Behavior

- Homepage displays SAP profit separately from rebate composition.
- Rebate total is shown as a composition item, not added again.
- Homepage displays the warning: brand rebates are not long-term fixed income; profit quality has dependency risk.

## Evidence

- `business_metrics_snapshots` is used for SAP profit when available.
- Fallback reference values match the Sprint019 acceptance requirement.

