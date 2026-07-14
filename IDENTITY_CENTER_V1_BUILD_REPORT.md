# VAFOX Identity Center V1.0 Build Report

## Architecture

The Identity Center is the authentication and authorization boundary for `ai.vafox.com`.

```text
Real employee identity
  -> organization and position
  -> RBAC function permissions
  -> company/store/self data scope
  -> inherited AI permission snapshot
  -> Core API read-only facts
```

Applications do not receive SAP production credentials. Enterprise facts are read from `core.vafox.com` through the authenticated Core API.

## Data Model

- `identity_org_units`: company, department, and store hierarchy.
- `identity_positions`: position and default-role definitions.
- `identity_profiles`: real name, employee number, mobile, WeCom ID, department, store, and position.
- `identity_roles`, `identity_permissions`, `identity_role_permissions`: RBAC catalog.
- `identity_user_roles`, `identity_data_scopes`: user assignment and data boundaries.
- `identity_login_audit`: successful, failed, disabled, and logout events.
- `identity_permission_audit`: denied and privileged identity-management actions.
- `identity_wecom_sso_states`: short-lived WeCom SSO state contract.

Existing `auth_users` accounts remain valid. They receive a compatibility profile marked `pending` verification; existing passwords are not reset. Newly created employees require a verified real name, unique employee number, strong temporary password, and mandatory first-login password change.

## Permission Model

- CEO: company-wide access, CEO Vault, identity administration, and all AI assistants.
- Management: company operating, brand, store, inventory, approval, and identity-view permissions.
- Store manager: only the assigned store's sales, inventory, replenishment, and employee-growth context.
- Purchaser: products, inventory, sales trends, purchasing, and replenishment analysis.
- Employee: product and brand knowledge, guide assistant, and training.
- Identity administrator: identity creation, role assignment, account disablement, and audit.

Every AI run stores the user's role and effective data-scope snapshot. A store manager cannot submit another store ID; the server replaces a missing store with the assigned store and rejects a different store.

## User Experience

- Login accepts a unique real name, employee number, mobile, WeCom ID, or legacy username.
- The administrator can create users, assign roles, bind stores, disable accounts, and inspect recent audits.
- Login and identity pages are Chinese and do not display database or API implementation details.
- WeCom SSO status, start, and callback contracts are reserved. They stay disabled until approved enterprise credentials are configured.

## Security Check

- Passwords use bcrypt with cost 12 for new and changed passwords.
- Session is cleared before login to prevent session fixation.
- Cookies remain Secure, HttpOnly, and SameSite=Lax.
- CSRF protection remains required for all mutating browser actions.
- Shared/default passwords are not added.
- Failed login, disabled-account login, logout, permission denial, role change, user creation, and account status changes are audited.
- AI permissions inherit the signed-in user's RBAC and data scope.
- No SAP hostname, credential, driver, write statement, or write permission was added.

## Tests

- Identity schema coverage.
- CEO, management, store manager, purchaser, and employee role definitions.
- CEO wildcard authorization.
- Store-manager own-store enforcement and cross-store denial.
- Employee inventory-agent denial.
- Purchaser inventory permission boundaries.
- Identity administration, login audit, mandatory password change, and WeCom route contracts.
- Chinese real-identity login and administration pages.
- Existing Enterprise AI platform regression tests.

## Next Step

1. Have the CEO or identity administrator verify legacy user profiles and replace compatibility identifiers with real employee numbers.
2. Configure approved WeCom application credentials in server environment variables and complete OAuth identity exchange.
3. Add supplier, explorer, and leader profile tables using the same identity, role, audit, and data-scope contracts.
4. Deploy only after a production database backup and a named administrator account are confirmed.
