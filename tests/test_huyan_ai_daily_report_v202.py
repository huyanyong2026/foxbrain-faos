import tempfile
from pathlib import Path

from services.business.daily_report import DOMAINS, SECTIONS, DailyReportRepository, DailyReportService


class SourceReader:
    def __init__(self, unavailable=()):
        self.unavailable = set(unavailable)

    def get_daily_report_domain(self, domain, report_date):
        if domain in self.unavailable:
            raise RuntimeError("source unavailable")
        timestamp = f"{report_date}T00:30:00+00:00"
        return {
            "domain": domain,
            "data_source": [f"business-api:{domain}"],
            "updated_at": timestamp,
            "freshness_status": "fresh",
            "confidence": {"level": "high", "reason": "source contract verified"},
            "evidence": [{
                "evidence_id": f"{domain}:metric", "metric_key": f"{domain}.status",
                "observed_value": "verified", "comparison": "source supplied baseline",
                "scope": "ALL_DATA", "source_ref": f"trace:{domain}", "updated_at": timestamp,
            }],
        }


class RuntimeReader:
    def generate_daily_report(self, report_date, evidence):
        evidence_id = evidence[0]["evidence_id"]
        item = {"priority": "high", "conclusion": "Evidence-backed observation.",
                "recommendation": "CEO should request an accountable review.", "evidence_ids": [evidence_id]}
        return {section: [dict(item)] for section in SECTIONS}


def service(path, source=None, runtime=None, minimum=6):
    repository = DailyReportRepository(Path(path) / "reports.db")
    return DailyReportService(repository, source, runtime, minimum)


def test_generates_all_sections_and_lineage_from_verified_six_domain_data():
    with tempfile.TemporaryDirectory() as directory:
        reports = service(directory, SourceReader(), RuntimeReader())
        report = reports.generate("org-1", "2026-08-04")
        assert report["status"] == "published"
        assert report["coverage"]["included_domains"] == list(DOMAINS)
        assert set(report["sections"]) == set(SECTIONS)
        for items in report["sections"].values():
            assert items and all({"data_source", "updated_at", "freshness_status", "confidence"} <= item.keys() for item in items)
        assert {item["domain"] for item in report["source_status"]} == set(DOMAINS)


def test_insufficient_data_is_explicit_failure_without_generated_content():
    with tempfile.TemporaryDirectory() as directory:
        reports = service(directory, SourceReader({"employee"}), RuntimeReader())
        report = reports.generate("org-1", "2026-08-04")
        assert report["status"] == "failed"
        assert report["error"]["code"] == "insufficient_verified_domains"
        assert all(not items for items in report["sections"].values())
        assert report["confidence"]["level"] == "unavailable"


def test_published_report_is_idempotent_and_history_is_organization_scoped():
    with tempfile.TemporaryDirectory() as directory:
        reports = service(directory, SourceReader(), RuntimeReader())
        first = reports.generate("org-1", "2026-08-04")
        second = reports.generate("org-1", "2026-08-04")
        reports.generate("org-2", "2026-08-04")
        assert second["report_id"] == first["report_id"]
        history = reports.repository.history("org-1", 30, 0)
        assert history["total"] == 1
        assert history["items"][0]["report_date"] == "2026-08-04"
