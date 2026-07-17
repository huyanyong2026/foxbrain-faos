import pytest

from release_guard import EXPECTED_VERSION, validate_manifest


def _manifest(version: str = EXPECTED_VERSION) -> dict:
    service = {
        "frontend_version": version,
        "backend_version": version,
        "api_version": version,
        "database_schema_version": version,
        "deployment_version": version,
        "runtime_version": version,
    }
    return {"services": {name: dict(service) for name in ("gateway", "huyan", "ai", "core")}}


def test_release_guard_accepts_genesis_release_manifest():
    result = validate_manifest(_manifest())
    assert result["status"] == "PASS"
    assert result["expected_version"] == EXPECTED_VERSION
    assert result["failures"] == []


@pytest.mark.parametrize("legacy_version", ["AI-OS-V4.0", "AI-OS-V5", "AI-OS-V5.1", "FoxBrain Enterprise OS"])
def test_release_guard_rejects_obsolete_governance_versions(legacy_version):
    result = validate_manifest(_manifest(legacy_version))
    assert result["status"] == "FAIL"
    assert any("obsolete legacy version" in failure or "expected" in failure for failure in result["failures"])
