import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LEGACY_DISPLAY_NAME = re.compile(
    r"(?<![A-Za-z0-9_])(?:Fire" + r"Fox|Firefox|Fox" + r"Brain)(?![A-Za-z0-9_])"
)


class VafoxBrandMigrationTests(unittest.TestCase):
    def test_four_system_names_are_present(self):
        portal = (ROOT / "portal_v2.py").read_text(encoding="utf-8")
        ai_base = (ROOT / "apps/ai/templates/base.html").read_text(encoding="utf-8")
        core = (ROOT / "apps/core_api/app.py").read_text(encoding="utf-8")
        gateway = (ROOT / "apps/gateway/index.html").read_text(encoding="utf-8")
        self.assertIn("VAFOX Enterprise Brain", portal)
        self.assertIn("VAFOX Enterprise AI Center", ai_base)
        self.assertIn("VAFOX Enterprise Data Core", core)
        self.assertIn("VAFOX Gateway", gateway)

    def test_user_visible_surfaces_have_no_legacy_display_name(self):
        paths = [ROOT / "portal_v2.py", ROOT / "apps/core_api/app.py"]
        paths.extend((ROOT / "apps/ai/templates").glob("*.html"))
        paths.extend([
            ROOT / "apps/gateway/index.html",
            ROOT / "apps/gateway/explorer_identity.py",
        ])
        failures = []
        for path in paths:
            match = LEGACY_DISPLAY_NAME.search(path.read_text(encoding="utf-8"))
            if match:
                failures.append("{}:{}".format(path.relative_to(ROOT), match.group(0)))
        self.assertEqual(failures, [])

    def test_current_markdown_uses_vafox_brand(self):
        failures = []
        current_markdown = [
            ROOT / "GENESIS_CONSTRUCTION_VALIDATION_REPORT.md",
            ROOT / "GENESIS_REMEDIATION_REPORT.md",
        ]
        for path in current_markdown:
            if not path.exists():
                continue
            text = path.read_text(encoding="utf-8")
            text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
            text = re.sub(r"`[^`]*`", "", text)
            match = LEGACY_DISPLAY_NAME.search(text)
            if match:
                failures.append("{}:{}".format(path.relative_to(ROOT), match.group(0)))
        self.assertEqual(failures, [])

    def test_technical_compatibility_identifiers_are_preserved(self):
        portal = (ROOT / "portal_v2.py").read_text(encoding="utf-8")
        ai_app = (ROOT / "apps/ai/app.py").read_text(encoding="utf-8")
        self.assertIn("/opt/firefox-portal", portal)
        self.assertIn("X-FoxBrain-Service-Token", ai_app)
        self.assertTrue((ROOT / "foxbrain_os").is_dir())

    def test_ai_visual_mark_uses_v(self):
        base = (ROOT / "apps/ai/templates/base.html").read_text(encoding="utf-8")
        login = (ROOT / "apps/ai/templates/login.html").read_text(encoding="utf-8")
        self.assertIn('<span>V</span><strong>VAFOX Enterprise AI Center</strong>', base)
        self.assertIn('<span class="mark">V</span>', login)


if __name__ == "__main__":
    unittest.main()
