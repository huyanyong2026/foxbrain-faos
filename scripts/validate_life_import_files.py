#!/usr/bin/env python3
"""Validate real SAP export files in an isolated temporary database."""

import argparse
from collections import Counter
import json
import sqlite3
import tempfile
from pathlib import Path

from foxbrain_os.life_import import import_batch_detail, stage_import_bytes


FILE_TYPES = {
    "supplier": "supplier_life",
    "product": "product_life",
    "people": "people_life",
}


def main():
    parser = argparse.ArgumentParser(description="Validate SAP exports without writing SAP or production data")
    parser.add_argument("--supplier", required=True, type=Path)
    parser.add_argument("--product", required=True, type=Path)
    parser.add_argument("--people", required=True, type=Path)
    parser.add_argument("--source-time", default="")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    results = []
    with tempfile.TemporaryDirectory(prefix="foxbrain-life-import-") as temp_name:
        temp = Path(temp_name)
        conn = sqlite3.connect(temp / "validation.db")
        conn.row_factory = sqlite3.Row
        try:
            for key in ("supplier", "product", "people"):
                path = getattr(args, key)
                data = path.read_bytes()
                staged = stage_import_bytes(
                    conn, data, path.name, FILE_TYPES[key], temp / "files", 0, args.source_time
                )
                detail = import_batch_detail(conn, staged["batch"]["batch_id"], row_limit=0)
                batch = detail["batch"]
                issue_counts = Counter()
                for validation_row in conn.execute(
                    "select validation_json from life_import_rows where batch_id=?",
                    (batch["batch_id"],),
                ):
                    issue_counts.update(item["code"] for item in json.loads(validation_row[0] or "[]"))
                results.append({
                    "file": path.name,
                    "object_type": FILE_TYPES[key],
                    "file_format": batch["file_format"],
                    "file_size": batch["file_size"],
                    "file_hash": batch["file_hash"],
                    "row_count": batch["row_count"],
                    "valid_count": batch["valid_count"],
                    "warning_count": batch["warning_count"],
                    "error_count": batch["error_count"],
                    "mapping": batch["mapping"],
                    "issue_counts": dict(sorted(issue_counts.items())),
                    "status": batch["status"],
                    "production_write": False,
                    "sap_write": False,
                })
            conn.rollback()
        finally:
            conn.close()

    payload = {
        "ok": all(item["error_count"] == 0 for item in results),
        "mode": "isolated_validation_only",
        "manual_confirmation_required": True,
        "production_write": False,
        "sap_write": False,
        "files": results,
    }
    output = json.dumps(payload, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output + "\n", encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
