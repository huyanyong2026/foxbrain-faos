# Enterprise Pack 12 - SDK Marketplace

## Goal

Pack 12 evolves VAFOX OS from a fixed application into an extensible enterprise platform.
New capabilities should prefer plugin design, while the core login, permission, audit, SAP,
knowledge, automation and AI agent framework stays stable.

## Platform Principles

- Keep the core stable and add business capabilities through plugins when possible.
- Every extension must declare its manifest, version, permissions and lifecycle.
- Extension APIs are versioned and backward compatible within the same major version.
- High-risk actions such as price, contract, finance, HR and external publishing require human approval.
- All extension activity must pass RBAC, audit logging and data governance rules.

## SDK Framework

The SDK framework exposes:

- `/api/sdk/framework`
- `/api/sdk/manifest-schema`
- `/api/sdk/extension-points`
- `/api/sdk/versioning`
- `/api/sdk/backward-compatibility`

The plugin manifest uses semantic versioning and declares entrypoints, permissions,
compatibility, dependencies, settings schema, approval policy and audit events.

## Extension APIs

The extension API contract covers:

- Authentication
- Knowledge
- SAP integration
- Workflow
- Notifications
- AI tools
- Dashboard components

All extension calls must preserve source traceability and permission checks before an AI
agent or workflow can use the result.

## Marketplace

Marketplace categories:

- AI Agents
- Dashboards
- Reports
- Workflow Packs
- SAP Extensions
- Knowledge Connectors

Boss and admin roles may install plugins. High-risk plugins require manual review before
activation.

## Module Lifecycle

Lifecycle:

```text
draft -> develop -> test -> review -> release -> monitor -> upgrade -> retire
```

Each step must retain approval and audit evidence.

## Backward Compatibility

- Minor and patch versions must not remove existing fields.
- New fields should be optional.
- Breaking changes require a major version.
- Deprecated APIs require a migration note and adapter plan.
- Contract tests are required before release.

## Current Delivery

- Added SDK, extension and marketplace API contracts.
- Added SDK Marketplace to the platform module registry.
- Added health checks for SDK, marketplace and compatibility status.
- Added docs and smoke-test coverage.
