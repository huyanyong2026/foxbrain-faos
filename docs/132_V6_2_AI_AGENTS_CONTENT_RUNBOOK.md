# FoxBrain V6.2 AI Agents + Content Center Runbook

## Goal

V6.2 adds a unified AI agent and content operation foundation without replacing the existing portal, SAP sync, knowledge center, or login system.

## Main Pages

- `/agents` or `/ai-agents`: AI agent center.
- `/ai-tasks`: AI task center.
- `/content`: content draft and publishing preparation center.
- `/logs`: system and operation log center, boss/admin only.
- `/permissions`: role permission overview, boss/admin only.

## Data Tables

- `ai_agents`: standard agent catalog.
- `ai_agent_runs`: traceable AI run records.
- `ai_tasks`: AI task center records.
- `content_posts`: unified content draft archive.
- `system_logs`: unified system log table.

## APIs

- `GET /api/agents/v6.2`
- `GET /api/agents/list`
- `POST /api/agents/run`
- `GET /api/agents/runs`
- `GET /api/agents/ai-tasks`
- `POST /api/agents/ai-tasks`
- `GET /api/agents/logs`

## Safety Rules

- AI does not write back to SAP.
- SAP data remains read-only and syncs at 22:00 daily.
- Price, contract, finance, external publishing, and mass notification actions require human approval.
- AI outputs must show limits when real data or knowledge evidence is missing.
- All important AI actions should be logged through `system_logs` and `activity_log`.

## Verification

1. Open `/api/health` and confirm V6.2 statuses are ready.
2. Open `/agents` on mobile and desktop.
3. Run one AI question through `/api/agents/run`.
4. Confirm the run appears in `/api/agents/runs`.
5. Confirm the generated task appears in `/api/agents/ai-tasks`.
6. Confirm admin can open `/logs` and `/permissions`.
