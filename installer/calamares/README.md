# Calamares installer configuration

SANORA OS uses **upstream Calamares unmodified** (`calamares` +
`calamares-settings-debian` from Debian trixie). There is no fork, no custom
module and no reimplemented installer.

## What SANORA OS supplies

`branding/sanora/` is a Calamares branding component installed by
`sanora-base` at `/etc/calamares/branding/sanora/`:

| File | Purpose |
|---|---|
| `branding.desc` | Product name, window size, colours, URLs, logo, slideshow |
| `show.qml` | Minimal installation slideshow; sentences use `qsTr()` |
| `sanora-logo.png` | Copied from `branding/sanora-logo.png` at package build time |

`branding.desc` uses `${NAME}`, `${VERSION_ID}`, `${HOME_URL}` and
`${BUG_REPORT_URL}` from `/etc/os-release`, so there is one source of truth for
version and identity (Calamares supports this substitution).

## The one documented patch

Debian's `calamares-settings-debian` ships `/etc/calamares/settings.conf` with
`branding: debian` **and** the Debian-specific module sequence and module
configuration (`unpackfs`, `bootloader`, `fstab`, ...). Calamares has a single
top-level settings file with no drop-in directory for that key. Rather than
forking the Debian config, hook
`build/live-build/hooks/normal/0020-sanora-calamares-branding.hook.chroot`
changes only `branding: debian` to `branding: sanora`. This is an explicit,
documented patch to an upstream-supplied configuration file — not a source
modification.

## Partitioning and LUKS2 (Phase 3)

`modules/partition.conf` is shipped by `sanora-base` at
`/etc/calamares/modules/partition.conf`. It uses only Calamares 3.3.14's own
verified keys (ADR-0010, ADR-0011):

- `luksGeneration: luks2` and `enableLuksAutomatedPartitioning: true`
- `partitionLayout` with an **unencrypted `/boot` ext4** (`noEncrypt: true`)
  and a LUKS2-encrypted ext4 root; Calamares prepends the EFI System Partition
  automatically on UEFI
- `initialPartitioningChoice: erase`, `initialSwapChoice: none`,
  `efi.mountPoint: /boot/efi`, 300 MiB recommended ESP
- `cryptsetup-initramfs` is installed so the initramfs unlocks the root volume

Calamares has no PBKDF key, and GRUB 2.12 cannot unlock LUKS2 with Argon2id.
The separate `/boot` means GRUB reads the kernel from plain ext4 and never
needs to unlock the volume, so Argon2id can be kept. PBKDF2 was investigated
and rejected (weaker KDF, would need custom scripting). See ADR-0011.

## Installation validation

`tests/install/qemu_install.py` boots the ISO in a disposable UEFI QEMU VM with
an empty qcow2 disk, starts Calamares, and drives the GUI with
`tests/install/calamares_driver.py` (AT-SPI widget discovery + xdotool, no
hardcoded coordinates). It then reboots **from the disk only** and validates
`/etc/os-release`, `sanora-info`, the created user, locale, keyboard, GPT/ESP,
GRUB, `cryptsetup luksDump`, Wayland and the SANORA theme. The workflow is
`.github/workflows/install.yml` (reads the source ISO run id from
`.github/INSTALL_TEST_TRIGGER`). A running Calamares process is not treated as
success; see `docs/architecture/STATUS.md` for the actual verified result.

## What is NOT implemented yet

- Btrfs + Snapper rollback configuration, OEM setup, online log uploading.
- A fully encrypted `/boot` (Secure Boot / own shim would be required).
- Localised installer text beyond upstream translations.

## Upstream references

- Calamares branding keys and `settings.conf` structure: the archived upstream
  GitHub repository `calamares/calamares` (`src/branding/default/branding.desc`,
  `settings.conf`), retrieved 2026-11-01.
- Debian trixie package `calamares` 3.3.14-1 and
  `calamares-settings-debian` 13.0.13-1:
  <https://packages.debian.org/trixie/calamares>.
- The architecture document notes the GitHub Calamares repo is archived since
  2025-08-18 and that Codeberg is the canonical upstream; phase 4 must
  re-validate installer documentation against the current Codeberg docs.
