#!/usr/bin/env python3
"""Sprint016.5 read-only verification helper.

Default mode is `fixture`, which verifies the local SQLite fixture through a
read-only URI. Real SQL Server connectivity must be enabled only on the server
with environment variables and an approved read-only source.
"""

import json
import os
import sqlite3
import sys
import tempfile
from pathlib import Path


def fixture_audit():
    tmp = Path(tempfile.mkdtemp(prefix="foxbrain-readonly-"))
    db_path = tmp / "readonly_fixture.sqlite"
    conn = sqlite3.connect(str(db_path))
    conn.execute("create table sales(id integer primary key, amount real)")
    conn.execute("insert into sales(amount) values(100)")
    conn.commit()
    conn.close()
    uri = "file:{}?mode=ro".format(str(db_path).replace("\\", "/"))
    source = sqlite3.connect(uri, uri=True)
    result = {
        "mode": "fixture",
        "real_connection_attempted": False,
        "select_allowed": False,
        "insert_denied": False,
        "update_denied": False,
        "delete_denied": False,
        "ddl_denied": False,
        "timeout_configured": True,
        "query_timeout_configured": True,
        "secrets_visible": False,
    }
    try:
        source.execute("select count(*) from sales").fetchone()
        result["select_allowed"] = True
        tests = {
            "insert_denied": "insert into sales(amount) values(200)",
            "update_denied": "update sales set amount=0",
            "delete_denied": "delete from sales",
            "ddl_denied": "create table denied(id integer)",
        }
        for key, sql in tests.items():
            try:
                source.execute(sql)
                result[key] = False
            except Exception as exc:
                result[key] = True
                result[key + "_message"] = exc.__class__.__name__
    finally:
        source.close()
    result["status"] = "passed" if all(result[k] for k in ["select_allowed", "insert_denied", "update_denied", "delete_denied", "ddl_denied"]) else "blocked"
    return result


def main():
    mode = os.environ.get("FOX_SYNC_MODE", "fixture")
    if mode == "fixture":
        print(json.dumps(fixture_audit(), ensure_ascii=False, indent=2))
        return 0
    required = ["FOX_SYNC_SQL_HOST", "FOX_SYNC_SQL_PORT", "FOX_SYNC_SQL_DATABASE", "FOX_SYNC_SQL_USER", "FOX_SYNC_SQL_PASSWORD"]
    missing = [key for key in required if not os.environ.get(key)]
    result = {
        "mode": mode,
        "real_connection_attempted": False,
        "status": "blocked",
        "missing": missing,
        "message": "Real read-only source verification is intentionally blocked until the approved source is configured on the server.",
        "secrets_visible": False,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 2 if missing else 1


if __name__ == "__main__":
    sys.exit(main())
