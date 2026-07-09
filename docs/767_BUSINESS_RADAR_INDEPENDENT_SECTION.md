# Business Radar Independent Section

## Rule

Business Radar is an independent section. The home page only shows an entry link and must not expand radar metrics, insight cards, evidence or action lists.

## Routes

- Page: `/business-radar`
- API: `/api/business-radar`
- Home policy API: `/api/business-radar/home-policy`

## Home Page Policy

- Show the Business Radar entry only when the user has boss, admin, finance or purchasing permission.
- Do not show yesterday sales, month sales, gross profit, inventory risk or AI insight cards on the home page.
- Do not duplicate Business Radar content into the first screen.
- Users click into `/business-radar` to see operating metrics, insights, actions and evidence.

## Architecture

Business Radar now has its own payload method, `business_radar_payload`, so the page and API use one internal contract. This keeps the module independent from the minimal home page.
