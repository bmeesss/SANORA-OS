"""Offline validation of the original SANORA KDE Plasma identity."""

import json
import re
import unittest
import xml.etree.ElementTree as ET

from helpers import REPO_ROOT


class ThemeValidation(unittest.TestCase):
    def setUp(self):
        self.plasma = REPO_ROOT / "branding" / "plasma"

    def test_look_and_feel_metadata_template_is_valid_json(self):
        text = (self.plasma / "look-and-feel/metadata.json.in").read_text()
        data = json.loads(text)
        self.assertEqual(data["KPackageStructure"], "Plasma/LookAndFeel")
        self.assertIn("@THEME_ID@", text)
        self.assertEqual(data["KPlugin"]["License"], "GPLv2+")

    def test_defaults_template_has_all_required_groups(self):
        text = (self.plasma / "look-and-feel/defaults.in").read_text()
        for group in (
            "[kdeglobals][KDE]", "[kdeglobals][General]",
            "[kdeglobals][Icons]", "[plasmarc][Theme]",
            "[Wallpaper]", "[kcminputrc][Mouse]",
            "[kwinrc][org.kde.kdecoration2]", "[ksplashrc][KSplash]",
        ):
            self.assertIn(group, text, f"missing defaults group {group}")
        for placeholder in ("@THEME_ID@", "@COLOR_SCHEME@", "@ICON_THEME@"):
            self.assertIn(placeholder, text)

    def test_layout_script_uses_verified_plasma_api(self):
        text = (self.plasma / "look-and-feel/org.kde.plasma.desktop-layout.js").read_text()
        for api in ("loadTemplate(", "panels()", "desktopsForActivity(",
                    "writeConfig(", "wallpaperPlugin", "location", "alignment",
                    "floating"):
            self.assertIn(api, text, f"layout script missing {api}")
        self.assertIn("sanora-default.png", text)
        self.assertIn("/usr/share/sanora/wallpapers", text)

    def test_color_schemes_have_required_sections(self):
        for name in ("SANORALight.colors", "SANORADark.colors"):
            text = (self.plasma / "colors" / name).read_text()
            with self.subTest(scheme=name):
                for section in (
                    "[General]", "[Colors:Window]", "[Colors:View]",
                    "[Colors:Button]", "[Colors:Selection]", "[Colors:Tooltip]",
                    "[WM]", "[ColorEffects:Disabled]", "[ColorEffects:Inactive]",
                ):
                    self.assertIn(section, text, f"{name} missing {section}")
                self.assertIn("Name=SANORA", text)

    def test_icon_theme_template_inherits_upstream(self):
        text = (self.plasma / "icons/index.theme.in").read_text()
        self.assertIn("Inherits=@ICON_INHERITS@", text)
        self.assertIn("[scalable/apps]", text)
        self.assertNotIn("apple", text.lower())

    def test_plasma_desktop_theme_metadata(self):
        data = json.loads((self.plasma / "desktoptheme/metadata.json").read_text())
        self.assertEqual(data["KPlugin"]["Id"], "sanora")
        self.assertEqual(data["KPlugin"]["License"], "GPLv2+")
        self.assertIn("X-Plasma-API", data)
        plasmarc = (self.plasma / "desktoptheme/plasmarc").read_text()
        self.assertIn("FallbackTheme=default", plasmarc)

    def test_svg_assets_are_valid_and_original(self):
        for svg in (self.plasma / "icons").glob("*.svg"):
            with self.subTest(svg=svg.name):
                ET.parse(svg)
                raw = re.sub(r"<!--.*?-->", "", svg.read_text(), flags=re.S).lower()
                for forbidden in ("apple", "macos", "cupertino", "finder"):
                    self.assertNotIn(forbidden, raw)

    def test_system_kde_default_selects_sanora_theme(self):
        text = (REPO_ROOT / "config/desktop/kdeglobals").read_text()
        self.assertIn("LookAndFeelPackage=org.sanora.light.desktop", text)
        self.assertIn("ColorScheme=SANORALight", text)
        self.assertIn("Theme=sanora", text)

    def test_package_builder_installs_theme(self):
        script = (REPO_ROOT / "build/scripts/build-package.sh").read_text()
        for path in (
            "usr/share/plasma/look-and-feel",
            "usr/share/color-schemes",
            "usr/share/icons",
            "usr/share/plasma/desktoptheme/sanora",
            "org.sanora.light.desktop",
            "org.sanora.dark.desktop",
        ):
            self.assertIn(path, script)


if __name__ == "__main__":
    unittest.main()
