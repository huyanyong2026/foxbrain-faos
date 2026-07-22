# FoxBrain Core Release Report

## Release metadata

- **Deployment version:** `v1.0.0-core-release`
- **Tag:** `v1.0.0-core-release`
- **Commit:** the commit resolved by `git rev-list -n 1 v1.0.0-core-release`.
  The annotated release tag is the immutable source-of-truth for the final
  release commit.
- **Scope:** Core Data API v2.0, five governed business domains, Evidence
  Layer, RBAC/data scope, and the SAP read-only boundary.

## Canonical runtime source inventory

The production source is synchronized from these canonical repository paths;
there is no separate, untracked `ai-runtime/` copy.

| Component | Canonical source |
| --- | --- |
| Core API v2.0 | `apps/core_api/app.py` |
| Sales Domain Adapter | `apps/core_api/sales_adapter.py` |
| Evidence Adapter | `services/runtime/app.py` (`CoreEvidenceAdapter`) |
| WeCom Runtime Adapter | `services/runtime/app.py` (`RuntimeRouter`) |

The Core deployment workflow stages `sales_adapter.py` with `app.py` and
`__init__.py`, then checks all three files before installing them. This keeps
the production Core API import graph synchronized with the Git release.

## Validation performed

| Check | Result |
| --- | --- |
| Core API, RBAC, Sales Domain, Evidence, and WeCom Runtime tests | 20 passed |
| Repository structure tests | 6 passed |
| Workflow script validation | passed (4 SSH actions / 4 script blocks) |
| Python compilation for Core API and Runtime | passed |
| Sensitive-file review | passed; tracked environment files are examples/templates only |

## Deployment boundary

The release remains read-only for SAP: Core reads the SAP Mirror projection,
and the runtime only turns evidence envelopes into cited responses. It does
not establish a SAP production credential or write path.
