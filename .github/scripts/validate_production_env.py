import sys
from pathlib import Path

env_path = Path(sys.argv[1] if len(sys.argv) > 1 else ".env")
required_secret_names = (
    "CORE_API_TOKEN",
    "PORTAL_INITIAL_ADMIN_PASSWORD",
    "ADMIN_PASSWORD",
    "POSTGRES_PASSWORD",
    "DATABASE_URL",
    "MINIO_ROOT_PASSWORD",
    "JWT_SECRET",
    "ENCRYPTION_KEY",
)
placeholder_fragments = ("change_me", "changeme", "replace_me")
values = {}

for raw_line in env_path.read_text(encoding="utf-8").splitlines():
    line = raw_line.strip()
    if not line or line.startswith("#") or "=" not in line:
        continue
    name, value = line.split("=", 1)
    values[name.strip()] = value.strip().strip("'\"")

missing = []
placeholders = []
for name in required_secret_names:
    value = values.get(name, "")
    if not value:
        missing.append(name)
        continue
    lowered = value.lower()
    if any(fragment in lowered for fragment in placeholder_fragments):
        placeholders.append(name)

if missing or placeholders:
    for name in missing:
        print(f"::error title=Missing production env value::{name} must be populated in the server-managed .env file.", file=sys.stderr)
    for name in placeholders:
        print(f"::error title=Placeholder production env value::{name} still contains a placeholder in the server-managed .env file.", file=sys.stderr)
    print("Production deployment cannot continue until the production server .env contains real production secret values.", file=sys.stderr)
    sys.exit(1)

print("Production server .env contains the required non-placeholder secret values.")
