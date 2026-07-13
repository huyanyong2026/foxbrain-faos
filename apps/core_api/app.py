"""Authenticated, read-only HTTP access to the SAP mirror.

The service deliberately exposes no generic SQL endpoint and accepts no
mutating HTTP methods.  SAP credentials are never loaded by this process.
"""

from __future__ import annotations

import hmac
import json
import os
import re
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from decimal import Decimal
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse


IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_@$#]*$")
DEFAULT_TABLES = {
    "dbo.OADM", "dbo.OITM", "dbo.OITB", "dbo.OITW", "dbo.OWHS",
    "dbo.OCRD", "dbo.OCRG", "dbo.OINV", "dbo.INV1", "dbo.ORIN",
    "dbo.RIN1", "dbo.OPCH", "dbo.PCH1", "dbo.OPOR", "dbo.POR1",
    "dbo.ORDR", "dbo.RDR1", "dbo.OHEM", "dbo.OSLP",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def json_value(value):
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, (bytes, bytearray)):
        return {"type": "binary", "bytes": len(value)}
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value)


def quote_identifier(value: str) -> str:
    if not IDENTIFIER.fullmatch(value):
        raise ValueError("invalid identifier")
    return "[{}]".format(value.replace("]", "]]"))


class TokenPolicy:
    def __init__(self, raw: str):
        parsed = json.loads(raw or "{}")
        self.entries = []
        for client, config in parsed.items():
            token = str(config.get("token", ""))
            if token:
                self.entries.append((client, token, set(config.get("scopes", []))))

    def authorize(self, token: str, scope: str):
        for client, expected, scopes in self.entries:
            if hmac.compare_digest(token, expected) and scope in scopes:
                return client
        return None


class CoreService:
    def __init__(self, state_path=None, allowed_tables=None, connector=None):
        self.state_path = Path(state_path or os.environ.get(
            "CORE_MIRROR_STATE", "/opt/foxbrain-core/sync/mirror-state.db"
        ))
        configured = allowed_tables or os.environ.get("CORE_ALLOWED_TABLES", "")
        self.allowed_tables = {
            item.strip() for item in configured.split(",") if item.strip()
        } or set(DEFAULT_TABLES)
        self.connector = connector or self._connect

    def _connect(self):
        import pytds
        return pytds.connect(
            server=os.environ.get("CORE_DB_HOST", "127.0.0.1"),
            port=int(os.environ.get("CORE_DB_PORT", "11433")),
            database=os.environ.get("CORE_DB_NAME", "SAP_MIRROR"),
            user=os.environ["CORE_DB_USER"],
            password=os.environ["CORE_DB_PASSWORD"],
            timeout=15,
        )

    def status(self):
        result = {
            "service": "FoxBrain Enterprise Data Core",
            "mode": "read_only",
            "source": "SAP mirror",
            "checked_at": utc_now(),
            "mirror": {"status": "unknown", "completed_tables": 0, "failed_tables": 0},
        }
        if not self.state_path.exists():
            return result
        with closing(sqlite3.connect(str(self.state_path))) as db:
            db.row_factory = sqlite3.Row
            run = db.execute(
                "select * from mirror_runs order by rowid desc limit 1"
            ).fetchone()
            if run:
                data = dict(run)
                result["mirror"] = {
                    "status": "completed" if data.get("finished_at") and not data.get("error") else "running_or_failed",
                    "source_tables": data.get("source_tables", 0),
                    "completed_tables": data.get("completed_tables", 0),
                    "failed_tables": data.get("failed_tables", 0),
                    "started_at": data.get("started_at"),
                    "finished_at": data.get("finished_at"),
                }
        return result

    def tables(self):
        progress = {}
        if self.state_path.exists():
            with closing(sqlite3.connect(str(self.state_path))) as db:
                db.row_factory = sqlite3.Row
                for row in db.execute("select * from progress"):
                    progress[str(row[0])] = dict(row)
        return [
            {
                "table": name,
                "status": progress.get(name, {}).get("status", "not_recorded"),
                "rows": progress.get(name, {}).get("target_total"),
                "updated_at": progress.get(name, {}).get("updated_at"),
            }
            for name in sorted(self.allowed_tables)
        ]

    def rows(self, schema: str, table: str, limit: int, offset: int):
        full_name = "{}.{}".format(schema, table)
        if full_name not in self.allowed_tables:
            raise PermissionError("table is not approved for API access")
        schema_sql = quote_identifier(schema)
        table_sql = quote_identifier(table)
        limit = max(1, min(int(limit), 200))
        offset = max(0, int(offset))
        connection = self.connector()
        try:
            cursor = connection.cursor()
            cursor.execute(
                "select * from {}.{} order by (select null) offset %s rows fetch next %s rows only".format(
                    schema_sql, table_sql
                ),
                (offset, limit),
            )
            columns = [item[0] for item in cursor.description]
            rows = [dict(zip(columns, (json_value(value) for value in row))) for row in cursor.fetchall()]
            return {"table": full_name, "offset": offset, "limit": limit, "rows": rows}
        finally:
            connection.close()


class CoreApiHandler(BaseHTTPRequestHandler):
    server_version = "FoxBrainCore/1.0"

    def log_message(self, fmt, *args):
        print(json.dumps({"at": utc_now(), "client": self.client_address[0], "message": fmt % args}, ensure_ascii=True))

    def _token(self):
        header = self.headers.get("Authorization", "")
        return header[7:].strip() if header.lower().startswith("bearer ") else ""

    def _reply(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def _authorized(self, scope):
        client = self.server.policy.authorize(self._token(), scope)
        if not client:
            self._reply(401, {"error": "unauthorized"})
        return client

    def do_HEAD(self):
        self.do_GET()

    def do_GET(self):
        parsed = urlparse(self.path)
        try:
            if parsed.path in ("/healthz",):
                if self.client_address[0] not in ("127.0.0.1", "::1"):
                    return self._reply(404, {"error": "not_found"})
                return self._reply(200, {"status": "ok"})
            if parsed.path == "/api/health":
                if not self._authorized("facts:read"):
                    return
                return self._reply(200, self.server.service.status())
            if parsed.path == "/api/v1/status":
                if not self._authorized("facts:read"):
                    return
                return self._reply(200, self.server.service.status())
            if parsed.path == "/api/v1/public/status":
                if not self._authorized("public:read"):
                    return
                status = self.server.service.status()
                return self._reply(200, {
                    "service": status["service"], "mode": status["mode"],
                    "status": status["mirror"]["status"], "checked_at": status["checked_at"],
                })
            if parsed.path == "/api/v1/tables":
                if not self._authorized("facts:read"):
                    return
                return self._reply(200, {"tables": self.server.service.tables()})
            match = re.fullmatch(r"/api/v1/tables/([^/]+)/([^/]+)/rows", parsed.path)
            if match:
                if not self._authorized("facts:read"):
                    return
                query = parse_qs(parsed.query)
                result = self.server.service.rows(
                    match.group(1), match.group(2),
                    int(query.get("limit", [50])[0]), int(query.get("offset", [0])[0]),
                )
                return self._reply(200, result)
            return self._reply(404, {"error": "not_found"})
        except (ValueError, PermissionError) as exc:
            return self._reply(400, {"error": str(exc)})
        except Exception:
            return self._reply(503, {"error": "data_core_unavailable"})

    def _read_only(self):
        self._reply(405, {"error": "read_only_api"})

    do_POST = _read_only
    do_PUT = _read_only
    do_PATCH = _read_only
    do_DELETE = _read_only


def create_server(host=None, port=None, service=None, policy=None):
    token_config = os.environ.get("CORE_API_TOKENS_JSON", "{}")
    token_file = os.environ.get("CORE_API_TOKENS_FILE")
    if token_file:
        token_config = Path(token_file).read_text(encoding="utf-8")
    server = ThreadingHTTPServer(
        (host or os.environ.get("CORE_API_HOST", "127.0.0.1"), int(port or os.environ.get("CORE_API_PORT", "8090"))),
        CoreApiHandler,
    )
    server.service = service or CoreService()
    server.policy = policy or TokenPolicy(token_config)
    return server


def main():
    create_server().serve_forever()


if __name__ == "__main__":
    main()
