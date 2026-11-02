# SANORA OS — implementation status (updated 2026-11-02)

This is the verified state after the **Build and Boot Validation phase**.
Statuses are used exactly as defined by the project: `Implemented`, `Tested`,
`Partially tested`, `Planned`, `Blocked`, `Unknown`.

The phase-1 research document `SANORA_OS_ARCHITECTURE.md` is Dutch and remains
unchanged (SHA-256 pinned and enforced by `tests/test_static.py`). All new
documentation, configuration, code and UI text is English. ADR-0007 (NVIDIA)
remains `BLOCKED` and no NVIDIA component was added.

## Headline result

**A real SANORA OS ISO was built by `./build.sh` (Debian live-build) in a
Debian 13 trixie CI container and booted successfully in QEMU under both UEFI
and legacy BIOS, reaching KDE Plasma on Wayland with the SANORA identity.**

The authoritative evidence is GitHub Actions run
`41469346725` (commit `2f6a8bd9b08432c40a275bf395d54932c10b16dd`), whose job
`Build ISO and boot it in QEMU` completed **success** with every step green.
Complete build output is published as the `SANORA build diagnostics` check run;
the ISO, metadata, boot JSONs, screenshots and logs are uploaded as the
`sanora-iso-and-evidence` artifact.

| Area | Status | Evidence |
|---|---|---|
| Repository inspection (branch, history, existing files) | `Tested` | `git log`, `git ls-files`, `git fetch` at task start |
| Real Debian trixie build environment | `Tested` | `container: debian:trixie --privileged` in `.github/workflows/iso.yml`; live-build `20250505+deb13u1` |
| `./build.sh` full ISO build | `Tested` | step 7 of run `41469346725`: success |
| ISO artifact | `Tested` | `out/sanora-0.1.0-dev-amd64.iso` |
| UEFI boot | `Tested` | `out/boot-uefi/boot-validation.json`: `status: BOOTED` |
| Legacy BIOS boot | `Tested` | `out/boot-bios/boot-validation.json`: `status: BOOTED` |
| KDE Plasma + Wayland | `Tested` | `kwin_wayland`, `startplasma-wayland`, `XDG_SESSION_TYPE=wayland`, `loginctl` session type `wayland` |
| SANORA identity / metadata | `Tested` | `cat /etc/os-release`, `sanora-info`, branding files, Calamares branding |
| Network / audio / apps | `Tested` | NetworkManager active, IP `10.0.2.15`, PipeWire/WirePlumber active, Dolphin/Konsole/Discover/fwupd present |
| English default + additional locale | `Tested` | `en_US.UTF-8` default; `nl_NL.UTF-8` generated and `sanora-info` run under it |
| Calamares start + disk detection | `Tested` | Calamares process running, `lsblk` detects `sr0` (ISO) and `loop0` (squashfs) |
| LUKS2 installer configuration | `Implemented` + `Partially tested` | `/etc/calamares/modules/partition.conf` with `luksGeneration: luks2` present and read in the guest; ADR-0010 |
| Encrypted installation + reboot | `Not tested` | no installation was performed |
| Wallpaper display | `Not tested` / unresolved | assets and defaults present, but Plasma overwrote the `/etc/skel` config; see below |
| ISO reproducibility | `Tested` (negative result) | two same-commit builds differ; byte-level diff analysed |
| Performance baseline | `Tested` | `systemd-analyze`, `free -m`, load average, process count captured |
| NVIDIA | **`Blocked`** | ADR-0007 still awaiting confirmation; no NVIDIA packages |
| Signed SANORA repo, own shim, public release | `Planned` | not present |

## ISO BUILD (verified)

| Field | Value |
|---|---|
| Built | **YES** |
| Filename | `sanora-0.1.0-dev-amd64.iso` |
| Size | `2,392,113,152` bytes (2.39 GB) |
| SHA-256 | `4b601d434e2d430d53b7900039fae77261b0c9b31d0f84133849874b28461ad2` |
| Build commit | `2f6a8bd9b08432c40a275bf395d54932c10b16dd` |
| Build date (from `SOURCE_DATE_EPOCH`) | `2026-11-02T15:12:42Z` |
| `SOURCE_DATE_EPOCH` | `1793632362` |
| Base | Debian 13.7 (`trixie`), amd64 |
| Kernel | `6.12.113+deb13-amd64` (Debian kernel, unmodified) |
| KDE Plasma | `4:6.3.6-1` (`plasma-desktop`, `plasma-workspace 4:6.3.6-2`, `kwin-wayland 4:6.3.6-1`) |
| SDDM | `0.21.0+git20250502.4fe234b-2` |
| Calamares | `3.3.14-1` |
| live-build | `20250505+deb13u1` |
| Installed packages | `1743` |
| Build tool | Debian `live-build` (`lb config` / `lb build`), no custom builder |

Earlier successful builds: run `41462790740` (commit `4f95e50`, SHA-256
`f60388ad8d941315ec0ab871b52a06bf8ccea1b209120b23877e5da866e423c3`) and run
`41458963136` (commit `3aba266`, SHA-256
`e074a1421f38416207250abf8387d70f74cbd8238b6b353d908ba107508a9d26`).

## BOOT TEST (verified, QEMU/KVM)

VM: 4096 MiB RAM, 2 vCPUs, `-vga std`, OVMF (`/usr/share/qemu/OVMF.fd`) for
UEFI / SeaBIOS for BIOS, user-mode networking (e1000), `intel-hda`,
`-display none` with `screendump` framebuffer capture.

| Check | UEFI | BIOS |
|---|---|---|
| Kernel loaded | `true` | `true` |
| Serial login shell | `true` | `true` |
| Boot to shell | `29.2 s` | `39.0 s` |
| Boot menu screenshot | 800×600, non-blank | 640×480, non-blank |
| Desktop screenshot | 1280×800, non-blank | 1280×800, non-blank |
| KDE Plasma (`plasmashell`, `kwin_wayland`) | `true` | `true` |
| Wayland (`XDG_SESSION_TYPE=wayland`, `loginctl Type=wayland`) | `true` | `true` |
| Network (NetworkManager active + IP) | `true` | `true` |
| Audio subsystem (pipewire/pipewire-pulse/wireplumber active) | `true` | `true` |
| Discover / fwupd / Dolphin / Konsole | `true` | `true` |
| `/etc/os-release` = SANORA OS | `true` | `true` |
| `sanora-info` correct | `true` | `true` |
| Branding files present | `true` | `true` |
| English default | `true` | `true` |
| `nl_NL.UTF-8` usable | `true` | `true` |
| Calamares starts | `true` | `true` |
| Disk detection | `true` | `true` |
| `cryptsetup` present | `true` | `true` |
| LUKS2 config present | `true` | `true` |

Note on `echo $XDG_SESSION_TYPE`: from the **serial login shell** it is `tty`
(expected). Inside the graphical session it is `wayland`, verified from
`/proc/<kwin_wayland>/environ` and `loginctl show-session -p Type`. No claim is
made that the serial shell itself is a Wayland session.

Note on audio: the guest PipeWire stack is active; QEMU's host ALSA backend
emitted warnings because the CI container has no sound card. No physical audio
output was verified.

## INSTALLER / LUKS2

- Calamares starts, SANORA branding config is selected
  (`branding: sanora` in `/etc/calamares/settings.conf`), modules load and the
  VM disk (`sr0` / `loop0`) is detected.
- `installer/calamares/modules/partition.conf` now sets
  `luksGeneration: luks2`, `enableLuksAutomatedPartitioning: true`, EFI System
  Partition parameters (`/boot/efi`, 300 MiB / 32 MiB) and the schema-required
  `userSwapChoices`. See ADR-0010.
- **An encrypted installation and a reboot into the installed system were NOT
  performed.** Therefore LUKS2 is reported as `FAIL / NOT TESTED` for the
  installation criterion. Additional known risk: upstream Calamares documents
  that GRUB does not support LUKS2 with Argon2id (only PBKDF2); this must be
  resolved before encrypted installs can be claimed working.

## REPRODUCIBILITY (verified negative)

Two builds of the **same commit** (`2f6a8bd`) with the same
`SOURCE_DATE_EPOCH` were performed inside run `41469346725`.

| First ISO SHA-256 | Second ISO SHA-256 | Identical |
|---|---|---|
| `3a56afa69ae3e493fd2152a022f72678dcd3cfb9086b01e3f390adbb59b905cb` | `4b601d434e2d430d53b7900039fae77261b0c9b31d0f84133849874b28461ad2` | **NO** |

`build-metadata.json` was identical between the two builds **except** for the
resulting `artifact.sha256` — so build inputs, git commit,
`SOURCE_DATE_EPOCH`, package-list hashes and measured versions were all
identical. The divergence is in the ISO payload, not in the metadata.

Byte-level comparison (`cmp -l`, `od` hexdump) found the first differing byte
at offset `13,715,491`, inside the **squashfs superblock / table-offset area**
of `/live/filesystem.squashfs` (the `hsqs` magic is visible 28 bytes into the
dump), plus further differences around offsets `167,983,147` and `167,986,700`.
The `mkfs_time` field is identical, so `SOURCE_DATE_EPOCH` is being honoured
for that field; the differences are in squashfs internal table offsets / inode
data. Known candidates: apt list timestamps, `/var/lib/dpkg` state,
`update-initramfs` output, firmware file ordering, and locale/certificate
archives. This is consistent with the phase-1 note that Debian trixie live
images were not fully reproducible.

`diffoscope` was **not** run (not installed in the CI container). A full
diffoscope comparison of the two squashfs filesystems is the next task for this
area; no files were manipulated to make checksums match.

## PERFORMANCE BASELINE (measured, not an achievement)

Recorded inside the UEFI QEMU VM (4096 MiB RAM, 2 vCPU, KVM, OVMF, user-mode
network). Baseline only; no comparison against stock Debian was made and no
optimisation was applied.

| Metric | Measured value |
|---|---|
| `systemd-analyze` | kernel `4.174 s` + userspace `13.339 s` = `17.513 s` |
| `graphical.target` | `13.339 s` in userspace |
| Boot to serial shell (harness timer) | `29.2 s` (UEFI), `39.0 s` (BIOS) |
| `free -m` | total `3915`, used `1472`, free `1654`, shared `114`, buff/cache `1126`, available `2442` MiB |
| Load average | `2.41 0.56 0.19` |
| Processes | `190` |

## FIXES made during this phase (all verified)

1. **Workspace restoration** — the `build/` directory was excluded from the
   workspace snapshot; restored from `origin/arena/fa064594-sanora-os` before
   any change.
2. **CI trigger** — `workflow_dispatch` is unavailable to the repository token
   (HTTP 403). Added a `push` trigger on the dedicated marker
   `.github/ISO_BUILD_TRIGGER` so a real ISO build can be requested reliably.
3. **Missing Debian package** — `isolinux` (not `syslinux-common`) provides
   `/usr/lib/ISOLINUX/isolinux.bin`; added to CI install list and corrected
   `BUILDING.md` and the preflight message.
4. **`sanora-base` install failure (real build #3 failure)** —
   `dpkg-divert: error: 'diversion of /etc/os-release to
   /etc/os-release.debian by sanora-base' clashes with 'local diversion of
   /etc/os-release to /etc/os-release.debootstrap'`. `debootstrap` leaves that
   local diversion; live-build removes it in `chroot_hacks`, but only after
   packages are installed. `DEBIAN/preinst` now removes it first using
   live-build's own command. A regression test was added.
5. **False build-step failure** — `tee build/work/build-full.log` opened its
   output before `build/work` existed in a fresh checkout, so the step was
   reported as failed even though `./build.sh` produced a valid ISO. Fixed with
   `mkdir -p build/work` before the pipeline; run `41462790740` and
   `41469346725` are fully green.
6. **CI diagnostics** — full build output is published as a readable
   `SANORA build diagnostics` check run, because this sandbox cannot fetch
   Actions logs/artifacts from Azure blob hosts.
7. **Git metadata** — added `safe.directory` so `SOURCE_DATE_EPOCH`, git commit
   and build ID are real values in `build-metadata.json`.
8. **Calamares would not start** — Qt 6.5+ needs `libxcb-cursor0` on X11/XWayland
   and the guest needs the SDDM `XAUTHORITY`; added the package and fixed the
   launch environment. Calamares is now observed running.
9. **LUKS1 default** — Debian's Calamares settings ship no `partition.conf`;
   added a SANORA one using Calamares' own `luksGeneration: luks2` key (ADR-0010).
10. **`cryptsetup` false negative** — the binary lives in `/usr/sbin`, outside a
    normal user's PATH; the guest check now verifies `/usr/sbin/cryptsetup`.
11. **Measured versions and package count** — added `collect-versions.sh` and
    merged `versions` / `installed_package_count` into `build-metadata.json`.
12. **Wallpaper default (partial fix, still unresolved)** — Plasma overwrote the
    `/etc/skel` config on first start; a copy under `/etc/xdg` was added too,
    but the guest check still reports the default is not effective. Requires a
    Plasma Global Theme layout script (next phase), not another config copy.

## Genuine remaining blockers / gaps

1. **ADR-0007 (NVIDIA)** — still `BLOCKED`; no confirmation, no legal review,
   no NVIDIA components.
2. **Encrypted installation + reboot** — not performed; needs an automated
   Calamares GUI run in a disposable VM and a GRUB/LUKS2 PBKDF2 decision.
3. **Wallpaper display** — needs an original KDE Plasma Global Theme with a
   `org.kde.plasma.desktop-layout.js` layout script (a new feature, deferred).
4. **Full ISO reproducibility** — two same-commit builds differ inside the
   squashfs; diffoscope analysis and mitigation are outstanding.
5. **Signed SANORA APT repository** — local `.deb` delivery via
   `packages.chroot` still cannot use secure APT.
6. **Local sandbox** still has no `live-build` and no Debian mirror access; real
   builds happen only in the CI container.

## Next implementation phase (5 tasks)

1. Automate a disposable-VM Calamares installation (UEFI/GPT/ESP/LUKS2) and
   reboot into the installed system; resolve GRUB + LUKS2 PBKDF2.
2. Run `diffoscope` on the two same-commit ISOs, list every non-reproducible
   file, and fix the squashfs inputs with upstream-supported mechanisms.
3. Create the original SANORA KDE Global Theme (layout script setting the
   wallpaper) and set `LookAndFeelPackage` accordingly.
4. Set up a signed local SANORA APT repository and remove `packages.chroot`.
5. Decide ADR-0007; only then consider NVIDIA licensing, driver pinning and
   MOK/Secure Boot work.
