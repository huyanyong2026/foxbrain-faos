# Migration Guide

## Sprint 3 to Sprint 4

- Move browser API calls behind `@foxbrain/api-client`; configure `NEXT_PUBLIC_API_BASE_URL` for development, test, and production.
- Do not add database hostnames, credentials, or ORM clients to any `apps/*` package.
- Place shared browser types and UI components in `packages/types` and `packages/ui`.
- Existing Python service directories remain deployable during the freeze; service aliases document their target bounded contexts.
