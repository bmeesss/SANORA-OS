"""Offline validation of the Phase 3.1 LUKS2 / graphical-session harness.

These tests validate that the automation and the evidence requirements are
present. They do NOT claim an encrypted installation or a graphical session
worked — that can only be established by the QEMU CI run.
"""

import pathlib
import unittest

from helpers import REPO_ROOT


class InstallHarnessValidation(unittest.TestCase):
    def setUp(self):
        self.driver = (REPO_ROOT / "tests/install/calamares_driver.py").read_text()
        self.harness = (REPO_ROOT / "tests/install/qemu_install.py").read_text()
        self.partition = (REPO_ROOT / "installer/calamares/modules/partition.conf").read_text()
        self.workflow = (REPO_ROOT / ".github/workflows/install.yml").read_text()

    def test_partition_config_targets_luks2_with_unchecked_checkbox(self):
        self.assertIn("luksGeneration:                       luks2", self.partition)
        self.assertIn("enableLuksAutomatedPartitioning:      true", self.partition)
        self.assertIn("preCheckEncryption:                   false", self.partition)
        self.assertIn("noEncrypt: true", self.partition)
        self.assertIn('mountPoint: "/boot"', self.partition)

    def test_driver_automates_encrypt_checkbox_and_both_passphrases(self):
        # `En&crypt system` -> Alt+E (Calamares 3.3.14 EncryptWidget.ui).
        self.assertIn("alt+e", self.driver)
        self.assertIn("enable_encryption", self.driver)
        self.assertIn("filled both passphrases", self.driver)
        self.assertIn('"Passphrase": "luks"', self.driver)
        self.assertIn('"Confirm passphrase": "luks"', self.driver)

    def test_driver_refuses_plain_result_in_luks_mode(self):
        self.assertIn("crypto_LUKS", self.driver)
        self.assertIn("Encrypt system was not enabled", self.driver)
        self.assertIn("luks_created", self.driver)

    def test_driver_uses_calamares_install_mnemonic(self):
        # Verified: ViewManager.cpp tr("&Install", "@button").
        self.assertIn("alt+i", self.driver)
        self.assertIn("Do NOT force AT_SPI_BUS_ADDRESS", self.driver)

    def test_harness_requires_wrong_passphrase_rejection(self):
        self.assertIn("installed-wrong-passphrase", self.harness)
        self.assertIn("wrong_passphrase", self.harness)
        self.assertIn("no key available", self.harness)
        self.assertIn("WRONG", self.harness)

    def test_harness_checks_luks_header_crypttab_and_initramfs(self):
        for item in (
            "cryptsetup luksDump",
            "/etc/crypttab",
            "lsinitramfs",
            "dmsetup ls --target crypt",
            "initramfs_crypto",
        ):
            self.assertIn(item, self.harness)

    def test_harness_starts_a_graphical_session(self):
        for item in (
            "hmp_send_text",
            "sendkey ret",
            "sddm",
            "graphical_session_source",
            "SDDM autologin",
            "plasmashell",
            "XDG_SESSION_TYPE=wayland",
        ):
            self.assertIn(item, self.harness)

    def test_harness_validates_desktop_components(self):
        for item in (
            "WALLPAPER_PRESENT",
            "org.kde.plasma.taskmanager",
            "org.kde.plasma.kickoff",
            "dolphin konsole plasma-discover flatpak fwupdmgr",
            "WIREPLUMBER",
            "NETWORKMANAGER",
        ):
            self.assertIn(item, self.harness)

    def test_validation_sections_are_named_not_positional(self):
        self.assertIn("VALIDATE_SECTIONS", self.harness)
        self.assertIn('for i, key in enumerate(keys)', self.harness)

    def test_workflow_runs_both_scenarios(self):
        self.assertIn("--mode luks", self.workflow)
        self.assertIn("--mode plain", self.workflow)
        self.assertIn("wrong-passphrase-serial.txt", self.workflow)

    def test_no_real_secrets_are_hardcoded(self):
        # Only disposable-VM test passphrases; no private keys or tokens.
        combined = self.driver + self.harness + self.partition
        for forbidden in ("BEGIN PGP PRIVATE KEY BLOCK", "ghp_", "github_pat_"):
            self.assertNotIn(forbidden, combined)


if __name__ == "__main__":
    unittest.main()
