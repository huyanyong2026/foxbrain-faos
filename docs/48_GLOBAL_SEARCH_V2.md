# 48 Global Search V2

## Goal

Global Search V2 provides one permission-aware search entrance.

## API

- `GET /api/search/global?q=keyword`

## Result Shape

- Type
- Title
- Summary
- Tags
- Updated time
- Open action

## Safety

Sensitive finance, HR, customer and system details must be filtered by permission before display.
