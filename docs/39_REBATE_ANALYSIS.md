# 39 Rebate Analysis

## Goal

Rebate Analysis tracks supplier rebate dependency and uncertainty.

## Model

`finance_rebates`

- `rebate_id`
- `supplier_id`
- `brand_id`
- `period`
- `sales_amount`
- `rebate_rate`
- `expected_rebate`
- `actual_rebate`
- `status`
- `uncertainty_level`
- `notes`

## Status

- `expected`
- `confirmed`
- `received`
- `delayed`
- `uncertain`
- `cancelled`

## Osprey

Osprey rebate analysis should show rebate dependency, uncertainty and the impact of discount selling. It must not claim real rebate amounts until confirmed by accounting or supplier documents.
