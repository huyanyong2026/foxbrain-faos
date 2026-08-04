"""Evidence-gated CEO daily report orchestration and persistence.

This module owns only the report read model.  Source facts are obtained through
an injected, read-only domain client and narrative generation through an
injected AI Runtime client; neither dependency has a write operation here.
"""
from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import threading
import uuid
from datetime import date, datetime, timezone
from pathlib import Path


DOMAINS = ("sales", "product", "inventory", "customer", "employee", "supply_chain")
SECTIONS = ("business_summary", "business_opportunities", "business_risks", "ceo_actions")
FRESHNESS = ("fresh", "delayed", "stale", "missing", "conflict")
CONFIDENCE = ("high", "medium", "low", "unavailable")
PRIORITY = ("critical", "high", "normal")
FRESHNESS_RANK = {value: index for index, value in enumerate(FRESHNESS)}


class ReportInputError(ValueError):
    pass


class InsufficientData(RuntimeError):
    pass


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def parse_report_date(value: str) -> str:
    try:
        parsed = date.fromisoformat(str(value))
    except (TypeError, ValueError) as exc:
        raise ReportInputError("report_date_must_be_iso_date") from exc
    if parsed > datetime.now(timezone.utc).date():
        raise ReportInputError("future_report_date_not_allowed")
    return parsed.isoformat()


class DailyReportRepository:
    """SQLite-backed immutable publication history, separate from source systems."""

    def __init__(self, path: str | Path | None = None):
        self.path = str(path or os.getenv("CEO_DAILY_REPORT_DB", "/var/lib/vafox/daily-report.db"))
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._initialize()

    def _connect(self):
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self):
        with self._connect() as db:
            db.execute("""create table if not exists ceo_daily_reports (
                organization_id text not null, report_date text not null,
                idempotency_key text not null, status text not null,
                report_json text not null, created_at text not null,
                primary key (organization_id, idempotency_key)
            )""")
            db.execute("create index if not exists idx_daily_report_history on ceo_daily_reports(organization_id, report_date desc, created_at desc)")

    def save(self, organization_id: str, idempotency_key: str, report: dict) -> dict:
        encoded, created_at = json.dumps(report, ensure_ascii=False, separators=(",", ":")), _now()
        with self._lock, self._connect() as db:
            db.execute("""insert into ceo_daily_reports
                (organization_id,report_date,idempotency_key,status,report_json,created_at)
                values (?,?,?,?,?,?) on conflict(organization_id,idempotency_key)
                do update set status=excluded.status,report_json=excluded.report_json""",
                (organization_id, report["report_date"], idempotency_key, report["status"], encoded, created_at))
        return report

    def get(self, organization_id: str, report_date: str) -> dict | None:
        with self._connect() as db:
            row = db.execute("""select report_json from ceo_daily_reports where organization_id=? and report_date=?
                order by case status when 'published' then 0 when 'degraded' then 1 else 2 end, created_at desc limit 1""",
                (organization_id, report_date)).fetchone()
        return json.loads(row[0]) if row else None

    def latest(self, organization_id: str) -> dict | None:
        with self._connect() as db:
            row = db.execute("""select report_json from ceo_daily_reports where organization_id=?
                and status in ('published','degraded') order by report_date desc, created_at desc limit 1""",
                (organization_id,)).fetchone()
        return json.loads(row[0]) if row else None

    def history(self, organization_id: str, limit: int, offset: int) -> dict:
        with self._connect() as db:
            total = db.execute("select count(*) from ceo_daily_reports where organization_id=?", (organization_id,)).fetchone()[0]
            rows = db.execute("""select report_json from ceo_daily_reports where organization_id=?
                order by report_date desc, created_at desc limit ? offset ?""", (organization_id, limit, offset)).fetchall()
        items = []
        for row in rows:
            report = json.loads(row[0])
            items.append({key: report.get(key) for key in ("report_id", "report_date", "status", "generated_at", "updated_at", "freshness_status", "confidence", "coverage", "audit_id")})
        return {"items": items, "total": total, "limit": limit, "offset": offset}


class DailyReportService:
    """Collect real domain evidence, call AI Runtime, and enforce publication gates."""

    def __init__(self, repository: DailyReportRepository, source_client=None, runtime_client=None,
                 minimum_domains: int | None = None):
        self.repository, self.source_client, self.runtime_client = repository, source_client, runtime_client
        self.minimum_domains = minimum_domains or int(os.getenv("CEO_DAILY_REPORT_MINIMUM_DOMAINS", "6"))

    @staticmethod
    def _key(organization_id: str, report_date: str) -> str:
        material = f"{organization_id}|{report_date}|Asia/Shanghai|v2.0.2"
        return hashlib.sha256(material.encode()).hexdigest()

    def _failure(self, organization_id: str, report_date: str, audit_id: str, code: str, source_status: list[dict]) -> dict:
        report = {"report_id": str(uuid.uuid4()), "report_date": report_date, "timezone": "Asia/Shanghai",
                  "status": "failed", "generated_at": _now(), "data_source": [], "updated_at": None,
                  "freshness_status": "missing", "confidence": {"level": "unavailable", "reason": code},
                  "source_status": source_status, "sections": {name: [] for name in SECTIONS},
                  "coverage": {"included_domains": [], "excluded_domains": list(DOMAINS), "reason": code},
                  "audit_id": audit_id, "error": {"code": code, "message": "No report was generated because verified source data was insufficient."}}
        return self.repository.save(organization_id, self._key(organization_id, report_date), report)

    def generate(self, organization_id: str, report_date: str) -> dict:
        report_date, audit_id = parse_report_date(report_date), str(uuid.uuid4())
        existing = self.repository.get(organization_id, report_date)
        if existing and existing.get("status") in {"published", "degraded"}:
            return existing
        if self.source_client is None or self.runtime_client is None:
            return self._failure(organization_id, report_date, audit_id, "report_dependencies_unavailable", [])
        statuses, evidence, usable = [], [], []
        for domain in DOMAINS:
            try:
                payload = self.source_client.get_daily_report_domain(domain, report_date)
                self._validate_domain(payload, domain)
                status = payload["freshness_status"]
                accepted = status not in {"missing", "conflict"} and bool(payload["evidence"])
                statuses.append({"domain": domain, "available": accepted, "data_source": payload["data_source"],
                                 "updated_at": payload["updated_at"], "freshness_status": status,
                                 "confidence": payload["confidence"]})
                if accepted:
                    usable.append(domain)
                    for item in payload["evidence"]:
                        evidence.append({**item, "domain": domain, "data_source": payload["data_source"],
                                         "freshness_status": status})
            except (KeyError, TypeError, ValueError, RuntimeError):
                statuses.append({"domain": domain, "available": False, "data_source": [], "updated_at": None,
                                 "freshness_status": "missing", "confidence": {"level": "unavailable", "reason": "source_contract_invalid"}})
        if len(usable) < self.minimum_domains:
            return self._failure(organization_id, report_date, audit_id, "insufficient_verified_domains", statuses)
        try:
            generated = self.runtime_client.generate_daily_report(report_date, evidence)
            sections = self._validate_and_enrich(generated, evidence)
        except (KeyError, TypeError, ValueError, RuntimeError):
            return self._failure(organization_id, report_date, audit_id, "runtime_output_rejected", statuses)
        sources = sorted({source for item in evidence for source in item["data_source"]})
        timestamps = [item["updated_at"] for item in evidence]
        freshness = max((item["freshness_status"] for item in evidence), key=FRESHNESS_RANK.get)
        level = "high" if freshness == "fresh" else "medium" if freshness == "delayed" else "low"
        report = {"report_id": str(uuid.uuid4()), "report_date": report_date, "timezone": "Asia/Shanghai",
                  "status": "published" if len(usable) == len(DOMAINS) else "degraded", "generated_at": _now(),
                  "data_source": sources, "updated_at": min(timestamps), "freshness_status": freshness,
                  "confidence": {"level": level, "reason": "deterministic evidence coverage and freshness gate"},
                  "source_status": statuses, "sections": sections,
                  "coverage": {"included_domains": usable, "excluded_domains": [d for d in DOMAINS if d not in usable],
                               "reason": "all required domains verified" if len(usable) == len(DOMAINS) else "limited to verified domains"},
                  "audit_id": audit_id}
        return self.repository.save(organization_id, self._key(organization_id, report_date), report)

    @staticmethod
    def _validate_domain(payload: dict, domain: str):
        if not isinstance(payload, dict) or payload.get("domain") != domain:
            raise ValueError("domain_contract_invalid")
        if not isinstance(payload.get("data_source"), list) or not payload["data_source"]:
            raise ValueError("source_required")
        datetime.fromisoformat(payload["updated_at"].replace("Z", "+00:00"))
        if payload.get("freshness_status") not in FRESHNESS or payload.get("confidence", {}).get("level") not in CONFIDENCE:
            raise ValueError("lineage_invalid")
        if not isinstance(payload.get("evidence"), list):
            raise ValueError("evidence_invalid")
        for item in payload["evidence"]:
            required = ("evidence_id", "metric_key", "observed_value", "scope", "source_ref", "updated_at")
            if not isinstance(item, dict) or any(item.get(key) is None for key in required):
                raise ValueError("evidence_invalid")
            datetime.fromisoformat(item["updated_at"].replace("Z", "+00:00"))

    @staticmethod
    def _validate_and_enrich(generated: dict, evidence: list[dict]) -> dict:
        if not isinstance(generated, dict) or set(generated) != set(SECTIONS):
            raise ValueError("sections_invalid")
        by_id = {item["evidence_id"]: item for item in evidence}
        result = {}
        for section in SECTIONS:
            if not isinstance(generated[section], list) or (section == "business_summary" and not generated[section]):
                raise ValueError("section_items_invalid")
            result[section] = []
            for raw in generated[section]:
                refs = raw.get("evidence_ids") if isinstance(raw, dict) else None
                if not refs or any(ref not in by_id for ref in refs):
                    raise ValueError("evidence_reference_invalid")
                used = [by_id[ref] for ref in refs]
                if not all(str(raw.get(key, "")).strip() for key in ("conclusion", "recommendation")):
                    raise ValueError("narrative_required")
                freshness = max((item["freshness_status"] for item in used), key=FRESHNESS_RANK.get)
                level = "low" if freshness == "stale" else "medium" if freshness == "delayed" else "high"
                result[section].append({"item_id": str(uuid.uuid4()),
                    "priority": raw.get("priority") if raw.get("priority") in PRIORITY else "normal",
                    "conclusion": raw["conclusion"].strip(), "evidence": used,
                    "recommendation": raw["recommendation"].strip(),
                    "data_source": sorted({source for item in used for source in item["data_source"]}),
                    "updated_at": min(item["updated_at"] for item in used), "freshness_status": freshness,
                    "confidence": {"level": level, "reason": "derived from referenced evidence freshness"},
                    "related_item_ids": []})
        return result
