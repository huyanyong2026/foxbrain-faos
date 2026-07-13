# FoxBrain Enterprise AI

`ai.vafox.com` is the enterprise AI collaboration layer. It is separate from the CEO private brain and from the Enterprise Data Core.

## Modules

- AI工作台
- Agent中心
- 企业微信连接
- 知识中心
- 任务中心
- AI反馈学习

## Data boundary

```text
core.vafox.com (read-only facts)
          -> ai.vafox.com (analysis, suggestions, task drafts)
          -> human review
          -> huyan.vafox.com (approved decisions and memory)

Living Enterprise -> object context and evidence
```

Every AI result and task requires evidence. AI results remain pending until a manager, boss or administrator accepts or rejects them. Feedback becomes a learning candidate and requires another human review.

CEO Brain can pull only human-approved AI results through `GET /ops-api/exchange/approved-runs` with the server-side service token. The AI service never pushes an unapproved suggestion into the CEO decision system.

## Existing platform compatibility

The service is designed to replace the existing `vafox-auth` application on port 5010 while preserving the existing `auth_users` table and login sessions. Dify keeps `/api`, `/console` and `/v1`; FoxBrain business APIs use `/ops-api` to avoid route conflicts. Existing WeCom and n8n services remain independent.

## Deployment order

1. Back up `/opt/ai-vafox`, PostgreSQL and Nginx configuration.
2. Copy this directory to a versioned release directory.
3. Put secrets only in the server `.env`.
4. Build the candidate container without stopping production.
5. Run schema initialization and health checks against a staging database.
6. Replace `vafox-auth`, add the Nginx locations, and run `nginx -t`.
7. Verify all six pages, login, CSRF, permissions and human approval.

No component writes SAP or installs anything on an SAP server.
