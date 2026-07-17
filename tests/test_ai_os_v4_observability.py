import json
import os
import subprocess
import sys

from foxbrain_os.platform_governance import RELEASE_VERSION, control_tower_status, version_payload


def test_version_payload_exposes_genesis_runtime_metadata(monkeypatch, tmp_path):
    metadata = tmp_path / "deployment.json"
    metadata.write_text(json.dumps({"system": "VAFOX", "version": RELEASE_VERSION, "commit": "abc123", "build_time": "2026-07-16T00:00:00+00:00", "deploy_time": "2026-07-16T00:01:00+00:00", "environment": "production"}))
    monkeypatch.setenv("FOXBRAIN_DEPLOYMENT_METADATA", str(metadata))
    monkeypatch.setenv("GIT_COMMIT", "abc123")
    payload = version_payload("gateway")
    assert payload["system"] == "VAFOX"
    assert payload["version"] == RELEASE_VERSION
    assert payload["service"] == "gateway"
    assert payload["status"] == "running"


def test_control_tower_has_genesis_health_dashboard_fields(monkeypatch):
    monkeypatch.setenv("GIT_COMMIT", "abc123")
    payload = control_tower_status(last_deploy="2026-07-16T00:01:00+00:00")
    assert payload["release_version"] == RELEASE_VERSION
    assert payload["commit"] == "abc123"
    assert payload["last_deploy"] == "2026-07-16T00:01:00+00:00"
    assert set(payload["components"]) >= {"gateway", "huyan", "ai", "core"}


def test_generate_deployment_metadata(tmp_path):
    output = tmp_path / "deployment.json"
    env = os.environ.copy()
    env.update({"FOXBRAIN_DEPLOYMENT_METADATA": str(output), "GIT_COMMIT": "abc123", "BUILD_TIME": "2026-07-16T00:00:00+00:00", "DEPLOY_TIME": "2026-07-16T00:01:00+00:00", "FOXBRAIN_ENV": "production"})
    subprocess.check_call([sys.executable, "scripts/generate_deployment_metadata.py"], env=env)
    payload = json.loads(output.read_text())
    assert payload["system"] == "VAFOX"
    assert payload["version"] == RELEASE_VERSION
    assert payload["commit"] == "abc123"
    assert payload["environment"] == "production"
