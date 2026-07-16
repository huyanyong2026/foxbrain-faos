from foxbrain_os.platform_governance import runtime_payload


def test_runtime_payload_safe_v5_metadata(monkeypatch):
    monkeypatch.setenv("FOXBRAIN_VERSION", "AI-OS-V5")
    monkeypatch.setenv("FOXBRAIN_ENV", "production")
    payload = runtime_payload("huyan")
    assert payload["system"] == "FoxBrain"
    assert payload["service"] == "Huyan"
    assert payload["version"] == "AI-OS-V5"
    assert payload["environment"] == "production"
    assert payload["status"] == "running"
    assert payload["runtime_status"] == "running"
    assert payload["checks"]["ceo_command_center_enabled"] is True
    forbidden = {"customer", "financial", "sap_rows", "business_data", "token", "password"}
    assert forbidden.isdisjoint(payload.keys())


def test_all_runtime_services_have_checks(monkeypatch):
    monkeypatch.setenv("FOXBRAIN_VERSION", "AI-OS-V5")
    for service in ("gateway", "huyan", "ai", "core"):
        payload = runtime_payload(service)
        assert payload["version"] == "AI-OS-V5"
        assert payload["checks"]
