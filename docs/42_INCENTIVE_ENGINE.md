# 42 Incentive Engine

## Goal

Incentive Engine prepares editable salary and bonus plan structures.

## Model

`hr_incentive_plans`

- Plan name and type
- Store and employee scope
- Date range
- Rule description
- Calculation method
- Sales and gross profit targets
- Margin target
- Bonus pool rate
- Individual and team weights
- Break-even incentive fields

## Break-even Template

After a store reaches break-even:

- Base salary stays unchanged.
- Incremental gross profit can enter an incentive pool.
- Example discussion structure:
  - 30% of incremental gross profit as incentive pool
  - 20% allocated by individual contribution
  - 10% allocated by team contribution

These are editable defaults, not final company rules.

## Safety

The calculator is a scenario tool. It must not be treated as payroll instruction until reviewed and approved.
