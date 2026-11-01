# SANORA OS

SANORA OS is an independent, **international** Linux distribution for everyday
desktop use. It is built on Debian 13 "trixie" (amd64) with KDE Plasma on
Wayland. English is the default system language, documentation language, UI
terminology and default user experience; the design is intentionally not tied
to any country so that more languages can be added later.

SANORA OS does not reinvent Linux. It reuses upstream Debian, the Linux kernel,
KDE Plasma, KDE Frameworks, KWin, Qt, Wayland, XWayland, Mesa, systemd,
NetworkManager, PipeWire, WirePlumber, AppArmor, fwupd, Flatpak, AppStream,
Discover, Calamares and `live-build`. SANORA-owned work is limited to
integration, configuration, branding, defaults, system tooling, installer
experience, documentation and quality assurance.

> **Status: development foundation (`0.1.0-dev`).** The first milestone is a
> bootable *development ISO*, not a release. Do not use it as a daily driver.
> See [docs/development/BUILDING.md](docs/development/BUILDING.md) for the
> build, and [docs/architecture/STATUS.md](docs/architecture/STATUS.md) for an
> honest implemented / tested / blocked overview.

## Quick start

```sh
# On a Debian 13 (trixie) amd64 host with internet access:
sudo apt install live-build debootstrap xorriso squashfs-tools \
                 syslinux-common grub-efi-amd64-bin dosfstools mtools \
                 dpkg-dev git python3
./build.sh --check          # offline validation, no root or network needed
sudo ./build.sh              # build the ISO into ./out/
```

`./build.sh` is the single supported entrypoint. It verifies host dependencies,
configures Debian + Plasma + Wayland, installs the explicit SANORA package set,
builds the `sanora-base` Debian package, applies SANORA configuration and
branding, calls `lb build`, and writes the ISO plus `build-metadata.json` into
`out/`. Every step is documented in
[docs/development/BUILDING.md](docs/development/BUILDING.md).

On a machine without `live-build` (including restricted CI sandboxes),
`./build.sh --config-only` still assembles and validates the complete
`live-build` configuration tree and builds the SANORA package offline.

## Project layout

| Path | Purpose |
|---|---|
| `build.sh` | Developer entrypoint for validation and ISO builds |
| `build/live-build/` | Canonical `lb config` options and chroot hooks |
| `build/scripts/` | Preflight, package build, config assembly, metadata |
| `config/packages/` | Explicit, reviewed package lists |
| `config/desktop/` | KDE / Plasma system defaults |
| `config/system/` | `/etc` defaults, live-config, security baseline |
| `branding/` | Original SANORA SVG/PNG assets and ISO text |
| `packages/sanora-base/` | The first SANORA Debian package |
| `installer/calamares/` | Calamares branding (installer is upstream) |
| `tests/` | Offline test suite (`tests/run.sh`) |
| `.github/` | Static-validation CI; ISO builds are manual/release-only |
| `docs/development/` | Build, repository, testing, branding, i18n docs |
| `docs/decisions/` | English ADRs and the decision index |
| `SANORA_OS_ARCHITECTURE.md` | Phase-1 research document (Dutch, historical) |

The phase-1 architecture document is written in Dutch and is kept unchanged as
a historical record. All new documentation, code, configuration and UI text is
English. Translating or superseding that document is a separate, explicit task.

## Licensing

SANORA-authored **source code** is licensed `GPL-2.0-or-later`; see
[LICENSE](LICENSE). Documentation and branding assets are covered by
[THIRD_PARTY.md](THIRD_PARTY.md) until a separate documentation/asset license
is decided. Upstream components keep their own licenses. Nothing from Apple is
copied: SANORA OS is an original identity, not a macOS clone.

## Known blockers

- **NVIDIA in the default ISO (ADR-0007) is not implemented.** The architecture
  document still marks this decision as requiring confirmation and a legal /
  Secure Boot review. Per the project stop conditions, NVIDIA components are
  **not** bundled and the decision is flagged, not made silently. See
  [docs/decisions/0007-nvidia-in-default-iso.md](docs/decisions/0007-nvidia-in-default-iso.md).
- An ISO has not yet been built in this development environment: the sandbox
  has no `live-build` and no access to Debian package mirrors. See
  [docs/architecture/STATUS.md](docs/architecture/STATUS.md) for the exact
  failure and the fix.
- There is no SANORA APT repository, no signed release channel, no own Secure
  Boot shim and no published release yet.

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md), [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
and [SECURITY.md](SECURITY.md) before opening a pull request. Small,
verifiable changes are preferred. Never claim a test passed unless it ran.

---

SANORA OS — quality over speed.
