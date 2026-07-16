from foxbrain_os.platform_alignment import platform_manifest, validate_manifest


def test_enterprise_os_manifest_covers_all_platforms():
    manifest = platform_manifest()
    assert manifest["version"] == "0.20.5"
    assert set(manifest["platforms"]) == {"core", "ai", "huyan", "gateway"}
    assert manifest["data_chain"] == "SAP B1 -> SAP Mirror -> Core -> Gateway/Huyan/AI"


def test_non_negotiable_alignment_rules_are_enforced():
    assert validate_manifest() == []
    broken = platform_manifest()
    broken["platforms"]["ai"]["source_of_truth"] = "local facts database"
    assert "ai_core_source_of_truth_missing" in validate_manifest(broken)
