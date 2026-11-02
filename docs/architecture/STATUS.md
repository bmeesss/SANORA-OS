# SANORA OS — implementation status (2026-11-01)

This is the honest state of the repository after the **implementation
kickoff**. It replaces guesses with evidence. Statuses are used exactly as
defined by the project: `Implemented`, `Tested`, `Partially tested`, `Planned`,
`Blocked`, `Unknown`.

The phase-1 research document `SANORA_OS_ARCHITECTURE.md` is Dutch and remains
unchanged (SHA-256 pinned in `tests/data/architecture_doc.sha256`). All new
documentation, configuration, code and UI text is English. SANORA OS is an
international distribution; English is the default.

## Summary

SANORA OS now has a real, versioned, testable build foundation: a Debian
`live-build` configuration, an explicit package set, a real Debian package
(`sanora-base`), original branding, Calamares branding, an offline test suite
and CI. **An ISO has NOT been built in this environment** and nothing has been
boot-tested. The failure is environmental (no `live-build`, no Debian mirror
access), is recorded below, and is not hidden.

| Area | Status | Evidence |
|---|---|---|
| Repository inspection (branch, history, existing files) | `Tested` | `git log`, `git ls-files`, `find` at task start; branch `arena/fa064594-sanora-os`, 3 pre-existing commits, 2 tracked files |
| Repository structure | `Implemented` | `build/`, `config/`, `branding/`, `packages/`, `installer/`, `tests/`, `docs/`, `.github/` — all contain real files, no empty placeholders |
| `live-build` option set | `Implemented` + `Tested` offline | `build/live-build/options.sh`; every option checked against trixie `lb_config(1)` by `test_static.py` |
| Build entrypoint `./build.sh` | `Implemented` + `Partially tested` | `--check`, `--config-only`, `--clean` executed successfully; full ISO path blocked at preflight |
| `sanora-base` Debian package | `Implemented` + `Tested` | built with `dpkg-deb --build`; `test_package.py` builds, extracts and inspects it; byte-reproducible across two builds |
| Config tree assembly | `Implemented` + `Tested` | `test_assemble.py` runs the real script, checks idempotence and exact tree contents |
| Package selection | `Implemented` + `Partially tested` | 8 lists, 60 unique packages, syntax/duplicates/NVIDIA-free checked offline; names individually checked against packages.debian.org on 2026-11-01; not installed on a real system |
| Branding (logo, wallpaper, ISO text) | `Implemented` + `Partially tested` | original SVG + PNG assets committed; PNG magic bytes and SVG XML validated; visual appearance inspected; not seen on a booted desktop |
| KDE default theme/wallpaper wiring | `Partially tested` | `/etc/xdg/kdeglobals` and `/etc/skel` config set; documented as best-effort and **not boot-verified** |
| Calamares branding | `Implemented` + `Partially tested` | branding component shipped by package; hook switches `branding:` key; installer never launched |
| Security baseline (packages/config) | `Implemented` + `Not tested` | AppArmor/firewalld/polkit/unattended-upgrades/cryptsetup selected; no enforcement or boot verification |
| LUKS2 through the installer | `Planned` | `cryptsetup` is installed, Calamares encryption module is **not configured** |
| NVIDIA in the ISO | **`Blocked`** | ADR-0007 still `ter bevestiging` in the architecture doc; see below |
| ISO creation | **`Failed / Blocked`** | exact failure below |
| ISO boot, hardware compatibility, Wayland session, Secure Boot | `Unknown` / `Planned` | no boot test performed; no hardware claims made |
| Reproducibility | `Partially tested` | `sanora-base` .deb and config assembly are byte-reproducible; ISO reproducibility unverified |
| Signed SANORA APT repository, own shim, release | `Planned` | not present |
| CI | `Implemented` + `Not executed` | workflows written; GitHub Actions has not run them yet |
| Translation catalogues | `Planned` | gettext infrastructure in `sanora-info`, no `.po`/`.mo` files yet |

## ISO — exact result of the build attempt

**Result: FAILED. No ISO exists. `out/` contains only `build-metadata.json`
with `"status": "failed"` and an empty `SHA256SUMS`.**

Attempts, in order:

1. `./build.sh` (default ISO mode) → exit 1 at **Step 1/7 host preflight**.
   Exact preflight output:
   ```
   [preflight] host: debian 12
   [preflight] user: uid=1001
   [preflight] MISSING: root privileges required for 'lb build'; run: sudo ./build.sh
   [preflight] MISSING: command 'lb' not found
   [preflight] MISSING: command 'debootstrap' not found
   [preflight] MISSING: command 'xorriso' not found
   [preflight] MISSING: command 'mksquashfs' not found
   [preflight] MISSING: asset '/usr/lib/ISOLINUX/isolinux.bin' not found
   [preflight] MISSING: asset directory '/usr/lib/grub/x86_64-efi' not found
   [preflight] MISSING: Debian mirror unreachable: https://deb.debian.org/debian/dists/trixie/Release
   [preflight] FAILED.
   ```
   `build.sh` wrote `out/build-metadata.json` with
   `"error": "host preflight failed ..."` rather than pretending success.

2. `sudo -E ./build.sh` → exit 1. Root check now passes (`uid=0`), but the
   same missing tools, bootloader assets and unreachable mirror remain. This
   proves the failure is **not** just a permissions issue.

3. `sudo apt-get install -y live-build debootstrap xorriso squashfs-tools` →
   exit 100: `E: Unable to locate package live-build` (and the other three).
   `apt-get update -qq` itself fails with
   `W: Failed to fetch http://deb.debian.org/debian/dists/bookworm/InRelease
   Connection failed [IP: 151.101.194.132 80]`.

4. Direct probe `curl https://deb.debian.org/debian/dists/trixie/Release` →
   `curl: (35) OpenSSL SSL_connect: SSL_ERROR_SYSCALL`, HTTP code `000`.
   Plain HTTP gives `curl: (52) Empty reply from server`. The sandbox permits
   outbound traffic only to `github.com`, `codeload.github.com`,
   `api.github.com`, `registry.npmjs.org`, `pypi.org` and
   `files.pythonhosted.org`; Debian mirrors are not reachable.

5. Investigated substituting upstream `live-build` from
   `https://github.com/debian-live/live-build`. That repository is a 2015
   snapshot (`VERSION 5.0~a11-1`) and its `scripts/build/config` contains
   **zero** occurrences of `--bootloaders` and `--uefi-secure-boot`. It uses
   the older singular `--bootloader` option set and cannot build the trixie
   configuration in `options.sh`. It was therefore **not** used, and no custom
   ISO builder was written.

**Likely cause:** sandbox network egress restrictions plus a Debian 12 host
without the live-build toolchain. This is an environment limitation, not a
defect proven in the SANORA configuration. The configuration itself has not
been executed by `lb config`/`lb build`, so its runtime correctness remains
`Unknown`.

**Fix / verification still required:** on a Debian 13 trixie amd64 host (or the
`debian:trixie` container in `.github/workflows/iso.yml`) with network access:
```sh
sudo apt install live-build debootstrap xorriso squashfs-tools \
                 syslinux-common grub-efi-amd64-bin dosfstools mtools \
                 dpkg-dev git python3 curl
sudo ./build.sh
sha256sum -c out/SHA256SUMS
```
Then boot the ISO and update this file. **The fix has NOT been verified.**

**What was changed in response to this failure** (all implemented, none of
them a fake success):

1. `build/scripts/preflight.sh` now checks every required command, bootloader
   asset, root privileges and mirror reachability **before** `lb build`, and
   exits with an actionable message instead of a cryptic late failure.
2. `build.sh` writes `out/build-metadata.json` with `"status": "failed"` and
   the error text on failure, so a failed build cannot be mistaken for a pass.
3. `.github/workflows/iso.yml` runs the build in a privileged
   `debian:trixie` container with the full toolchain, on manual/release/schedule
   triggers only. That workflow is the intended place to complete the build;
   it has not been executed yet.
4. `./build.sh --config-only` and `./build.sh --check` were added so the entire
   `live-build` configuration, package and metadata can be built and validated
   **offline**, which is how this repository was verified despite the network
   restriction.

**Whether the fix was verified:** No. Only the offline portion was verified;
`lb build` itself has never run here. The ISO remains `Failed / Blocked`.

## Genuine blockers

1. **ADR-0007 — NVIDIA in the default ISO is `BLOCKED`.**
   `SANORA_OS_ARCHITECTURE.md` §0.5 lists ADR-0007 as `Ter bevestiging` and
   Bijlage A.2 explicitly asks for confirmation before any ISO/package/installer
   configuration. The kickoff instruction says to stop that specific
   implementation and flag it instead of deciding it. Consequently: no
   `nvidia-*` package, driver, firmware or MOK handling is in the package set,
   hooks or `sanora-base`. See `docs/decisions/0007-nvidia-in-default-iso.md`.
   Everything else in the foundation proceeded as instructed.
2. **ISO build environment**: no `live-build` and no Debian mirror in this
   sandbox (details above).
3. **Legal review before any public ISO**: firmware blobs from
   `non-free-firmware`, branding/documentation licence, and NVIDIA licensing
   if ADR-0007 is confirmed. See `THIRD_PARTY.md`.

## Explicitly not claimed

- "ISO successfully built" — false.
- "Boot tested successfully" — false.
- "Hardware is supported" — false. Package selection uses upstream open
  drivers and Debian firmware, but no device has been tested.
- "Wayland session works" — untested. Debian trixie's `sddm` is still
  described as an X11 display manager; session selection must be boot-verified.
- "LUKS2 installer works" — false; only `cryptsetup` is installed.
- "AppArmor/firewalld/Secure Boot are enforced" — untested.
- "Two ISO builds are reproducible" — unverified.

## Next implementation phase (3–7 concrete tasks)

1. Run `./build.sh` on a networked Debian trixie host/container, capture the
   real `lb config` + `lb build` logs, and fix any option/package errors.
2. Boot the resulting ISO in a UEFI VM and in BIOS mode; confirm
   `XDG_SESSION_TYPE=wayland`, `sanora-info`, Discover and Calamares branding.
3. Validate Calamares 3.3.14 configuration against current Codeberg docs; add
   LUKS2 module configuration and an installer dry-run test.
4. Confirm ADR-0007 (or revert to opt-in) and, if confirmed, do the legal +
   MOK/Secure Boot review before adding any NVIDIA component.
5. Replace the best-effort `/etc/skel` wallpaper with an original KDE Plasma
   Global Theme and set `LookAndFeelPackage` accordingly.
6. Add a signed local SANORA APT repository (replacing `packages.chroot`) and
   `diffoscope` reproducibility comparison for the ISO.
7. Add the first translation catalogue (`sanora-base.mo`) and a locale smoke
   test for a non-English locale.
