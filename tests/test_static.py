"""Offline static validation of the SANORA OS build foundation.

Run with: python3 -m unittest discover -s tests -v
These tests need no root, no network and no live-build installation.
"""

import hashlib
import re
import stat
import unittest
import xml.etree.ElementTree as ET

from helpers import REPO_ROOT, package_names, read_version_env


class StaticValidation(unittest.TestCase):

    def test_required_files_exist(self):
        required = [
            "README.md", "LICENSE", "CONTRIBUTING.md", "CODE_OF_CONDUCT.md",
            "SECURITY.md", "THIRD_PARTY.md", ".gitignore", "build.sh",
            "config/version.env",
            "build/live-build/options.sh",
            "build/live-build/README.md",
            "build/scripts/preflight.sh",
            "build/scripts/build-package.sh",
            "build/scripts/assemble-config.sh",
            "build/scripts/write-metadata.py",
            "build/scripts/collect-versions.sh",
            ".github/workflows/iso.yml",
            ".github/ISO_BUILD_TRIGGER",
            "tests/boot/qemu_boot.py",
            "config/packages/README.md",
            "config/desktop/README.md",
            "config/system/README.md",
            "branding/sanora-logo.svg", "branding/sanora-logo.png",
            "branding/sanora-wallpaper.svg", "branding/sanora-wallpaper.png",
            "branding/iso/README.txt", "branding/iso/disk-info",
            "packages/sanora-base/DEBIAN/control.in",
            "packages/sanora-base/DEBIAN/preinst",
            "packages/sanora-base/DEBIAN/postrm",
            "packages/sanora-base/DEBIAN/copyright",
            "packages/sanora-base/usr/bin/sanora-info",
            "installer/calamares/branding/sanora/branding.desc",
            "installer/calamares/branding/sanora/show.qml",
            "installer/calamares/modules/partition.conf",
            "branding/plasma/README.md",
            "branding/plasma/look-and-feel/metadata.json.in",
            "branding/plasma/look-and-feel/defaults.in",
            "branding/plasma/look-and-feel/org.kde.plasma.desktop-layout.js",
            "branding/plasma/colors/SANORALight.colors",
            "branding/plasma/colors/SANORADark.colors",
            "branding/plasma/icons/index.theme.in",
            "branding/plasma/icons/sanora-launcher.svg",
            "build/scripts/build-repo.sh",
            "repo/README.md",
            "tests/install/calamares_driver.py",
            "tests/install/qemu_install.py",
            "tests/boot/qemu_baseline.py",
            "docs/decisions/0011-luks2-grub-argon2id.md",
            "docs/decisions/0012-signed-apt-repository.md",
            "tests/data/lb_config_trixie_options.txt",
            "SANORA_OS_ARCHITECTURE.md",
        ]
        missing = [p for p in required if not (REPO_ROOT / p).is_file()]
        self.assertEqual(missing, [], f"missing required files: {missing}")

    def test_architecture_document_unchanged(self):
        """The phase-1 approved document must not be silently rewritten."""
        expected = (REPO_ROOT / "tests/data/architecture_doc.sha256").read_text().split()[0]
        actual = hashlib.sha256(
            (REPO_ROOT / "SANORA_OS_ARCHITECTURE.md").read_bytes()
        ).hexdigest()
        self.assertEqual(actual, expected,
                         "SANORA_OS_ARCHITECTURE.md was modified; this requires an explicit ADR")

    def test_lb_config_options_are_verified(self):
        allowed = set()
        for line in (REPO_ROOT / "tests/data/lb_config_trixie_options.txt").read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                allowed.add(line)
        used = set(re.findall(r"--([a-z][a-z0-9-]*)",
                              (REPO_ROOT / "build/live-build/options.sh").read_text()))
        unknown = sorted(used - allowed)
        self.assertEqual(unknown, [],
                         f"unverified lb config options (check trixie lb_config(1)): {unknown}")
        self.assertIn("bootloaders", used)
        self.assertIn("firmware-chroot", used)

    def test_package_list_syntax_and_no_duplicates(self):
        names = package_names()
        self.assertGreater(len(names), 30, "package set suspiciously small")
        self.assertLess(len(names), 120, "package set suspiciously large for a minimal ISO")
        seen = {}
        valid = re.compile(r"^[a-z0-9][a-z0-9+.\-]*$")
        for name, source in names:
            with self.subTest(package=name):
                self.assertRegex(name, valid, f"invalid package name in {source}")
        for name, source in names:
            if name in seen:
                self.fail(f"duplicate package '{name}' in {seen[name]} and {source}")
            seen[name] = source

    def test_no_nvidia_packages(self):
        blocked = [(n, s) for n, s in package_names() if "nvidia" in n.lower()]
        self.assertEqual(blocked, [],
                         "ADR-0007 is BLOCKED; NVIDIA packages must not be in the ISO: "
                         f"{blocked}")
        # Also guard the hooks and the SANORA package payload.
        for path in list((REPO_ROOT / "build/live-build/hooks/normal").glob("*.hook.chroot")) + \
                    list((REPO_ROOT / "packages/sanora-base").rglob("*")):
            if path.is_file() and path.suffix not in {".png"}:
                text = path.read_text(errors="ignore").lower()
                self.assertNotIn("nvidia-", text,
                                 f"NVIDIA component referenced in {path}")

    def test_english_international_defaults(self):
        version = read_version_env()
        self.assertEqual(version["SANORA_DEFAULT_LOCALE"], "en_US.UTF-8")
        self.assertEqual(version["SANORA_DEFAULT_KEYBOARD"], "us")
        options = (REPO_ROOT / "build/live-build/options.sh").read_text()
        # options.sh interpolates the single-source values from version.env.
        self.assertIn("locales=${SANORA_DEFAULT_LOCALE}", options)
        self.assertIn("keyboard-layouts=${SANORA_DEFAULT_KEYBOARD}", options)
        # No country-specific Dutch default may leak into new configuration.
        for path in list((REPO_ROOT / "config").rglob("*")) + \
                    list((REPO_ROOT / "build").rglob("*")):
            if path.is_file() and path.suffix in {"", ".conf", ".sh", ".chroot", ".desc", ".qml"}:
                text = path.read_text(errors="ignore")
                self.assertNotIn("nl_NL", text, f"Dutch locale hardcoded in {path}")

    def test_no_apple_assets_or_branding(self):
        for svg in (REPO_ROOT / "branding").glob("*.svg"):
            with self.subTest(svg=svg.name):
                ET.parse(svg)  # also verifies valid XML
                # Comments legitimately state that Apple assets are NOT used;
                # strip them so only the actual artwork is inspected.
                raw = re.sub(r"<!--.*?-->", "", svg.read_text(), flags=re.S)
                text = raw.lower()
                for forbidden in ("apple", "macos", "cupertino", "finder"):
                    self.assertNotIn(forbidden, text,
                                     f"Apple reference in {svg.name}")
        for png in (REPO_ROOT / "branding").glob("*.png"):
            self.assertTrue(png.read_bytes().startswith(b"\x89PNG\r\n\x1a\n"),
                            f"{png.name} is not a PNG")

    def test_hooks_and_scripts_are_executable(self):
        executable = [
            "build.sh",
            "build/scripts/preflight.sh",
            "build/scripts/build-package.sh",
            "build/scripts/assemble-config.sh",
            "build/scripts/build-repo.sh",
            "build/scripts/write-metadata.py",
            "tests/install/calamares_driver.py",
            "tests/install/qemu_install.py",
            "packages/sanora-base/DEBIAN/preinst",
            "packages/sanora-base/DEBIAN/postrm",
            "packages/sanora-base/usr/bin/sanora-info",
            "tests/run.sh",
        ]
        for rel in executable:
            mode = (REPO_ROOT / rel).stat().st_mode
            self.assertTrue(mode & stat.S_IXUSR, f"{rel} is not executable")

    def test_control_template_has_required_fields(self):
        text = (REPO_ROOT / "packages/sanora-base/DEBIAN/control.in").read_text()
        for field in ("Package:", "Version:", "Architecture:", "Maintainer:",
                      "Description:", "Depends:"):
            self.assertIn(field, text, f"missing {field} in control.in")
        self.assertIn("@SANORA_VERSION@", text)
        version = read_version_env()
        self.assertEqual(version["SANORA_VERSION"], "0.1.0-dev")
        self.assertEqual(version["DEBIAN_SUITE"], "trixie")
        self.assertEqual(version["SANORA_ARCH"], "amd64")

    def test_gitignore_covers_generated_artifacts(self):
        text = (REPO_ROOT / ".gitignore").read_text()
        for entry in ("/out/", "/build/work/", "*.deb"):
            self.assertIn(entry, text, f".gitignore must cover {entry}")

    def test_build_script_clamps_squashfs_mtimes(self):
        text = (REPO_ROOT / "build.sh").read_text()
        self.assertIn("MKSQUASHFS_OPTIONS", text)
        self.assertIn("-all-time", text)
        self.assertIn("SOURCE_DATE_EPOCH", text)

    def test_build_metadata_schema_mentions_nvidia_gate(self):
        text = (REPO_ROOT / "build/scripts/write-metadata.py").read_text()
        self.assertIn("ADR-0007", text)
        self.assertIn("boot_tested", text)

    def test_package_handles_debootstrap_os_release_diversion(self):
        # Verified regression from ISO build #3: debootstrap leaves a local
        # diversion of /etc/os-release that clashes with sanora-base's own.
        preinst = (REPO_ROOT / "packages/sanora-base/DEBIAN/preinst").read_text()
        self.assertIn("os-release.debootstrap", preinst)
        self.assertIn("--local --remove --no-rename", preinst)
        postrm = (REPO_ROOT / "packages/sanora-base/DEBIAN/postrm").read_text()
        self.assertIn("dpkg-divert", postrm)

    def test_calamares_partition_config_uses_luks2(self):
        text = (REPO_ROOT / "installer/calamares/modules/partition.conf").read_text()
        self.assertIn("luksGeneration:", text)
        self.assertIn("luks2", text)
        self.assertIn("userSwapChoices:", text)  # required by the Calamares schema
        self.assertIn("partitionLayout:", text)
        self.assertIn("noEncrypt: true", text)  # unencrypted /boot (ADR-0011)
        self.assertIn('mountPoint: "/boot"', text)

    def test_developer_documentation_exists_and_is_actionable(self):
        required = [
            "docs/development/BUILDING.md",
            "docs/development/REPOSITORY.md",
            "docs/development/TESTING.md",
            "docs/development/PACKAGE_STRATEGY.md",
            "docs/development/BRANDING.md",
            "docs/development/INTERNATIONALIZATION.md",
            "docs/development/SECURITY_BASELINE.md",
            "docs/architecture/STATUS.md",
            "docs/decisions/README.md",
            "docs/decisions/0007-nvidia-in-default-iso.md",
        ]
        missing = [p for p in required if not (REPO_ROOT / p).is_file()]
        self.assertEqual(missing, [], f"missing developer docs: {missing}")
        building = (REPO_ROOT / "docs/development/BUILDING.md").read_text()
        self.assertIn("./build.sh", building)
        self.assertIn("live-build", building)
        status = (REPO_ROOT / "docs/architecture/STATUS.md").read_text()
        self.assertIn("Built | **YES**", status,
                      "status doc must record the verified ISO build")
        self.assertIn("BOOTED", status)
        self.assertIn("BLOCKED", status)


if __name__ == "__main__":
    unittest.main()
