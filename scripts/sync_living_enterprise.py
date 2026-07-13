"""Build Life Objects from confirmed local FoxBrain sources. Never connects to SAP."""

import argparse
import json
import os
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from foxbrain_os.living_enterprise import (  # noqa: E402
    ensure_living_enterprise_schema,
    living_enterprise_summary,
    sync_life_objects_from_confirmed_sources,
)


def main():
    parser = argparse.ArgumentParser(description="Sync evidence-backed Life Objects from confirmed local sources")
    parser.add_argument(
        "--db",
        default=str(Path(os.environ.get("APP_DIR", "/opt/firefox-portal")) / "portal.db"),
        help="FoxBrain SQLite database path",
    )
    parser.add_argument("--publish", action="store_true", help="Commit local Life Object changes")
    args = parser.parse_args()

    database = Path(args.db).expanduser().resolve()
    if not database.exists():
        raise SystemExit("Database not found: {}".format(database))
    conn = sqlite3.connect(str(database))
    conn.row_factory = sqlite3.Row
    try:
        ensure_living_enterprise_schema(conn)
        result = sync_life_objects_from_confirmed_sources(conn)
        summary = living_enterprise_summary(conn)
        if args.publish:
            conn.commit()
        else:
            conn.rollback()
        print(json.dumps({
            "ok": True,
            "mode": "publish" if args.publish else "dry_run",
            "database": str(database),
            "sap_connection": False,
            "result": result,
            "summary": summary,
        }, ensure_ascii=False, indent=2))
    finally:
        conn.close()


if __name__ == "__main__":
    main()
