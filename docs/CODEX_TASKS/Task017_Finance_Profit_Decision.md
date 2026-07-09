# Task017 Finance Profit Decision Engine

## Status

Completed locally.

## Delivered

- Finance center upgrade
- Store profit page
- Brand profit page
- Profit record model
- Expense model
- Rebate model
- Cashflow watch placeholder
- Discount impact calculator
- Break-even calculator
- Finance task generation endpoint
- Finance permission checks
- Health check marker

## API

- `GET /api/finance`
- `GET /api/finance/profit`
- `POST /api/finance/profit`
- `GET /api/finance/store-profit`
- `GET /api/finance/brand-profit`
- `GET /api/finance/expenses`
- `POST /api/finance/expenses`
- `GET /api/finance/cashflow`
- `GET /api/finance/rebates`
- `POST /api/finance/rebates`
- `POST /api/finance/discount-calculate`
- `POST /api/finance/break-even-calculate`
- `POST /api/finance/create-task`

## Notes

Financial data remains restricted to owner, admin and finance roles. No real profit or cashflow conclusion is generated without real data.
