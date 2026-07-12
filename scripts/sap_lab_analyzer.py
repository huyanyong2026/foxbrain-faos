"""Read-only SAP Business One lab inventory and copy-path validator.

The tool never issues DML or DDL against SAP. It builds a local SQLite
checkpoint database and JSON/CSV evidence files from SELECT-only queries.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sqlite3
import time
from pathlib import Path


OBJECT_RULES = {
    "company": {"OADM": "company profile"},
    "store": {"OWHS": "warehouse/store master"},
    "brand": {"OMRC": "manufacturer/brand master"},
    "product": {
        "OITM": "product master",
        "ITM1": "product price list",
        "OITW": "product inventory by warehouse",
    },
    "supplier": {"OCRD": "business partner master (supplier filter)"},
    "customer": {"OCRD": "business partner master (customer filter)"},
    "employee": {"OHEM": "employee master", "OSLP": "sales employee master"},
    "sales": {
        "OINV": "A/R invoice header",
        "INV1": "A/R invoice rows",
        "ORIN": "A/R credit memo header",
        "RIN1": "A/R credit memo rows",
    },
    "purchase": {
        "OPOR": "purchase order header",
        "POR1": "purchase order rows",
        "OPCH": "A/P invoice header",
        "PCH1": "A/P invoice rows",
    },
    "inventory": {
        "OITW": "inventory by warehouse",
        "OIVL": "inventory valuation log",
        "OILM": "inventory log message",
    },
    "finance": {"OJDT": "journal entry header", "JDT1": "journal entry rows"},
    "contract": {"OOAT": "blanket agreement header", "OAT1": "agreement rows"},
}


def quote(name: str) -> str:
    return "[" + str(name).replace("]", "]]" ) + "]"


def classify_table(name: str) -> str:
    for object_type, tables in OBJECT_RULES.items():
        if name in tables:
            return object_type
    if name.startswith("@"):
        return "user_defined"
    if name.startswith(("A", "ADOC")):
        return "audit_or_archive"
    if name.startswith(("O", "NNM", "CINF")):
        return "master_or_header"
    if name and name[-1:].isdigit():
        return "detail_or_child"
    return "system_or_support"


def object_suggestions(table_name: str) -> list[dict]:
    result = []
    for object_type, tables in OBJECT_RULES.items():
        if table_name in tables:
            result.append(
                {
                    "table_name": table_name,
                    "foxbrain_object": object_type,
                    "relationship": tables[table_name],
                    "status": "suggested",
                    "requires_human_confirmation": True,
                }
            )
    return result


def stable_hash(columns: list[str], rows: list[tuple]) -> str:
    digest = hashlib.sha256()
    digest.update(json.dumps(columns, ensure_ascii=False).encode("utf-8"))
    for row in rows:
        digest.update(
            json.dumps(row, ensure_ascii=False, default=str, separators=(",", ":")).encode("utf-8")
        )
    return digest.hexdigest()


def init_state(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path)
    db.execute(
        """create table if not exists table_progress(
        table_name text primary key, status text not null, source_rows integer,
        sampled_rows integer default 0, sample_hash text, attempts integer default 0,
        updated_at integer not null, error text default '')"""
    )
    db.commit()
    return db


def connect(args):
    import pytds

    password = os.environ.get(args.password_env, "")
    if not password:
        raise RuntimeError(f"missing password environment variable: {args.password_env}")
    return pytds.connect(
        args.host,
        port=args.port,
        database=args.database,
        user=args.user,
        password=password,
        timeout=args.timeout,
        autocommit=False,
    )


def read_dictionary(cursor) -> tuple[list[dict], list[dict]]:
    cursor.execute(
        """select s.name,t.name,
        (select sum(p.rows) from sys.partitions p where p.object_id=t.object_id and p.index_id in (0,1))
        from sys.tables t join sys.schemas s on s.schema_id=t.schema_id
        order by s.name,t.name"""
    )
    tables = [
        {
            "schema": row[0],
            "table_name": row[1],
            "row_count": int(row[2] or 0),
            "category": classify_table(row[1]),
        }
        for row in cursor.fetchall()
    ]
    cursor.execute(
        """select s.name,t.name,c.column_id,c.name,ty.name,c.max_length,c.precision,c.scale,c.is_nullable
        from sys.tables t join sys.schemas s on s.schema_id=t.schema_id
        join sys.columns c on c.object_id=t.object_id
        join sys.types ty on ty.user_type_id=c.user_type_id
        order by s.name,t.name,c.column_id"""
    )
    columns = [
        {
            "schema": r[0], "table_name": r[1], "position": int(r[2]),
            "column_name": r[3], "data_type": r[4], "max_length": int(r[5]),
            "precision": int(r[6]), "scale": int(r[7]), "nullable": bool(r[8]),
        }
        for r in cursor.fetchall()
    ]
    return tables, columns


def write_dictionary(output: Path, tables: list[dict], columns: list[dict]) -> None:
    output.mkdir(parents=True, exist_ok=True)
    (output / "sap_business_dictionary.json").write_text(
        json.dumps({"tables": tables, "columns": columns}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    for filename, records in (("sap_tables.csv", tables), ("sap_columns.csv", columns)):
        with (output / filename).open("w", newline="", encoding="utf-8-sig") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(records[0]) if records else [])
            if records:
                writer.writeheader()
                writer.writerows(records)
    suggestions = [item for table in tables for item in object_suggestions(table["table_name"])]
    (output / "foxbrain_object_mapping_suggestions.json").write_text(
        json.dumps(suggestions, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def validate_copy(cursor, state, tables: list[dict], sample_rows: int, max_tables: int) -> dict:
    completed = failed = skipped = 0
    processed_now = 0
    for table in tables:
        name = table["table_name"]
        existing = state.execute(
            "select status,sample_hash from table_progress where table_name=?", (name,)
        ).fetchone()
        if existing and existing[0] == "completed":
            skipped += 1
            continue
        if max_tables and processed_now >= max_tables:
            break
        processed_now += 1
        try:
            cursor.execute(f"select top {int(sample_rows)} * from {quote(table['schema'])}.{quote(name)}")
            columns = [item[0] for item in cursor.description] if cursor.description else []
            rows = cursor.fetchall()
            sample_hash = stable_hash(columns, rows)
            attempts = state.execute(
                "select coalesce(attempts,0) from table_progress where table_name=?", (name,)
            ).fetchone()
            state.execute(
                "insert or replace into table_progress values(?,?,?,?,?,?,?,?)",
                (name, "completed", table["row_count"], len(rows), sample_hash,
                 int(attempts[0] if attempts else 0) + 1, int(time.time()), ""),
            )
            state.commit()
            completed += 1
        except Exception as exc:
            state.execute(
                "insert or replace into table_progress values(?,?,?,?,?,?,?,?)",
                (name, "failed", table["row_count"], 0, "", 1, int(time.time()), str(exc)[:1000]),
            )
            state.commit()
            failed += 1
        finally:
            cursor.connection.rollback()
    total_completed = state.execute(
        "select count(*) from table_progress where status='completed'"
    ).fetchone()[0]
    total_failed = state.execute(
        "select count(*) from table_progress where status='failed'"
    ).fetchone()[0]
    return {
        "processed_this_run": processed_now,
        "completed_this_run": completed,
        "failed_this_run": failed,
        "resumed_skipped": skipped,
        "completed_total": total_completed,
        "failed_total": total_failed,
        "source_table_total": len(tables),
        "full_copy_completed": False,
        "validation_scope": f"metadata + up to {sample_rows} real rows per table",
    }


def verify_completed(cursor, state, tables: list[dict], sample_rows: int) -> dict:
    matched = mismatched = errors = 0
    for table in tables:
        saved = state.execute(
            "select sample_hash from table_progress where table_name=? and status='completed'",
            (table["table_name"],),
        ).fetchone()
        if not saved:
            continue
        try:
            cursor.execute(
                f"select top {int(sample_rows)} * from {quote(table['schema'])}.{quote(table['table_name'])}"
            )
            columns = [item[0] for item in cursor.description] if cursor.description else []
            current = stable_hash(columns, cursor.fetchall())
            if current == saved[0]:
                matched += 1
            else:
                mismatched += 1
        except Exception:
            errors += 1
        finally:
            cursor.connection.rollback()
    return {"hash_matched": matched, "hash_mismatched": mismatched, "hash_errors": errors}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default=os.environ.get("SAP_LAB_HOST", "192.168.10.107"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("SAP_LAB_PORT", "1433")))
    parser.add_argument("--database", default=os.environ.get("SAP_LAB_DATABASE", "2019"))
    parser.add_argument("--user", default=os.environ.get("SAP_LAB_USER", "foxbrain_reference_reader"))
    parser.add_argument("--password-env", default="SAP_LAB_PASSWORD")
    parser.add_argument("--output", type=Path, default=Path("sap-lab-output"))
    parser.add_argument("--sample-rows", type=int, default=3)
    parser.add_argument("--max-tables", type=int, default=0)
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()

    connection = connect(args)
    try:
        cursor = connection.cursor()
        tables, columns = read_dictionary(cursor)
        connection.rollback()
        write_dictionary(args.output, tables, columns)
        state = init_state(args.output / "sap_lab_checkpoint.db")
        result = validate_copy(cursor, state, tables, args.sample_rows, args.max_tables)
        if args.verify:
            result.update(verify_completed(cursor, state, tables, args.sample_rows))
        result.update(
            {
                "database": args.database,
                "dictionary_tables": len(tables),
                "dictionary_columns": len(columns),
                "generated_at": int(time.time()),
            }
        )
        (args.output / "copy_validation_result.json").write_text(
            json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(json.dumps(result, ensure_ascii=False))
        state.close()
    finally:
        connection.rollback()
        connection.close()


if __name__ == "__main__":
    main()
