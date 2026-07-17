# Gateway Legacy Audit

Version: Genesis-Construction-003-1

| Area | Status | Classification | Action |
| --- | --- | --- | --- |
| Old product/portal branding on Gateway | Replaced with VAFOX Identity Center / Welcome Home language | MIGRATE | Keep only identity-center brand copy. |
| Manual application menu | Reframed as automatic role routing | MIGRATE | Do not expose a launcher experience after login. |
| Legacy login pages in downstream apps | Still exist for app-local compatibility | MIGRATE | Move toward Gateway session trust while preserving existing auth until cutover. |
| Duplicate identity services | Explorer identity remains separate for public Explorer flow | KEEP | Connect to VID governance before expanding privileges. |
| SAP/Core data chain | Existing boundary preserved | KEEP | Gateway must read through approved Core/public contracts only. |
| Old portals | Historical portal docs remain | ARCHIVE | Keep as implementation history, not Gateway identity UX. |
| Old authentication implementation | App-local login remains in downstream apps | MIGRATE | Phase into VID-resolved SSO/session validation. |
| Unsafe direct private data exposure | Not found in Gateway static page | KEEP | Continue no private data exposure. |
