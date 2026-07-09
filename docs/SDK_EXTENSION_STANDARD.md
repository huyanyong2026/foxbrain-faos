# FoxBrain SDK Extension Standard

## Manifest

Required plugin manifest fields:

- `plugin_id`
- `name`
- `version`
- `sdk_version`
- `category`
- `entrypoints`
- `permissions`
- `compatibility`

Optional fields:

- `description`
- `author`
- `dependencies`
- `settings_schema`
- `approval_policy`
- `audit_events`
- `release_notes`

Secrets must be referenced through environment variables or a future secret vault. They
must never be stored in plugin manifests or source code.

## Permissions

Plugins declare the minimum permission scope they need. Default behavior is deny. The
runtime grants access only when the user role and plugin permission are both allowed.

## Audit

All plugin actions that read sensitive data, write business data, call AI tools, trigger
workflows or change system settings must create audit records.

## Approval

The following actions default to human approval:

- Price and discount changes
- Contract changes
- Finance actions
- HR actions
- External publishing
- SAP writeback
- Customer data export

## Compatibility

FoxBrain SDK uses semantic versioning:

- Major version: breaking changes only.
- Minor version: additive optional capabilities.
- Patch version: bug fixes without contract changes.

Existing plugin contracts must remain valid across minor and patch releases.
