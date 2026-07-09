# Task080 Business Radar Independent Section

## Request

Make Business Radar an independent section. Do not expand it on the home page. Apply the rule internally and externally across the system.

## Implementation

- Kept the home page minimal with only a Business Radar entry link.
- Added `business_radar_payload` as the internal contract.
- Added `/api/business-radar` as the independent data API.
- Added `/api/business-radar/home-policy` to expose the home page rule.
- Added documentation and smoke tests.

## Safety

No database changes. Existing `/business-radar` page remains compatible.
