# ADR-0010 — LUKS2 configuration for the Calamares installer

- **Status:** Implemented (configuration), **not validated by an installed
  system boot**. Proposed 2026-11-02, accepted as an implementation of the
  already-approved security baseline (phase-1 §12.5 / ADR-0005); no approved
  architecture decision is changed.
- **Context:** The project requires LUKS2 support through the installer for a
  UEFI + GPT + EFI System Partition + LUKS2 + Linux filesystem layout. QEMU
  boot test #5 proved that Debian trixie's `calamares-settings-debian`
  13.0.13-1 ships **no** `/etc/calamares/modules/partition.conf`; Calamares
  therefore uses its compiled defaults, which specify `luksGeneration: luks1`.
  `cryptsetup` 2:2.7.5-2 was present, and Calamares 3.3.14-1 started.
- **Decision:** Ship a minimal SANORA-owned
  `/etc/calamares/modules/partition.conf` through `sanora-base`, using only
  Calamares' own documented module keys. No custom partitioning code. The file
  sets `luksGeneration: luks2`, `enableLuksAutomatedPartitioning: true`, the
  EFI System Partition parameters (`/boot/efi`, 300 MiB recommended,
  32 MiB minimum) and the schema-required `userSwapChoices`. Calamares'
  automated "Erase disk" partitioning on UEFI creates the GPT and ESP.
- **Alternatives considered:**
  1. Do nothing and accept LUKS1 — rejected, does not meet the requirement.
  2. Fork/patch `calamares-settings-debian` — rejected, creates a maintenance
     burden and breaks Debian package upgrades.
  3. Write a custom disk-management script — explicitly rejected by the task.
  4. Use a Calamares `partitionLayout` preset — more complex, still relies on
     the same module; deferred until automated installation is validated.
- **Consequences / known risk:** Upstream Calamares documents that GRUB does
  not support LUKS2 with Argon2id and supports LUKS2 only with PBKDF2. A
  Calamares-created LUKS2 volume may therefore fail to unlock at boot on
  GRUB-based systems. This must be resolved (PBKDF2 key derivation, or a
  separate `/boot`) **before** encrypted installation can be claimed working.
  It requires an actual VM installation followed by a reboot, which has not
  been performed.
- **Verification status:** The config file is present in the ISO and checked
  by `tests/test_static.py` and the QEMU guest checks. Disk detection in the
  VM is verified. **Installation, unlocking and reboot are NOT verified.**
- **References:** Calamares `src/modules/partition/partition.conf`,
  `partition.schema.yaml` and `Config.cpp` (upstream source tree, retrieved
  2026-11-02); Debian trixie packages `calamares` 3.3.14-1 and
  `calamares-settings-debian` 13.0.13-1.
