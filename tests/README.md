# Testing

SANORA OS uses an explicit status vocabulary. Nothing in this directory claims
that an ISO boots; boot validation is a manual test until CI has a runner that
can boot a VM.

Statuses: `Implemented`, `Tested`, `Partially tested`, `Planned`, `Blocked`,
`Unknown`.

## Automated, offline

```sh
./build.sh --check       # same as ./tests/run.sh
./tests/run.sh           # full offline suite
```

`tests/run.sh` executes, in order:

| # | Check | What it actually verifies |
|---|---|---|
| 1 | `bash -n` on all shell scripts, hooks and maintainer scripts | shell syntax |
| 2 | `python3 -m py_compile` on all Python modules | Python syntax |
| 3 | `shellcheck -S warning` **if installed** | shell lint; printed as `SKIPPED` when unavailable, never as passed |
| 4 | `check_package_names.py` (offline) | package-list syntax, uniqueness, count |
| 5 | `unittest discover -p 'test_*.py'` | see below |

### `test_static.py`

- All required repository files exist.
- `SANORA_OS_ARCHITECTURE.md` is byte-identical to the approved phase-1
  document (SHA-256 pinned in `tests/data/architecture_doc.sha256`).
- Every `--option` in `build/live-build/options.sh` appears in the transcribed
  trixie `lb_config(1)` synopsis (`tests/data/lb_config_trixie_options.txt`).
  This prevents invented live-build flags.
- Package lists: valid Debian names, no duplicates, 30–120 entries, **no
  NVIDIA packages**, no NVIDIA references in hooks or the SANORA payload.
- English/international defaults: `en_US.UTF-8`, `us`, no `nl_NL` in config.
- Branding SVGs are valid XML and contain no Apple/macOS references in the
  artwork; PNGs have PNG magic bytes.
- Scripts, hooks and maintainer scripts are executable.
- `DEBIAN/control.in` has all required fields and the version placeholder.
- `.gitignore` covers generated artefacts.

### `test_package.py`

Builds `sanora-base` with `dpkg-deb --build` at a fixed `SOURCE_DATE_EPOCH`
and inspects the real `.deb`:

- control fields, expected payload files, root ownership, no developer README
  installed at `/README.md`,
- `/etc/os-release` identity,
- `sanora-info` output against an extracted tree (via `SANORA_ROOT`),
- `sh -n` on maintainer scripts and the helper,
- file mtimes clamped to `SOURCE_DATE_EPOCH`,
- **two consecutive builds produce byte-identical `.deb` files**.

### `test_assemble.py`

Runs the real `build/scripts/assemble-config.sh` into a temporary directory and
validates the exact tree `lb build` would read: eight verbatim package lists,
exactly one `.deb` in `packages.chroot`, two executable hooks, deterministic
`build-info`, ISO medium files, no duplicated branding overlay, no NVIDIA
package, no Dutch locale, and **idempotent assembly** (two runs give identical
file hashes).

### `check_package_names.py --online` (optional, manual)

Queries `https://packages.debian.org/trixie/<name>` for every package and
asserts a real "Details of package" page. Requires network. Network failures are
reported as `UNKNOWN` and make the command exit non-zero — never a silent pass.

```sh
python3 tests/check_package_names.py --online
```

## Manual tests (documented, NOT executed here)

### ISO creation

```sh
sudo apt install live-build debootstrap xorriso squashfs-tools \
                 syslinux-common grub-efi-amd64-bin dosfstools mtools \
                 dpkg-dev git python3
sudo ./build.sh
ls -la out/
sha256sum -c out/SHA256SUMS
```

Record: ISO filename, size, SHA-256, `build-metadata.json` contents, and the
last 50 lines of `build/work/live/build.log`. Update
`docs/architecture/STATUS.md` with the result.

### Basic boot validation (when hardware/VM is available)

1. Boot `out/*.iso` in a UEFI VM (e.g. QEMU/OVMF) and in BIOS/legacy mode.
2. Confirm the bootloader menu appears and shows SANORA OS.
3. Confirm the live session reaches a KDE Plasma **Wayland** desktop:
   `echo $XDG_SESSION_TYPE` must report `wayland`.
4. Confirm `sanora-info` prints SANORA OS identity and English defaults.
5. Confirm Discover opens, AppStream metadata is present, and `fwupd` is
   available (`fwupdmgr --version`).
6. Confirm NetworkManager and PipeWire are running; test Wi-Fi and audio on
   real hardware before claiming support.
7. Start Calamares and confirm the SANORA branding loads without errors and
   that the welcome page shows SANORA OS. **Do not complete an installation on
   a disk with data you need.**
8. Confirm AppArmor status (`aa-status`), firewalld state, and that
   `unattended-upgrades` configuration is present.
9. Record `systemd-analyze` output as a baseline only; do not invent a KPI
   comparison without three runs on three days against stock Debian 13 + Plasma.
10. Test Secure Boot behaviour separately with and without MOK enrollment.

### Reproducibility

Build twice from the same commit on the same host with the same
`SOURCE_DATE_EPOCH`, compare the ISO SHA-256 values, and investigate
differences with `diffoscope`. Debian trixie 13.2 live images were reported as
not fully reproducible by the Debian wiki, so differences are expected and must
be documented rather than hidden.

## What is deliberately NOT tested here

- Booting any ISO, installer completion, LUKS2 encryption, hardware
  compatibility, GPU behaviour, Secure Boot, NVIDIA, performance KPIs,
  translations, or signed repository updates.
- Everything in that list is `Planned`, `Blocked` or `Unknown`; see
  `docs/architecture/STATUS.md`.
