# Task088 VAFOX OS UX 2.0 Information Architecture

## Objective

Implement the 7.8 private AI upgrade suggestion as VAFOX OS UX 2.0, focused on Apple Experience Edition information architecture.

## Scope

- Keep the home page minimal.
- Use four first-layer entries: Business, AI, Messages and Me.
- Move content hierarchy to click-through pages.
- Keep one page one subject.
- Limit each layer to eight entries or fewer.
- Remove explanatory small text from the home page.
- Add fixed global search and AI access.
- Add mobile bottom navigation.
- Keep existing Enterprise V1.0 to V2.3 capabilities compatible.

## Delivered

- `foxbrain_os/ux_information_architecture.py`
- `/api/ux`
- `/api/ux/information-architecture`
- `/api/ux/v2`
- `/os/business`
- `/os/ai`
- `/os/messages`
- `/os/me`
- `/os/search`

## Acceptance Tests

- The UX module imports successfully.
- The contract version is `VAFOX OS UX 2.0`.
- The first layer has exactly four entries.
- The home page block links to the four first-layer routes.
- Advanced pages are not expanded in the final home page block.
- The final home page block does not include explanatory small text.
- Logged-in layout includes global search, fixed AI and mobile bottom navigation.
- Documentation contains the Apple Experience Edition rules.
