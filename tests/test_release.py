"""Offline checks of the release-engineering documentation and invariants."""

import pathlib
import unittest

from helpers import REPO_ROOT


class ReleaseValidation(unittest.TestCase):
    def setUp(self):
        self.release = (REPO_ROOT / "docs/development/RELEASE.md").read_text()
        self.repo = (REPO_ROOT / "build/scripts/build-repo.sh").read_text()
        self.assemble = (REPO_ROOT / "build/scripts/assemble-config.sh").read_text()
        self.harness = (REPO_ROOT / "tests/install/qemu_install.py").read_text()

    def test_release_doc_records_verified_and_not_implemented_state(self):
        for item in (
            "verified", "NOT implemented", "Offline-managed release signing key",
            "Key distribution and rotation", "APT", "Versioning",
        ):
            self.assertIn(item, self.release)

    def test_build_repo_refuses_unsigned_archives(self):
        self.assertIn("refusing to fall back to an unsigned archive", self.repo)
        self.assertIn("--batch --verify", self.repo)
        self.assertIn("Release.gpg", self.repo)
        self.assertIn("InRelease", self.repo)
        self.assertIn("SOURCE_DATE_EPOCH", self.repo)
        self.assertIn("gzip -9 -n", self.repo)

    def test_repo_is_consumed_with_signed_by(self):
        self.assertIn("signed-by=/etc/apt/trusted.gpg.d/sanora.key.chroot.asc", self.assemble)
        self.assertIn("packages.chroot fallback", self.assemble)
        self.assertIn("InRelease", self.assemble)

    def test_installed_system_checks_apt_gpg_and_no_leaked_dev_key(self):
        self.assertIn("apt_verification", self.harness)
        self.assertIn("NO_PUBKEY", self.harness)
        self.assertIn("ephemeral_dev_key_not_trusted_in_installed_system", self.harness)

    def test_dev_key_directory_is_gitignored(self):
        gitignore = (REPO_ROOT / ".gitignore").read_text()
        self.assertIn(".sanora-dev-gnupg", gitignore)

    def test_version_single_source_of_truth(self):
        version_env = (REPO_ROOT / "config/version.env").read_text()
        self.assertIn("SANORA_VERSION=", version_env)
        self.assertIn("SANORA_CODENAME=", version_env)
        self.assertIn("SOURCE_DATE_EPOCH", self.repo)
        # No hardcoded version string in the repo builder; it reads version.env.
        self.assertIn('source "$REPO_ROOT/config/version.env"', self.repo)
        self.assertNotIn("0.1.0-dev", self.repo)


if __name__ == "__main__":
    unittest.main()
