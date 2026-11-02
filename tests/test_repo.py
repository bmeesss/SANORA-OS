"""Offline validation of the signed SANORA APT repository wiring."""

import os
import pathlib
import shutil
import subprocess
import tempfile
import unittest

from helpers import BUILD_EPOCH, REPO_ROOT, build_package


class RepoValidation(unittest.TestCase):

    def test_build_repo_generates_signed_archive_with_stubbed_tools(self):
        """Exercise the whole generator flow offline with CLI test doubles."""
        stub = REPO_ROOT / "tests" / "data" / "stubbin"
        work = REPO_ROOT / "build" / "work"
        created = ["repo", "gnupg", "repo-key-id", "repo-metadata.json",
                   "Release.generated"]
        dev_keyring = REPO_ROOT / ".sanora-dev-gnupg"
        def cleanup():
            for name in created:
                p = work / name
                if p.is_dir():
                    shutil.rmtree(p, ignore_errors=True)
                elif p.exists():
                    p.unlink()
            if dev_keyring.is_dir():
                shutil.rmtree(dev_keyring, ignore_errors=True)
        cleanup()
        build_package()  # ensures the .deb exists
        env = os.environ.copy()
        env["PATH"] = f"{stub}{os.pathsep}{env['PATH']}"
        env["SANORA_REPO_AUTO_KEY"] = "1"
        env["SOURCE_DATE_EPOCH"] = BUILD_EPOCH
        try:
            proc = subprocess.run(
                ["bash", str(REPO_ROOT / "build/scripts/build-repo.sh")],
                env=env, cwd=str(REPO_ROOT), capture_output=True, text=True,
            )
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            repo = work / "repo"
            for rel in (
                "pool/main/s/sanora-base/sanora-base_0.1.0-dev_all.deb",
                "dists/sanora/main/binary-amd64/Packages",
                "dists/sanora/main/binary-amd64/Packages.gz",
                "dists/sanora/Release",
                "dists/sanora/Release.gpg",
                "dists/sanora/InRelease",
                "sanora-archive-key.asc",
            ):
                self.assertTrue((repo / rel).is_file(), f"missing {rel}")
            metadata = (work / "repo-metadata.json").read_text()
            self.assertIn('"signature_verified": true', metadata)

            # With a signed repo present, assemble-config.sh must wire it in.
            with tempfile.TemporaryDirectory() as td:
                env2 = os.environ.copy()
                env2.pop("SANORA_FORCE_PACKAGES_CHROOT", None)
                env2["SOURCE_DATE_EPOCH"] = BUILD_EPOCH
                env2["SANORA_BUILD_ID"] = "test-repo"
                res = subprocess.run(
                    ["bash", str(REPO_ROOT / "build/scripts/assemble-config.sh"), td],
                    env=env2, cwd=str(REPO_ROOT), capture_output=True, text=True,
                )
                self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
                conf = pathlib.Path(td) / "config"
                listing = (conf / "archives/sanora.list.chroot").read_text()
                self.assertIn("signed-by=/etc/apt/trusted.gpg.d/sanora.key.chroot.asc",
                              listing)
                self.assertIn("file://", listing)
                self.assertIn("sanora main", listing)
                self.assertTrue((conf / "archives/sanora.key.chroot").is_file())
                self.assertIn(
                    "sanora-base",
                    (conf / "package-lists/sanora-repo.list.chroot").read_text(),
                )
                self.assertEqual(
                    list((conf / "packages.chroot").glob("*.deb")), [],
                    "packages.chroot must not be used when a signed repo exists",
                )
        finally:
            cleanup()

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
