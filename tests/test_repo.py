"""Offline validation of the signed SANORA APT repository wiring."""

import unittest

from helpers import REPO_ROOT


class RepoValidation(unittest.TestCase):
    def test_build_repo_script_is_complete(self):
        script = (REPO_ROOT / "build/scripts/build-repo.sh").read_text()
        for item in (
            "apt-ftparchive", "Release.gpg", "InRelease", "Release",
            "Packages.gz", "sanora-archive-key.asc", "--detach-sign",
            "--clearsign", "--verify", "SOURCE_DATE_EPOCH",
            "SANORA_REPO_KEY_ID", "SANORA_REPO_AUTO_KEY",
        ):
            self.assertIn(item, script, f"build-repo.sh missing {item}")
        self.assertIn("refusing to fall back to an unsigned archive", script)

    def test_assemble_config_wires_signed_repository(self):
        script = (REPO_ROOT / "build/scripts/assemble-config.sh").read_text()
        for item in (
            "archives/sanora.list.chroot",
            "archives/sanora.key.chroot",
            "sanora-repo.list.chroot",
            "signed-by=/etc/apt/trusted.gpg.d/sanora.key.chroot.asc",
            "file://",
            "packages.chroot fallback",
        ):
            self.assertIn(item, script, f"assemble-config.sh missing {item}")

    def test_build_script_calls_repo_builder(self):
        script = (REPO_ROOT / "build.sh").read_text()
        self.assertIn("build-repo.sh", script)
        self.assertIn("Step 2b/7", script)

    def test_repo_documentation_exists(self):
        for path in ("repo/README.md", "docs/decisions/0012-signed-apt-repository.md"):
            self.assertTrue((REPO_ROOT / path).is_file(), path)

    def test_ci_enables_ephemeral_key_and_diffoscope(self):
        iso = (REPO_ROOT / ".github/workflows/iso.yml").read_text()
        self.assertIn("SANORA_REPO_AUTO_KEY", iso)
        self.assertIn("diffoscope", iso)
        self.assertIn("gnupg", iso)


if __name__ == "__main__":
    unittest.main()
