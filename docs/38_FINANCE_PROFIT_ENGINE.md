# 38 Finance Profit Engine

## Goal

Finance Profit Engine helps the owner review profit, expense, cashflow and financial risk without inventing financial data.

## Pages

- `/finance`
- `/finance/store-profit`
- `/finance/brand-profit`

## Models

### `finance_profit_records`

Tracks profit by company, store, brand, product, supplier or campaign.

### `finance_expenses`

Tracks manual or synchronized expense records.

### `finance_rebates`

Tracks expected, confirmed and received supplier rebates.

## Decision Areas

- Company profit
- Store profit
- Brand profit
- Product profit
- Expense analysis
- Cashflow watch
- Rebate analysis
- Discount impact
- Break-even calculation

## Safety

Finance V1 shows empty states when real SAP/accounting data is not available. It must not invent balances, margins, rebate amounts or profit conclusions.
