from foxbrain_os.platform_governance import control_tower_status, health_payload, version_payload


def test_version_payload_has_standard_metadata(monkeypatch):
    monkeypatch.setenv("FOXBRAIN_VERSION", "0.20.5")
    payload = version_payload("foxbrain-core")
    assert set(payload) == {"service", "version", "commit", "build_time", "environment"}
    assert payload["service"] == "foxbrain-core"
    assert payload["version"] == "0.20.5"


def test_health_payload_requires_process_database_dependencies():
    checks = {"process": {"status": "healthy"}, "database": {"status": "healthy"}, "dependencies": {"status": "healthy"}}
    payload = health_payload("foxbrain-ai", checks)
    assert payload["status"] == "healthy"
    assert set(payload["checks"]) == {"process", "database", "dependencies"}


def test_control_tower_displays_enterprise_status():
    payload = control_tower_status(last_deploy="2026-07-16T00:00:00+00:00")
    assert payload["platform"] == "FoxBrain Enterprise OS"
    assert payload["release_version"] == "0.20.5"
    assert payload["components"]["core"]["status"] == "Healthy"
    assert payload["components"]["sap_sync"]["status"] == "Healthy"
