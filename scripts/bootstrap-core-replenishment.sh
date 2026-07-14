#!/usr/bin/env bash
set -euo pipefail

ENV_FILE=/opt/foxbrain-core/api/core-api.env
API_APP=/opt/foxbrain-core/api/app.py
PYTHON=/opt/foxbrain-core/sync/venv/bin/python
TOKEN_HANDOFF=/opt/foxbrain-core/api/ai-replenishment.token

if [[ $(id -u) -ne 0 ]]; then
  echo "ERROR: run as root"
  exit 1
fi
if [[ ! -f "$ENV_FILE" || ! -x "$PYTHON" ]]; then
  echo "ERROR: Core API installation was not found"
  exit 1
fi

cp -a "$ENV_FILE" "${ENV_FILE}.bak.$(date +%Y%m%d%H%M%S)"
cp -a "$API_APP" "${API_APP}.bak.$(date +%Y%m%d%H%M%S)"

"$PYTHON" - "$ENV_FILE" "$TOKEN_HANDOFF" <<'PY'
import json
import os
import secrets
import sys
from pathlib import Path

import pytds

env_path = Path(sys.argv[1])
handoff_path = Path(sys.argv[2])
lines = env_path.read_text(encoding="utf-8").splitlines()
env = {}
for line in lines:
    if line and not line.lstrip().startswith("#") and "=" in line:
        key, value = line.split("=", 1)
        env[key.strip()] = value

required = ["CORE_DB_HOST", "CORE_DB_NAME", "CORE_DB_USER", "CORE_DB_PASSWORD"]
missing = [key for key in required if not env.get(key)]
if missing:
    raise SystemExit("ERROR: missing Core settings: " + ", ".join(missing))

connection = pytds.connect(
    server=env["CORE_DB_HOST"],
    port=int(env.get("CORE_DB_PORT", "11433")),
    database=env["CORE_DB_NAME"],
    user=env["CORE_DB_USER"],
    password=env["CORE_DB_PASSWORD"],
    timeout=15,
)
try:
    cursor = connection.cursor()
    cursor.execute("select WhsCode, WhsName from dbo.OWHS order by WhsCode")
    warehouses = [(str(code).strip(), str(name or "").strip()) for code, name in cursor.fetchall()]
finally:
    connection.close()

targets = [
    ("nanshan", "南山店", "南山"),
    ("hangyuan", "航苑店", "航苑"),
    ("zhenxing", "振兴店", "振兴"),
]
mapping = {}
for store_code, store_name, marker in targets:
    exact = [(code, name) for code, name in warehouses if name.replace(" ", "") == store_name]
    candidates = exact or [(code, name) for code, name in warehouses if marker in name.replace(" ", "")]
    if len(candidates) != 1:
        visible = ", ".join(f"{code}:{name}" for code, name in candidates) or "none"
        raise SystemExit(f"ERROR: warehouse match for {store_name} is not unique: {visible}")
    warehouse_code, _warehouse_name = candidates[0]
    mapping[warehouse_code] = {"store_code": store_code, "store_name": store_name}

token_file_value = env.get("CORE_API_TOKENS_FILE")
if not token_file_value:
    raise SystemExit("ERROR: CORE_API_TOKENS_FILE is not configured")
token_path = Path(token_file_value)
token_config = json.loads(token_path.read_text(encoding="utf-8"))
selected_token = ""
for config in token_config.values():
    if "facts:read" in config.get("scopes", []) and config.get("token"):
        selected_token = str(config["token"])
        break
if not selected_token:
    selected_token = secrets.token_urlsafe(48)
    token_config["ai-replenishment"] = {"token": selected_token, "scopes": ["facts:read"]}
    token_path.write_text(json.dumps(token_config, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    token_path.chmod(0o600)

updates = {
    "CORE_STORE_MAP_JSON": json.dumps(mapping, ensure_ascii=False, separators=(",", ":")),
    "CORE_TIMEZONE": "Asia/Shanghai",
}
kept = [line for line in lines if line.split("=", 1)[0].strip() not in updates]
env_path.write_text("\n".join(kept + [f"{key}={value}" for key, value in updates.items()]) + "\n", encoding="utf-8")
env_path.chmod(0o600)
handoff_path.write_text(selected_token + "\n", encoding="utf-8")
handoff_path.chmod(0o600)

print("WAREHOUSE_MAPPING=" + json.dumps(mapping, ensure_ascii=False, separators=(",", ":")))
print("TOKEN_STATUS=ready")
PY

curl -fsSL \
  https://raw.githubusercontent.com/huyanyong2026/foxbrain-faos/main/apps/core_api/app.py \
  -o "${API_APP}.new"
"$PYTHON" -m py_compile "${API_APP}.new"
install -m 0644 "${API_APP}.new" "$API_APP"
rm -f "${API_APP}.new"

systemctl restart foxbrain-core-api.service

for _attempt in $(seq 1 15); do
  if curl -fsS http://127.0.0.1:8090/healthz >/dev/null; then
    break
  fi
  sleep 1
done

"$PYTHON" - "$TOKEN_HANDOFF" <<'PY'
import json
import sys
import urllib.request
from collections import Counter
from pathlib import Path

token = Path(sys.argv[1]).read_text(encoding="utf-8").strip()
request = urllib.request.Request(
    "http://127.0.0.1:8090/api/v1/replenishment/input",
    headers={"Authorization": "Bearer " + token},
)
with urllib.request.urlopen(request, timeout=60) as response:
    payload = json.load(response)
counts = Counter(item["store_name"] for item in payload.get("items", []))
expected = {"南山店", "航苑店", "振兴店"}
if not expected.issubset(counts):
    raise SystemExit("ERROR: real-data response is missing one or more stores")
print("CORE_REAL_DATA_TEST=passed")
print("BUSINESS_DATE=" + str(payload.get("business_date", "")))
for store in ("南山店", "航苑店", "振兴店"):
    print(f"{store}_SKU_ROWS={counts[store]}")
PY

echo "CORE_REPLENISHMENT_BOOTSTRAP=complete"
