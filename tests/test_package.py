"""Build and inspect the sanora-base Debian package. Fully offline."""

import hashlib
import pathlib
import shutil
import tempfile
import unittest

from helpers import BUILD_EPOCH, REPO_ROOT, build_package, read_version_env, run


class PackageValidation(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        built = build_package()
        cls.tmp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.tmp.cleanup)
        cls.root = pathlib.Path(cls.tmp.name) / "extracted"
        cls.root.mkdir()
        # Work on a private copy: other tests rebuild the package in place.
        cls.deb = pathlib.Path(cls.tmp.name) / "sanora-base.deb"
        shutil.copy2(built, cls.deb)
        run(["dpkg-deb", "-x", str(cls.deb), str(cls.root)])

    def test_control_fields(self):
        fields = run(["dpkg-deb", "-f", str(self.deb),
                      "Package", "Version", "Architecture", "Depends"]).stdout
        version = read_version_env()["SANORA_VERSION"]
        self.assertIn("Package: sanora-base", fields)
        self.assertIn(f"Version: {version}", fields)
        self.assertIn("Architecture: all", fields)
        self.assertIn("base-files", fields)

    def test_expected_payload_files(self):
        expected = [
            "etc/os-release",
            "etc/sanora/release",
            "etc/sanora/sanora.conf",
            "etc/apt/apt.conf.d/99-sanora-security",
            "etc/live/config.conf.d/10-sanora-user.conf",
            "etc/xdg/kdeglobals",
            "etc/skel/.config/plasma-org.kde.plasma.desktop-appletsrc",
            "etc/calamares/branding/sanora/branding.desc",
            "etc/calamares/branding/sanora/show.qml",
            "etc/calamares/branding/sanora/sanora-logo.png",
            "etc/calamares/modules/partition.conf",
            "etc/xdg/plasma-org.kde.plasma.desktop-appletsrc",
            "usr/share/plasma/look-and-feel/org.sanora.light.desktop/metadata.json",
            "usr/share/plasma/look-and-feel/org.sanora.dark.desktop/metadata.json",
            "usr/share/plasma/look-and-feel/org.sanora.light.desktop/contents/defaults",
            "usr/share/plasma/look-and-feel/org.sanora.light.desktop/contents/layouts/org.kde.plasma.desktop-layout.js",
            "usr/share/color-schemes/SANORALight.colors",
            "usr/share/color-schemes/SANORADark.colors",
            "usr/share/icons/sanora/index.theme",
            "usr/share/icons/sanora-dark/index.theme",
            "usr/share/plasma/desktoptheme/sanora/metadata.json",
            "usr/share/sanora/tests/calamares_driver.py",
            "usr/bin/sanora-info",
            "usr/share/sanora/branding/sanora-logo.svg",
            "usr/share/sanora/branding/sanora-logo.png",
            "usr/share/sanora/wallpapers/sanora-wallpaper.svg",
            "usr/share/sanora/wallpapers/sanora-wallpaper.png",
            "usr/share/doc/sanora-base/copyright",
        ]
        missing = [p for p in expected if not (self.root / p).is_file()]
        self.assertEqual(missing, [], f"missing payload files: {missing}")

    def test_no_developer_readme_in_payload(self):
        self.assertFalse((self.root / "README.md").exists(),
                         "developer README must not be installed at /README.md")

    def test_os_release_identity_is_english_and_international(self):
        text = (self.root / "etc/os-release").read_text()
        self.assertIn('NAME="SANORA OS"', text)
        self.assertIn('ID="sanora"', text)
        self.assertIn('ID_LIKE="debian"', text)
        self.assertIn('DEFAULT_LANGUAGE="en"', text)
        self.assertNotIn("nl_NL", text)
        self.assertIn("Debian 13 (trixie)", text)

    def test_sanora_info_runs_against_extracted_tree(self):
        # build-info is written by the live-build config, not by the package;
        # supply a representative one so the helper can be exercised offline.
        (self.root / "etc/sanora/build-info").write_text(
            "SANORA_BUILD_ID=test-0001\n"
            "DEBIAN_SUITE=trixie\n"
            "DEBIAN_VERSION=13\n"
            "SANORA_ARCH=amd64\n"
            "SANORA_DEFAULT_LOCALE=en_US.UTF-8\n"
        )
        result = run([str(self.root / "usr/bin/sanora-info")],
                     env={"SANORA_ROOT": str(self.root), "LC_ALL": "C"})
        self.assertEqual(result.returncode, 0, result.stderr)
        for expected in ("SANORA OS", "sanora", "Debian 13", "trixie",
                         "amd64", "en_US.UTF-8", "test-0001",
                         "KDE Plasma (Wayland)"):
            self.assertIn(expected, result.stdout,
                          f"sanora-info output missing '{expected}':\n{result.stdout}")

    def test_maintainer_scripts_syntax(self):
        for script in ("preinst", "postrm"):
            path = REPO_ROOT / "packages/sanora-base/DEBIAN" / script
            result = run(["sh", "-n", str(path)])
            self.assertEqual(result.returncode, 0,
                             f"{script} has shell syntax errors: {result.stderr}")
        result = run(["sh", "-n", str(self.root / "usr/bin/sanora-info")])
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_package_is_root_owned(self):
        listing = run(["dpkg-deb", "-c", str(self.deb)]).stdout
        self.assertNotIn("user/user", listing)
        self.assertIn("root/root", listing)

    def test_mtimes_are_clamped_to_source_date_epoch(self):
        # A build with epoch 0 must not record the checkout time in the .deb.
        out_dir = REPO_ROOT / "build" / "work" / "packages"
        for old in out_dir.glob("*.deb"):
            old.unlink()
        run(["bash", str(REPO_ROOT / "build" / "scripts" / "build-package.sh")],
            env={"SOURCE_DATE_EPOCH": "0"})
        deb = sorted(out_dir.glob("*.deb"))[0]
        listing = run(["dpkg-deb", "-c", str(deb)]).stdout
        self.assertIn("1970-01-01", listing)
        self.assertNotIn("2026-", listing)

    def test_package_build_is_reproducible(self):
        out_dir = REPO_ROOT / "build" / "work" / "packages"
        for old in out_dir.glob("*.deb"):
            old.unlink()
        digests = []
        for _ in range(2):
            run(["bash", str(REPO_ROOT / "build" / "scripts" / "build-package.sh")],
                env={"SOURCE_DATE_EPOCH": BUILD_EPOCH})
            deb = sorted(out_dir.glob("*.deb"))[0]
            digests.append(hashlib.sha256(deb.read_bytes()).hexdigest())
        self.assertEqual(digests[0], digests[1],
                         "two builds with the same SOURCE_DATE_EPOCH differ")


if __name__ == "__main__":
    unittest.main()
