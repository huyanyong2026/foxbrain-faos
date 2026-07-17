# VAFOX Gateway Architecture

Version: Genesis-Construction-003-1

## Mission

`gateway.vafox.com` is the VAFOX Identity Center: the front door of VAFOX Outdoor LIFE.

It is not a portal, dashboard, or application launcher. It verifies identity, resolves VID, recognizes roles, loads context, and routes the person home automatically.

## Preserved Core Chain

Gateway does not modify SAP, bypass Core, create duplicate identity systems, or expose private business data. SAP, Enterprise Data Hub, Enterprise Digital Twin, FoxBrain Intelligence Engine, Memory, Workflow, and Permission remain the capability layer.

## Login Experience

Mobile-first flow:

1. 🔥 VAFOX Outdoor LIFE / 欢迎回家
2. Login
3. Identity verification
4. VID resolution
5. Role recognition
6. Context loading
7. Automatic routing

No manual system selection is presented.

## Routing Rules

- Founder / CEO → `https://huyan.vafox.com`
- Employee → `https://ai.vafox.com`
- Administrator → `https://core.vafox.com`
- Reserved: Customer Home, Supplier Home, Brand Home, Club Home

## Identity Context

Gateway context contains:

- Who am I?
- My roles
- My relationships
- My growth stage
- My permissions
- My current mission context

This prepares downstream AI Router, Mission Engine, and Memory calls.

## Security Controls

- Short-lived signed session token.
- Server-side permission validation.
- Audit logging requirement for login, context, routing, and permission decisions.
- No SAP data, private business data, or internal configuration exposed to public pages.

## Brand System

Use:

- 🔥 火狐狸 VAFOX
- VAFOX Outdoor LIFE
- On the way · 一路有你
- Footer: Powered by FoxBrain Intelligence Engine
