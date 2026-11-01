"""Assemble and validate the live-build config tree without live-build.

This is the strongest offline test: it runs the real assembly script and
checks the exact tree that `lb build` would consume.
"""

import hashlib
import pathlib
import stat
import tempfile
import unittest

from helpers import BUILD_EPOCH, REPO_ROOT, build_package, run


def tree_digest(root: pathlib.Path) -> dict:
    result = {}
    for path in sorted(root.rglob("*")):
        if path.is_file():
            rel = str(path.relative_to(root))
            result[rel] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


class AssembleValidation(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        build_package()
        cls.tmp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.tmp.cleanup)
        cls.live = pathlib.Path(cls.tmp.name) / "live"
        cls.conf = cls.live / "config"
        cls.env = {
            "SOURCE_DATE_EPOCH": BUILD_EPOCH,
            "SANORA_BUILD_ID": "test-0001",
        }
        result = run(
            ["bash", str(REPO_ROOT / "build/scripts/assemble-config.sh"), str(cls.live)],
            env=cls.env,
        )
        if result.returncode != 0:
            raise AssertionError(f"assemble-config.sh failed:\n{result.stdout}\n{result.stderr}")

    def test_package_lists_are_copied_verbatim(self):
        source = {p.name: p.read_bytes()
                  for p in (REPO_ROOT / "config/packages").glob("*.list.chroot")}
        self.assertEqual(len(source), 8)
        for name, data in source.items():
            target = self.conf / "package-lists" / name
            self.assertTrue(target.is_file(), f"missing {name}")
            self.assertEqual(target.read_bytes(), data, f"{name} was altered")

    def test_exactly_one_deb_in_packages_chroot(self):
        debs = list((self.conf / "packages.chroot").glob("*.deb"))
        self.assertEqual(len(debs), 1, f"expected one .deb, found {debs}")
        self.assertEqual(debs[0].name, "sanora-base_0.1.0-dev_all.deb")

    def test_hooks_are_present_and_executable(self):
        hooks = sorted((self.conf / "hooks/normal").glob("*.hook.chroot"))
        self.assertEqual(len(hooks), 2)
        for hook in hooks:
            self.assertTrue(hook.stat().st_mode & stat.S_IXUSR,
                            f"{hook.name} not executable")

    def test_build_info_is_deterministic(self):
        content = (self.conf / "includes.chroot/etc/sanora/build-info").read_text()
        self.assertIn("SANORA_BUILD_ID=test-0001", content)
        self.assertIn(f"SOURCE_DATE_EPOCH={BUILD_EPOCH}", content)
        self.assertIn("DEBIAN_SUITE=trixie", content)
        self.assertIn("SANORA_DEFAULT_LOCALE=en_US.UTF-8", content)
        self.assertNotIn("@", content)

    def test_iso_medium_files(self):
        readme = (self.conf / "includes.binary/README.txt").read_text()
        self.assertIn("0.1.0-dev", readme)
        self.assertNotIn("@SANORA_VERSION@", readme)
        self.assertTrue((self.conf / "includes.binary/.disk/info").is_file())

    def test_branding_is_delivered_only_by_the_package(self):
        # No duplicated overlay copy of assets that sanora-base already owns.
        self.assertFalse(
            (self.conf / "includes.chroot/usr/share/sanora").exists(),
            "branding assets must come from the package, not a second overlay",
        )
        self.assertFalse(
            (self.conf / "includes.chroot/etc/xdg/kdeglobals").exists(),
            "KDE defaults must come from the package, not a second overlay",
        )

    def test_no_nvidia_packages_in_assembled_config(self):
        for lst in (self.conf / "package-lists").glob("*.list.chroot"):
            for line in lst.read_text().splitlines():
                if line.strip() and not line.strip().startswith("#"):
                    self.assertNotIn("nvidia", line.lower(),
                                     f"NVIDIA package in {lst.name}")

    def test_no_dutch_locale_in_assembled_config(self):
        for path in self.conf.rglob("*"):
            if path.is_file() and path.suffix != ".deb" and path.suffix != ".png":
                self.assertNotIn("nl_NL", path.read_text(errors="ignore"),
                                 f"Dutch locale hardcoded in {path}")

    def test_assembly_is_idempotent(self):
        before = tree_digest(self.conf)
        result = run(
            ["bash", str(REPO_ROOT / "build/scripts/assemble-config.sh"), str(self.live)],
            env=self.env,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        after = tree_digest(self.conf)
        self.assertEqual(before, after,
                         "assembling twice produced different config trees")


if __name__ == "__main__":
    unittest.main()
