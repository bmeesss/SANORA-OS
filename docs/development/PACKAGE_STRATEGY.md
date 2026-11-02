# Package strategy

## Base and channels

- **Base:** Debian 13 "trixie" stable, amd64, archive areas
  `main contrib non-free-firmware` (ADR-0001).
- **Build-time sources:** HTTPS Debian mirrors with `--apt-secure true` and
  `debian-archive-keyring`; `trixie-security` and `trixie-updates` enabled,
  backports disabled.
- **Package manager:** `apt`/`dpkg`. No snap as a default channel.
- **Application channel:** Flatpak (installed, Discover Flatpak backend,
  `kde-config-flatpak` KCM). No remote is preconfigured by default (Q-09).
- **Metadata:** AppStream + PackageKit so Discover can manage Debian packages
  (Q-08 remains an open ADR).
- **Firmware:** `live-build --firmware-binary true --firmware-chroot true`
  pulls firmware from Debian's `non-free-firmware` area. Per-blob legal review
  is a gate before any public ISO.

## The explicit list

`config/packages/*.list.chroot` contains eight lists and **60 unique packages**
(as of 2026-11-01; for the exact current list run
`python3 tests/check_package_names.py`). Each list has one responsibility:

1. `00-base` — live-boot/live-config, live user, `sudo`, locales, trust anchors.
2. `10-plasma` — Plasma on Wayland, KWin, XWayland, SDDM, Breeze, file manager,
   terminal, polkit KDE agent.
3. `20-audio-network` — NetworkManager + plasma-nm, PipeWire + WirePlumber,
   BlueZ + bluedevil.
4. `30-software` — Discover, AppStream, PackageKit, Flatpak, fwupd, Firefox ESR.
5. `40-security` — AppArmor, firewalld, polkit, unattended-upgrades, cryptsetup.
6. `50-hardware` — Mesa userspace, `pciutils`, `usbutils`, `lshw`.
7. `60-i18n-a11y` — Noto/DejaVu/Liberation fonts, emoji, IBus, AT-SPI, Orca.
8. `70-installer` — Calamares, Debian settings, btrfs-progs, squashfs-tools.

Names were individually checked against
`https://packages.debian.org/trixie/<name>` on 2026-11-01.
`tests/check_package_names.py --online` repeats that check when network is
available.

## Why `--apt-recommends true` for now

The Debian Live Manual warns that disabling recommends can remove packages
`live-config` needs (`user-setup`, `sudo`). For the first development ISO,
bootability matters more than size. Reducing recommends is a **measured**
later task: change the flag, inspect live-build's generated `binary.packages`,
diff against the baseline and re-add anything required. No unverified
"optimisation" is applied now.

## Deliberately excluded

- NVIDIA packages of any kind — ADR-0007 is `BLOCKED`.
- Explicit firmware packages (handled by live-build), CPU microcode packages,
  codec bundles, snap/snapd, office suites, games, third-party repos.
- Custom kernels, custom compositors, forks of upstream packages.

## SANORA-owned packages

`packages/sanora-base` is the only SANORA package today. It is a `dpkg-deb`
binary staging tree (no debhelper yet) built reproducibly by
`build/scripts/build-package.sh` and installed by live-build via
`config/packages.chroot/`.

Planned modular split (not implemented): `sanora-defaults`, `sanora-branding`,
`sanora-tools`, `sanora-release`. No giant package.

## Future work

- Replace `packages.chroot` with a **signed local SANORA APT repository** so
  updates are possible and secure APT applies to SANORA packages too (the
  Debian Live Manual notes `packages.chroot` cannot use secure APT).
- Pin package versions for reproducible builds.
- Generate `binary.packages` review and a firmware inventory.
- Decide ADR-0003 / Q-08 (PackageKit) and Q-09 (default apps/Flathub remote).
