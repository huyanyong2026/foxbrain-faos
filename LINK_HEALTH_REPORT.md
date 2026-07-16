# Huyan V5 Link Health Report

Version: HUYAN-V5-MIGRATION-V1

## Scope

Audited production-facing domains and in-repo navigation references for the Huyan V5 migration:

- `https://gateway.vafox.com`
- `https://huyan.vafox.com`
- `https://ai.vafox.com`
- `https://core.vafox.com`

## Route Decisions

| Domain | V5 status | Action |
| --- | --- | --- |
| `gateway.vafox.com` | Healthy | Keeps role-based entry and points CEO users to Huyan Command Center. |
| `huyan.vafox.com` | Healthy | Root experience is now the CEO Today Center / Autonomous Command Center. |
| `ai.vafox.com` | Healthy | Remains AI Workspace for employees and technical/admin AI work. |
| `core.vafox.com` | Healthy | Remains Core Enterprise Digital Twin data layer. |

## Removed From Main CEO Navigation

- 今天 / old Today dashboard wording
- 企业资料
- 系统
- Technical information
- Manual report pages

These entries are now consolidated under `/admin` for authorized administrators.

## Deprecated Routes

No hard broken links were found in the Huyan V5 templates touched by this migration. Legacy admin destinations remain reachable only through `/admin` so CEO navigation no longer exposes old manual dashboard behavior.

## Link Health Result

PASS — Huyan V5 navigation contains no known broken links or deprecated CEO-facing manual report routes.
