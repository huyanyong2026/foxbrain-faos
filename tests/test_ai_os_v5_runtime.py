from foxbrain_os.platform_governance import RELEASE_VERSION, runtime_payload


def test_runtime_payload_safe_genesis_metadata(monkeypatch):
    monkeypatch.setenv("FOXBRAIN_VERSION", RELEASE_VERSION)
    monkeypatch.setenv("FOXBRAIN_SYSTEM", "VAFOX")
    monkeypatch.setenv("FOXBRAIN_ENV", "production")
    payload = runtime_payload("huyan")
    assert payload["system"] == "VAFOX"
    assert payload["service"] == "Huyan"
    assert payload["version"] == RELEASE_VERSION
    assert payload["environment"] == "production"
    assert payload["status"] == "running"
    assert payload["runtime_status"] == "running"
    assert payload["checks"]["ceo_command_center_enabled"] is True
    forbidden = {"customer", "financial", "sap_rows", "business_data", "token", "password"}
    assert forbidden.isdisjoint(payload.keys())


def test_all_runtime_services_have_genesis_checks(monkeypatch):
    monkeypatch.setenv("FOXBRAIN_VERSION", RELEASE_VERSION)
    monkeypatch.setenv("FOXBRAIN_SYSTEM", "VAFOX")
    for service in ("gateway", "huyan", "ai", "core"):
        payload = runtime_payload(service)
        assert payload["version"] == RELEASE_VERSION
        assert payload["checks"]
