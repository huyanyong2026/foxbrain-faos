# SAP B1 Sync Notes

This page records the SAP B1 sync design for FoxBrain.

Sensitive values are intentionally omitted. Put real hostnames, database names,
usernames, and passwords in `.env` on the server only.

## Current Design

- Source: SAP B1 SQL Server
- Target: local PostgreSQL snapshot database
- Consumer: FoxBrain portal, Dify, n8n, and AI reporting jobs
- Schedule: daily automatic sync, recommended at 02:00

## Synced Data Areas

- Customers
- Items
- Warehouses
- Salespersons
- Stock by warehouse
- Sales invoices
- Sales invoice lines
- Purchase orders
- Daily sales summary
- Store sales summary

## Security Rules

- Do not commit database passwords, API keys, or server passwords.
- Use a read-only SAP SQL account for production sync.
- Restrict SQL Server access to the approved application server IP only.
- AI answers should always show data update time and data source.

## Recommended Environment Variables

See `.env.example`.
