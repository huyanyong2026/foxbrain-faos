"""Read-only SAP B1 full mirror copier with per-table checkpoints."""

from __future__ import annotations

import argparse
import base64
import json
import os
import sqlite3
import time
from pathlib import Path


BASE = Path(os.environ.get("FOXBrain_CORE_BASE", "/opt/foxbrain-core"))
ENV = BASE / "sync/mirror-source.env"
STATE = BASE / "sync/mirror-state.db"
LOG = BASE / "logs/sap-mirror.jsonl"
TARGET_DATABASE = "SAP_MIRROR"
BINARY_TEXT_TABLES = {"OCPC", "OFRM", "OHMM", "OULA"}


def read_env(path=ENV):
    data = {}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            key, value = line.split("=", 1)
            data[key.strip()] = value.strip()
    return data


def log_event(**payload):
    payload["time"] = int(time.time())
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, default=str) + "\n")


def quote(name):
    return "[" + str(name).replace("]", "]]" ) + "]"


def binary_text_expression(column_name, data_type):
    """Read legacy text values without asking the TDS driver to decode them."""
    quoted = quote(column_name)
    normalized_type = data_type.lower()
    if normalized_type == "ntext":
        return f"convert(varbinary(max),convert(nvarchar(max),{quoted})) as {quoted}"
    if normalized_type == "text":
        return f"convert(varbinary(max),convert(varchar(max),{quoted})) as {quoted}"
    return f"convert(varbinary(max),{quoted}) as {quoted}"


def source_projection(columns, table):
    return ",".join(
        binary_text_expression(row[0], row[1])
        if table in BINARY_TEXT_TABLES
        and row[1].lower() in ("char", "varchar", "nchar", "nvarchar", "text", "ntext")
        else quote(row[0])
        for row in columns
    )


def normalize_rows(columns, table, rows):
    import pytds

    binary_types = {"image", "binary", "varbinary", "timestamp", "rowversion"}
    normalized = []
    for row in rows:
        values = []
        for column, value in zip(columns, row):
            if isinstance(value, bytes):
                if column[1].lower() in binary_types or table in BINARY_TEXT_TABLES:
                    value = pytds.Binary(value)
                else:
                    value = "FOX_BINARY_BASE64:" + base64.b64encode(value).decode("ascii")
            values.append(value)
        normalized.append(tuple(values))
    return normalized


def ddl_type(row):
    data_type = row[1].lower()
    size = int(row[2] or 0)
    precision = int(row[3] or 0)
    scale = int(row[4] or 0)
    if data_type in ("varchar", "char", "varbinary", "binary"):
        return f"{data_type}({'max' if size == -1 else max(1, size)})"
    if data_type in ("nvarchar", "nchar"):
        return f"{data_type}({'max' if size == -1 else max(1, size // 2)})"
    if data_type in ("decimal", "numeric"):
        return f"{data_type}({precision},{scale})"
    if data_type in ("timestamp", "rowversion"):
        return "binary(8)"
    return data_type


def init_state(path=STATE):
    path.parent.mkdir(parents=True, exist_ok=True)
    state = sqlite3.connect(path)
    state.execute(
        """create table if not exists progress(
        table_name text primary key,status text,source_rows integer default 0,
        target_rows integer default 0,copied_rows integer default 0,
        updated_at integer,error text)"""
    )
    state.execute(
        """create table if not exists mirror_runs(
        id integer primary key autoincrement,mode text not null,status text not null,
        source_tables integer default 0,completed_tables integer default 0,
        failed_tables integer default 0,started_at integer not null,finished_at integer,error text)"""
    )
    state.commit()
    return state


def source_tables(cursor):
    cursor.execute(
        """select s.name,t.name from sys.tables t join sys.schemas s on s.schema_id=t.schema_id
        order by s.name,t.name"""
    )
    return [(row[0], row[1]) for row in cursor.fetchall()]


def table_columns(cursor, schema, table):
    cursor.execute(
        """select c.name,ty.name,c.max_length,c.precision,c.scale,c.is_nullable,c.is_computed,c.column_id
        from sys.columns c join sys.types ty on ty.user_type_id=c.user_type_id
        where c.object_id=object_id(%s) order by c.column_id""",
        (schema + "." + table,),
    )
    return [row for row in cursor.fetchall() if not row[6]]


def primary_key_columns(cursor, schema, table):
    cursor.execute(
        """select c.name from sys.indexes i
        join sys.index_columns ic on ic.object_id=i.object_id and ic.index_id=i.index_id
        join sys.columns c on c.object_id=ic.object_id and c.column_id=ic.column_id
        where i.object_id=object_id(%s) and i.is_primary_key=1 order by ic.key_ordinal""",
        (schema + "." + table,),
    )
    return [row[0] for row in cursor.fetchall()]


def row_count(cursor, schema, table):
    cursor.execute(f"select count(*) from {quote(schema)}.{quote(table)}")
    return int(cursor.fetchone()[0])


def target_exists(cursor, schema, table):
    cursor.execute("select case when object_id(%s,'U') is null then 0 else 1 end", (schema + "." + table,))
    return bool(cursor.fetchone()[0])


def order_expression(columns, primary_key):
    if primary_key:
        return ",".join(quote(name) for name in primary_key)
    sortable = [row[0] for row in columns if row[1].lower() not in ("image", "text", "ntext", "xml")]
    return ",".join(quote(name) for name in sortable) or "(select 0)"


def keyset_predicate(primary_key, last_values):
    clauses = []
    params = []
    for index, key in enumerate(primary_key):
        prefix = [f"{quote(primary_key[p])}=%s" for p in range(index)]
        clauses.append("(" + " and ".join(prefix + [f"{quote(key)}>%s"]) + ")")
        params.extend(last_values[:index])
        params.append(last_values[index])
    return " or ".join(clauses), params


def row_counts_reconciled(source_end, target_total):
    """Accept rows captured during a live read when the ending counts agree."""
    return target_total == source_end


def missing_keys_in_batch(target_cursor, schema, table, primary_key, source_keys):
    clauses = []
    params = []
    for key_values in source_keys:
        clauses.append("(" + " and ".join(f"{quote(key)}=%s" for key in primary_key) + ")")
        params.extend(key_values)
    projection = ",".join(quote(key) for key in primary_key)
    target_cursor.execute(
        f"select {projection} from {quote(schema)}.{quote(table)} where " + " or ".join(clauses),
        tuple(params),
    )
    existing = {tuple(row) for row in target_cursor.fetchall()}
    return [key for key in source_keys if key not in existing]


def ensure_target_key_index(target_cursor, schema, table, primary_key):
    index_name = "IX_FOX_MIRROR_PK"
    target_cursor.execute(
        "select count(1) from sys.indexes where object_id=object_id(%s) and name=%s",
        (schema + "." + table, index_name),
    )
    if int(target_cursor.fetchone()[0]) == 0:
        keys = ",".join(quote(key) for key in primary_key)
        target_cursor.execute(
            f"create unique nonclustered index {quote(index_name)} on "
            f"{quote(schema)}.{quote(table)}({keys})"
        )
        target_cursor.connection.commit()


def find_missing_primary_keys(source_cursor, target_cursor, schema, table, primary_key):
    ensure_target_key_index(target_cursor, schema, table, primary_key)
    projection = ",".join(quote(key) for key in primary_key)
    target_cursor.execute(
        f"select {projection} from {quote(schema)}.{quote(table)}"
    )
    existing = {tuple(row) for row in target_cursor.fetchall()}
    source_cursor.execute(
        f"select {projection} from {quote(schema)}.{quote(table)} order by {projection}"
    )
    missing = []
    while True:
        rows = source_cursor.fetchmany(5000)
        if not rows:
            break
        missing.extend(tuple(row) for row in rows if tuple(row) not in existing)
    return missing


def insert_missing_primary_keys(
    source_cursor, target_cursor, schema, table, columns, primary_key, missing_keys
):
    if not missing_keys:
        return 0
    names = [row[0] for row in columns]
    projection = source_projection(columns, table)
    inserted = 0
    batch_size = max(1, min(200, 1900 // len(primary_key)))
    for start in range(0, len(missing_keys), batch_size):
        keys = missing_keys[start:start + batch_size]
        clauses = []
        params = []
        for key_values in keys:
            clauses.append("(" + " and ".join(f"{quote(key)}=%s" for key in primary_key) + ")")
            params.extend(key_values)
        source_cursor.execute(
            f"select {projection} from {quote(schema)}.{quote(table)} where "
            + " or ".join(clauses),
            tuple(params),
        )
        rows = normalize_rows(columns, table, source_cursor.fetchall())
        insert_rows(target_cursor, schema, table, names, rows)
        inserted += len(rows)
    target_cursor.connection.commit()
    return inserted


def insert_rows(cursor, schema, table, names, rows):
    if not rows:
        return
    row_width = len(names)
    rows_per_statement = max(1, min(500, 2000 // row_width))
    column_sql = ",".join(quote(name) for name in names)
    for start in range(0, len(rows), rows_per_statement):
        batch = rows[start:start + rows_per_statement]
        values_sql = ",".join(
            "(" + ",".join(["%s"] * row_width) + ")" for _ in batch
        )
        params = tuple(value for row in batch for value in row)
        cursor.execute(
            f"insert into {quote(schema)}.{quote(table)}({column_sql}) values {values_sql}",
            params,
        )


def create_target_table(cursor, schema, table, columns):
    if schema != "dbo":
        cursor.execute(f"if schema_id({repr(schema)}) is null exec('create schema {quote(schema)}')")
    if target_exists(cursor, schema, table):
        cursor.execute(f"drop table {quote(schema)}.{quote(table)}")
    definitions = []
    for row in columns:
        target_type = "varbinary(max)" if table in BINARY_TEXT_TABLES and row[1].lower() in ("char", "varchar", "nchar", "nvarchar", "text", "ntext") else ddl_type(row)
        definitions.append(quote(row[0]) + " " + target_type + (" null" if row[5] else " not null"))
    cursor.execute(f"create table {quote(schema)}.{quote(table)}(" + ",".join(definitions) + ")")


def copy_table(source_cursor, target_cursor, state, schema, table, batch_size):
    source_total = row_count(source_cursor, schema, table)
    progress = state.execute(
        "select status,copied_rows from progress where table_name=?", (schema + "." + table,)
    ).fetchone()
    exists = target_exists(target_cursor, schema, table)
    target_total = 0
    if exists:
        target_total = row_count(target_cursor, schema, table)
        if target_total == source_total:
            state.execute(
                "insert or replace into progress values(?,?,?,?,?,?,?)",
                (schema + "." + table, "completed", source_total, target_total, target_total, int(time.time()), ""),
            )
            state.commit()
            return "completed", source_total, target_total
    columns = table_columns(source_cursor, schema, table)
    if not columns:
        raise RuntimeError("table metadata missing")
    primary_key = primary_key_columns(source_cursor, schema, table)
    binary_rebuild = table in BINARY_TEXT_TABLES and progress and progress[0] == "failed"
    if exists and target_total < source_total and primary_key and not binary_rebuild:
        missing_keys = find_missing_primary_keys(
            source_cursor, target_cursor, schema, table, primary_key
        )
        insert_missing_primary_keys(
            source_cursor, target_cursor, schema, table, columns, primary_key, missing_keys
        )
        target_total = row_count(target_cursor, schema, table)
        source_total = row_count(source_cursor, schema, table)
        if target_total == source_total:
            state.execute(
                "insert or replace into progress values(?,?,?,?,?,?,?)",
                (schema + "." + table, "completed", source_total, target_total, target_total, int(time.time()), ""),
            )
            state.commit()
            return "completed", source_total, target_total
    copied = int(progress[1] or 0) if progress and progress[0] in ("running", "failed") else 0
    if (
        not target_exists(target_cursor, schema, table)
        or row_count(target_cursor, schema, table) != copied
        or binary_rebuild
    ):
        copied = 0
        create_target_table(target_cursor, schema, table, columns)
        target_cursor.connection.commit()
    names = [row[0] for row in columns]
    projection = ",".join(quote(name) for name in names)
    read_projection = source_projection(columns, table)
    ordering = order_expression(columns, primary_key)
    last_values = None
    if primary_key and copied:
        pk_projection = ",".join(quote(name) for name in primary_key)
        target_cursor.execute(
            f"select top 1 {pk_projection} from {quote(schema)}.{quote(table)} order by "
            + ",".join(quote(name) + " desc" for name in primary_key)
        )
        last_values = list(target_cursor.fetchone())
    while copied < source_total:
        if primary_key:
            where_sql = ""
            params = []
            if last_values is not None:
                predicate, params = keyset_predicate(primary_key, last_values)
                where_sql = " where " + predicate
            select_sql = (
                f"select top {int(batch_size)} {read_projection} from {quote(schema)}.{quote(table)}"
                + where_sql + " order by " + ordering
            )
            source_cursor.execute(select_sql, tuple(params))
        else:
            upper = min(source_total, copied + batch_size)
            select_sql = (
                "select " + projection + " from (select " + read_projection + ",row_number() over(order by "
                + ordering + f") as [__fox_row] from {quote(schema)}.{quote(table)}) [fox_page] "
                + f"where [__fox_row]>{copied} and [__fox_row]<={upper} order by [__fox_row]"
            )
            source_cursor.execute(select_sql)
        rows = source_cursor.fetchall()
        if not rows:
            break
        rows = normalize_rows(columns, table, rows)
        insert_rows(target_cursor, schema, table, names, rows)
        target_cursor.connection.commit()
        copied += len(rows)
        if primary_key:
            positions = [names.index(key) for key in primary_key]
            last_values = [rows[-1][position] for position in positions]
        state.execute(
            "insert or replace into progress values(?,?,?,?,?,?,?)",
            (schema + "." + table, "running", source_total, 0, copied, int(time.time()), ""),
        )
        state.commit()
    target_total = row_count(target_cursor, schema, table)
    source_end = row_count(source_cursor, schema, table)
    if primary_key and target_total < source_end:
        missing_keys = find_missing_primary_keys(
            source_cursor, target_cursor, schema, table, primary_key
        )
        insert_missing_primary_keys(
            source_cursor, target_cursor, schema, table, columns, primary_key, missing_keys
        )
        target_total = row_count(target_cursor, schema, table)
        source_end = row_count(source_cursor, schema, table)
    status = "completed" if row_counts_reconciled(source_end, target_total) else "failed"
    error = "" if status == "completed" else f"row_count_mismatch:start={source_total},end={source_end},target={target_total}"
    state.execute(
        "insert or replace into progress values(?,?,?,?,?,?,?)",
        (schema + "." + table, status, source_end, target_total, copied, int(time.time()), error),
    )
    state.commit()
    return status, source_end, target_total


def connect(config):
    import pytds

    source = pytds.connect(
        server=config["SOURCE_HOST"], port=int(config["SOURCE_PORT"]), database=config["SOURCE_DB"],
        user=config["SOURCE_USER"], password=config["SOURCE_PASSWORD"], autocommit=True, timeout=90,
    )
    target_master = pytds.connect(
        server="127.0.0.1", port=11433, database="master", user="sa",
        password=config["TARGET_SA_PASSWORD"], autocommit=True, timeout=90,
    )
    cursor = target_master.cursor()
    cursor.execute(f"if db_id('{TARGET_DATABASE}') is null create database {quote(TARGET_DATABASE)}")
    target_master.close()
    target = pytds.connect(
        server="127.0.0.1", port=11433, database=TARGET_DATABASE, user="sa",
        password=config["TARGET_SA_PASSWORD"], autocommit=False, timeout=90,
    )
    return source, target


def reconnect(source, target, config):
    for connection in (source, target):
        try:
            connection.close()
        except Exception:
            pass
    return connect(config)


def prioritize_incomplete_tables(tables, state):
    """Resume interrupted or mismatched tables before the full verification scan."""
    priority = {
        row[0]
        for row in state.execute(
            "select table_name from progress where status in ('running','failed')"
        )
    }
    return sorted(tables, key=lambda item: 0 if item[0] + "." + item[1] in priority else 1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--batch-size", type=int, default=5000)
    parser.add_argument("--max-tables", type=int, default=0)
    args = parser.parse_args()
    config = read_env()
    source, target = connect(config)
    state = init_state()
    started = int(time.time())
    run_id = state.execute(
        "insert into mirror_runs(mode,status,started_at) values(?,?,?)",
        ("dry_run" if args.dry_run else "full_copy", "running", started),
    ).lastrowid
    state.commit()
    source_cursor, target_cursor = source.cursor(), target.cursor()
    tables = prioritize_incomplete_tables(source_tables(source_cursor), state)
    selected = tables[: args.max_tables] if args.max_tables else tables
    completed = failed = 0
    try:
        for schema, table in selected:
            try:
                columns = table_columns(source_cursor, schema, table)
                if not columns:
                    raise RuntimeError("table metadata missing")
                if args.dry_run:
                    row_count(source_cursor, schema, table)
                    primary_key_columns(source_cursor, schema, table)
                    status, source_rows, target_rows = "validated", 0, 0
                else:
                    status, source_rows, target_rows = copy_table(
                        source_cursor, target_cursor, state, schema, table, args.batch_size
                    )
                if status in ("completed", "validated"):
                    completed += 1
                else:
                    failed += 1
                log_event(table=schema + "." + table, status=status, source_rows=source_rows, target_rows=target_rows)
            except Exception as exc:
                try:
                    target.rollback()
                except Exception:
                    source, target = reconnect(source, target, config)
                    source_cursor, target_cursor = source.cursor(), target.cursor()
                previous = state.execute(
                    "select source_rows,copied_rows from progress where table_name=?", (schema + "." + table,)
                ).fetchone() or (0, 0)
                state.execute(
                    "insert or replace into progress values(?,?,?,?,?,?,?)",
                    (schema + "." + table, "failed", previous[0], 0, previous[1], int(time.time()), str(exc)[:1000]),
                )
                state.commit()
                if "UnicodeDecodeError" in str(exc) and not args.dry_run:
                    BINARY_TEXT_TABLES.add(table)
                    try:
                        status, source_rows, target_rows = copy_table(
                            source_cursor, target_cursor, state, schema, table, args.batch_size
                        )
                        if status == "completed":
                            completed += 1
                            log_event(table=schema + "." + table, status="completed_binary_preserved", source_rows=source_rows, target_rows=target_rows)
                            continue
                        exc = RuntimeError("binary retry row count mismatch")
                    except Exception as retry_exc:
                        exc = retry_exc
                        try:
                            target.rollback()
                        except Exception:
                            source, target = reconnect(source, target, config)
                            source_cursor, target_cursor = source.cursor(), target.cursor()
                failed += 1
                state.execute(
                    "insert or replace into progress values(?,?,?,?,?,?,?)",
                    (schema + "." + table, "failed", previous[0], 0, previous[1], int(time.time()), str(exc)[:1000]),
                )
                state.commit()
                log_event(table=schema + "." + table, status="failed", error=str(exc))
        final_status = "completed" if failed == 0 else "completed_with_errors"
        state.execute(
            "update mirror_runs set status=?,source_tables=?,completed_tables=?,failed_tables=?,finished_at=? where id=?",
            (final_status, len(tables), completed, failed, int(time.time()), run_id),
        )
        state.commit()
        print(json.dumps({"run_id": run_id, "mode": "dry_run" if args.dry_run else "full_copy", "source_tables": len(tables), "processed": len(selected), "completed": completed, "failed": failed}, ensure_ascii=False))
    finally:
        state.close()
        source.close()
        target.close()


if __name__ == "__main__":
    main()
