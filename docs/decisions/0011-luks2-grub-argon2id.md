# ADR-0011 — LUKS2, GRUB and Argon2id: separate unencrypted /boot

- **Status:** Accepted 2026-11-02. Implements the already-approved LUKS2
  installer requirement (ADR-0010 / phase-1 §12.5); no approved architecture
  decision is changed.
- **Context:** The installer target is UEFI + GPT + EFI System Partition +
  LUKS2 + a Linux filesystem. Calamares 3.3.14 (Debian trixie) exposes
  `luksGeneration: luks2` but **no** configuration key for the LUKS2 PBKDF.
  `cryptsetup luksFormat --type luks2` defaults to an **Argon2id** keyslot.
  GRUB 2.12 in Debian trixie can unlock LUKS2 volumes only when the keyslot
  uses **PBKDF2**; it cannot unlock Argon2id. Calamares' own upstream
  `partition.conf` documents exactly this limitation.
- **Decision:** Keep the LUKS2 root with Argon2id (the stronger KDF) and add an
  explicit **unencrypted `/boot` ext4 partition** through Calamares'
  supported `partitionLayout` mechanism (`noEncrypt: true`). GRUB reads the
  kernel and initramfs from plain ext4 and never has to unlock the root volume.
  `cryptsetup-initramfs` is installed so the initramfs can unlock the LUKS2
  root at boot. PBKDF2 is therefore **not required** and not forced.
- **PBKDF2 alternative (rejected for v1):** converting the LUKS2 keyslot to
  PBKDF2 (`cryptsetup luksConvertKey --pbkdf pbkdf2`) would let GRUB unlock an
  encrypted `/boot`. Rejected because (a) Calamares does not expose the option,
  so it would need a custom post-partitioning script; (b) PBKDF2 is a weaker,
  GPU-friendly KDF than Argon2id and would reduce resistance to offline
  passphrase brute-force; (c) it does not remove the need for an initramfs
  unlock path. It remains an option for a later ADR if a fully encrypted
  `/boot` is ever required.
- **Other alternatives considered:** LUKS1 (rejected: does not meet the LUKS2
  requirement); forking `calamares-settings-debian` (rejected: maintenance
  burden); writing a custom disk-management tool (explicitly excluded).
- **Security implications (documented, not hidden):**
  - `/boot` is unencrypted: kernel, initramfs, GRUB config and any embedded
    keyfile are readable by anyone with physical access to the disk. The LUKS2
    root volume remains encrypted and protected by the passphrase.
  - An attacker could replace the initramfs on an unencrypted `/boot` (evil
    maid) unless Secure Boot validates the chain. SANORA OS does not yet have
    its own signed shim (phase-1 R-01), so this is a known residual risk.
  - This is the same trade-off Debian and most distributions make when using
    LUKS2 with GRUB.
- **Verification:** The configuration is shipped in the ISO and read by
  Calamares. An encrypted installation followed by a reboot must be performed
  in a disposable QEMU VM before LUKS2 is reported as working; see
  `docs/architecture/STATUS.md` for the current result.
- **References:** Calamares v3.3.14 `src/modules/partition/partition.conf`,
  `partition.schema.yaml`, `core/PartitionLayout.cpp`; Debian trixie
  `calamares` 3.3.14-1, `cryptsetup` 2:2.7.5-2.
