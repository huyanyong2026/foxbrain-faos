import json
from pathlib import Path

from foxbrain_os.platform_governance import deployment_metadata, version_payload


def test_version_payload_exposes_production_identity(monkeypatch):
    monkeypatch.setenv("FOXBRAIN_ENV", "production")
    monkeypatch.setenv("GIT_COMMIT", "abc123")
    payload = version_payload("gateway")
    assert payload["system"] == "FoxBrain"
    assert payload["version"] == "AI-OS-V4.0"
    assert payload["release"] == "production"
    assert payload["service"] == "gateway"
    assert payload["commit"] == "abc123"
    assert payload["status"] == "running"


def test_deployment_metadata_contains_required_services(monkeypatch, tmp_path):
    metadata = tmp_path / "deployment.json"
    metadata.write_text(json.dumps({
        "system": "FoxBrain",
        "version": "AI-OS-V4.0",
        "release": "production",
        "commit": "abc123",
        "build_time": "2026-01-01T00:00:00+00:00",
        "deploy_time": "2026-01-01T00:01:00+00:00",
        "environment": "production",
        "services": ["gateway", "huyan", "ai", "core"],
    }), encoding="utf-8")
    monkeypatch.setenv("FOXBRAIN_DEPLOYMENT_METADATA", str(metadata))
    data = deployment_metadata()
    assert data["services"] == ["gateway", "huyan", "ai", "core"]
    assert data["environment"] == "production"
