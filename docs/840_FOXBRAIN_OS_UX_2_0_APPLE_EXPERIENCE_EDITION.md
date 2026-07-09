# FoxBrain OS UX 2.0 Apple Experience Edition

## Goal

FoxBrain OS UX 2.0 makes the portal feel like an operating system instead of an ERP administration backend.

The home page is now only a first-layer entrance. It does not expose deep hierarchy, detailed numbers, repeated business modules or explanatory small text.

## First Layer

The home page keeps four first-layer entries only:

- Business
- AI
- Messages
- Me

The home page must not show explanatory small text under the entry layer.

## Layer Rules

- One page one subject.
- One layer has no more than eight entries.
- Users should find any normal function within three steps.
- Detailed business data appears only after click-through.
- AI is an independent center, similar to a direct ChatGPT-style entrance.
- Global search and the AI entrance stay fixed across logged-in pages.
- Mobile keeps a bottom navigation with Business, AI, Messages and Me.
- Business Radar stays an independent section and is not expanded on the home page.

## Business Layer

Business groups the enterprise objects:

- CEO Dashboard
- Stores
- Employees
- Products
- Brands
- Customers
- Suppliers
- Finance

## AI Layer

AI groups direct intelligence work:

- AI Assistant
- AI Knowledge
- AI Agents
- AI Tasks

## Messages Layer

Messages groups things requiring attention:

- AI Daily Report
- Approvals
- Notifications
- Todos

## Me Layer

Me groups personal and system controls:

- Profile
- Permissions
- Theme
- Settings
- System

## Implementation

The information architecture contract is implemented in `foxbrain_os/ux_information_architecture.py` and exposed through:

- `/api/ux`
- `/api/ux/information-architecture`
- `/api/ux/v2`

The portal home page routes users to:

- `/os/business`
- `/os/ai`
- `/os/messages`
- `/os/me`

The logged-in page shell also exposes:

- `/os/search`
- `/jarvis`

## Acceptance

- The home page shows four entries only.
- The home page does not show explanatory small text.
- No detailed dashboard or advanced module list is expanded on the first screen.
- Logged-in pages include a global search box and a fixed AI entry.
- Mobile pages include the four-entry bottom navigation.
- Existing modules remain available after click-through.
- The UX contract is documented, importable and covered by smoke tests.
