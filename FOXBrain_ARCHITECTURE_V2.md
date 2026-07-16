# VAFOX Foundation V2.0 Architecture

VAFOX Foundation V2.0 standardizes the existing platform into an Enterprise Operating System without redesigning business applications or changing SAP B1 workflows.

## Target Domains

| Layer | Domain | Responsibility |
| --- | --- | --- |
| Gateway | `gateway.vafox.com` | Unified authentication, authorization, routing, API security, health routing |
| Huyan | `huyan.vafox.com` | CEO Operating System, command center, briefing, risk radar, decision center |
| AI | `ai.vafox.com` | Digital Workforce Platform, agents, workspace, knowledge, memory |
| Core | `core.vafox.com` | Enterprise Digital Twin, master data, events, business APIs, governance |
| SAP | SAP B1 | Business truth layer and accounting authority |

## Architecture Flow

```text
Users -> gateway.vafox.com -> Identity / Permission / API Gateway
                            -> huyan.vafox.com CEO OS
                            -> ai.vafox.com AI Workforce
huyan + ai -> core.vafox.com Enterprise Digital Twin -> SAP B1 read-only mirror / approved integrations
```

## Non-Negotiable Guardrails

- SAP remains the business truth layer.
- AI must not directly modify SAP.
- Core provides approved business APIs and data governance.
- Existing working services are preserved.
- Foundation changes standardize, harden, automate, and document the current system.
