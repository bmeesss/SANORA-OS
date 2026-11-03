# Third-party components and licensing inventory

SANORA OS is an integration project. Almost everything in the image comes from
upstream and keeps its upstream licence. This file records what SANORA OS adds,
what it redistributes by reference, and which legal checks are still open.

> This is an engineering inventory, **not legal advice**. A qualified review is
> required before the first public ISO.

## SANORA-authored material

| Component | Location | Intended licence | Status |
|---|---|---|---|
| Build scripts, tests, helper scripts | `build/`, `build.sh`, `tests/`, `packages/sanora-base/DEBIAN/`, `packages/sanora-base/usr/bin/` | `GPL-2.0-or-later` | chosen in ADR-0006; full text in [LICENSE](LICENSE) |
| Documentation | `README.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, `docs/` | open, **not yet decided** | Q-01 in the architecture document remains open for docs/assets |
| Branding assets (logo, wallpaper, ISO text) | `branding/` | original work by this project, **not yet decided** | no third-party art, no Apple assets |

The `LICENSE` file is the SPDX `GPL-2.0-or-later` text retrieved from
`spdx/license-list-data` (`text/GPL-2.0-or-later.txt`) on 2026-11-01. The
"or later" permission is expressed in the SPDX identifier and in file headers,
not by editing the GPLv2 text.

## Upstream components (used unmodified)

Nothing below is forked. All are installed as unmodified Debian packages from
Debian 13 "trixie" using `apt` at build time.

| Area | Components | Source |
|---|---|---|
| Base | Debian 13 trixie, Linux kernel 6.12 (`linux-image-amd64`), systemd, APT | Debian archive |
| Desktop | KDE Plasma 6.3, KDE Frameworks 6, KWin (`kwin-wayland`), Qt 6, Wayland, XWayland, Mesa, SDDM, Breeze | Debian archive / KDE |
| Audio / network | PipeWire, WirePlumber, NetworkManager, BlueZ | Debian archive |
| Software management | Discover, AppStream, PackageKit, Flatpak, fwupd | Debian archive |
| Installer | Calamares, `calamares-settings-debian`, cryptsetup | Debian archive |
| Build | `live-build`, `debootstrap`, `xorriso`, `squashfs-tools`, syslinux, GRUB EFI | Debian archive (host tools) |
| Security | AppArmor, firewalld, polkit, `unattended-upgrades` | Debian archive |

Upstream licence information for installed packages is available inside the
image at `/usr/share/doc/<package>/copyright`. Debian's DFSG and derivative
guidelines are documented in the phase-1 architecture document §4 and §23.

## Firmware

`live-build` is configured with `--firmware-binary true` and
`--firmware-chroot true`, and `--archive-areas "main contrib non-free-firmware"`.
This pulls firmware packages from Debian's `non-free-firmware` archive area.
Firmware blobs carry **per-blob** redistribution terms; a machine-readable
`firmware-inventory.md` with filename, SHA-256, origin, SPDX identifier and
redistribution condition is still required before any public ISO (phase-1
risk R-08). It is not present yet.

## Explicitly NOT redistributed

- **NVIDIA proprietary driver userspace, GSP firmware and kernel modules.**
  ADR-0007 is still `BLOCKED / awaiting confirmation`. No NVIDIA component is
  listed in `config/packages/`, no `.deb` is vendored, and no hook downloads
  one. See
  [docs/decisions/0007-nvidia-in-default-iso.md](docs/decisions/0007-nvidia-in-default-iso.md).
- Flathub flatpakrepo files / preconfigured third-party remotes. Adding a
  remote by default is an open product decision (Q-09).
- Any Apple asset, trademark, icon, wallpaper, sound or interface copy.
- Any Snap package, Ubuntu trademark material, or Canonical-owned artwork.
- Custom kernels, custom compositors or modified upstream source trees.

## Open legal gates before the first public ISO

1. Legal review of all firmware blobs shipped in the image.
2. NVIDIA Driver License Agreement review, exact driver version pinning,
   GSP-firmware/userspace matching, license text delivery, MOK/Secure Boot
   documentation — only after ADR-0007 is confirmed.
3. Codec, font and AppStream metadata redistribution terms.
4. A decision on the licence for documentation and branding assets.
5. A signed SANORA APT repository and release-signing policy. The build-time
   repository is signed (ADR-0012), but the **release signing key** is still an
   ephemeral development key. Key distribution and rotation are documented in
   [docs/development/RELEASE.md](docs/development/RELEASE.md); a public
   release requires an offline-managed key whose fingerprint is published
   here before any ISO is released.
