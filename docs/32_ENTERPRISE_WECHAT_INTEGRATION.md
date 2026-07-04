# 32 Enterprise WeChat Integration

## Goal

Enterprise WeChat integration is reserved for future mobile login, task notifications, daily briefings and employee submission intake.

Task013 prepares the framework but does not hardcode or require credentials.

## Current Status

- `GET /api/wecom/status`
- Status: `placeholder`
- Configuration: environment variables only

## Future Features

- Enterprise WeChat login
- Send task notification
- Send AI CEO daily briefing
- Receive employee submissions
- Group message drafts
- Customer group content handoff

## Security Rules

- Do not commit `corp_id`, `agent_secret`, access tokens or webhook secrets.
- Store credentials in `.env` or server environment variables.
- Do not send messages automatically until the workflow is approved.
- Keep all external-send actions behind audit logs and human approval.

## Suggested Environment Variables

```text
WECOM_CORP_ID=
WECOM_AGENT_ID=
WECOM_AGENT_SECRET=
WECOM_WEBHOOK_URL=
```

These values are intentionally absent from source code.
