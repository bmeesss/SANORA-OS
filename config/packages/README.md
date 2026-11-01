# SANORA OS package set

This directory is the **explicit, reviewed** list of packages installed in the
development ISO. `build/scripts/assemble-config.sh` copies every
`*.list.chroot` file into live-build's `config/package-lists/`. One package per
line; `#` starts a comment. live-build installs these with `apt` (the default,
which fails the build on a missing package — deliberate).

## Principles

- No metapackage that silently drags in hundreds of applications.
- No fork of an upstream package. Everything comes unmodified from Debian 13
  `trixie` (`main`, `contrib`, `non-free-firmware`).
- Each list has one responsibility so that a reviewer can see why a package is
  there. Comments record the reason, not just the name.
- Package names were checked against `https://packages.debian.org/trixie/<name>`
  on 2026-11-01. `tests/check_package_names.py --online` re-checks them in CI.
- `--apt-recommends true` is used for this first ISO to maximise the chance of
  a bootable desktop. Reducing recommends is a **measured** later task (phase-1
  KPI plan §11); it is not guessed at here.

## Files

| File | Responsibility |
|---|---|
| `00-base.list.chroot` | live-boot, live-config, live user, locales, trust anchors |
| `10-plasma.list.chroot` | KDE Plasma on Wayland, SDDM, file manager, terminal |
| `20-audio-network.list.chroot` | NetworkManager, PipeWire, Bluetooth |
| `30-software.list.chroot` | Discover, AppStream, PackageKit, Flatpak, fwupd, browser |
| `40-security.list.chroot` | AppArmor, firewalld, polkit, unattended-upgrades, cryptsetup |
| `50-hardware.list.chroot` | Mesa userspace and hardware reporting tools |
| `60-i18n-a11y.list.chroot` | Fonts, input method, screen reader, AT-SPI |
| `70-installer.list.chroot` | Calamares and its Debian settings |

## Deliberately absent

- **Anything NVIDIA** (`nvidia-*`, `libnvidia-*`, CUDA, proprietary driver
  packages). ADR-0007 is `BLOCKED / awaiting confirmation` in the architecture
  document. `tests/test_static.py` fails if an NVIDIA package appears here.
  See `docs/decisions/0007-nvidia-in-default-iso.md`.
- Explicit firmware packages. live-build's `--firmware-binary true` and
  `--firmware-chroot true` pull firmware from Debian's `non-free-firmware`
  area; see `THIRD_PARTY.md` for the still-open per-blob legal review.
- Snap / snapd, Steam, office suites, games, codec bundles, CPU microcode
  packages and third-party repositories (Q-08 / Q-09 remain open).
- A preconfigured Flathub remote. Flatpak is installed, but adding a remote by
  default is a product decision; the documented manual command is
  `flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo`.

## Known open decisions affecting this list

- Q-08 (PackageKit as the APT backend for Discover): `packagekit` is installed
  provisionally so Discover can manage Debian packages. This is not yet a
  ratified ADR-0003 implementation.
- Q-09 (default applications/localisation): only English defaults and one
  browser are included.
- Q-03 (minimum hardware) and Q-05 (Plasma version) are not yet decided; the
  ISO currently uses trixie's Plasma 6.3.6 and Debian's 6.12 kernel.
