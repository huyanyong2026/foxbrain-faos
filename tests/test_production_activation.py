import json
from pathlib import Path

from foxbrain_os.platform_governance import deployment_metadata, version_payload


def test_version_payload_exposes_production_identity(monkeypatch):
    monkeypatch.setenv("FOXBRAIN_ENV", "production")
    monkeypatch.setenv("FOXBRAIN_SYSTEM", "VAFOX")
    monkeypatch.setenv("FOXBRAIN_VERSION", "AI-OS-V6-CLEAN-REBUILD-V1")
    monkeypatch.setenv("GIT_COMMIT", "abc123")
    payload = version_payload("gateway")
    assert payload["system"] == "VAFOX"
    assert payload["version"] == "AI-OS-V6-CLEAN-REBUILD-V1"
    assert payload["release"] == "production"
    assert payload["service"] == "gateway"
    assert payload["commit"] == "abc123"
    assert payload["status"] == "running"


def test_deployment_metadata_contains_required_services(monkeypatch, tmp_path):
    metadata = tmp_path / "deployment.json"
    metadata.write_text(json.dumps({
        "system": "VAFOX",
        "version": "AI-OS-V6-CLEAN-REBUILD-V1",
        "release": "production",
        "commit": "abc123",
        "build_time": "2026-01-01T00:00:00+00:00",
        "deploy_time": "2026-01-01T00:01:00+00:00",
        "environment": "production",
        "services": ["gateway", "huyan", "ai", "core"],
    }), encoding="utf-8")
    monkeypatch.setenv("FOXBRAIN_DEPLOYMENT_METADATA", str(metadata))
    monkeypatch.setenv("FOXBRAIN_SYSTEM", "VAFOX")
    monkeypatch.setenv("FOXBRAIN_VERSION", "AI-OS-V6-CLEAN-REBUILD-V1")
    data = deployment_metadata()
    assert data["system"] == "VAFOX"
    assert data["version"] == "AI-OS-V6-CLEAN-REBUILD-V1"
    assert data["services"] == ["gateway", "huyan", "ai", "core"]
    assert data["environment"] == "production"
