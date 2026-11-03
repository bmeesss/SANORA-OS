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

---

# Phase 3 — Installation & Desktop Experience (updated 2026-11-03)

This section records what was **actually verified** in the Phase 3 CI runs.
Phase 2 results above (ISO build, UEFI/BIOS boot, SANORA identity) remain
valid; Phase 3 adds the desktop identity, signed repository, reproducibility
investigation, baseline comparison and the installer work.

## Verified ISO build

Authoritative run: [`41528961532`](https://github.com/bmeesss/SANORA-OS/actions/runs/41528961532),
commit `48fc6237c793218653bb55c8321bc2f2af6f175f`, all 16 steps green.

| Field | Value |
|---|---|
| ISO | `sanora-0.1.0-dev-amd64.iso` |
| Size | `2,415,919,104` bytes |
| SHA-256 (final/second build) | `3c679a6f6a1ef03c4b0c0c419d78f6c489d534f86b3161bdd5ff89459fcc651f` |
| First same-commit build SHA-256 | `015f49057d93734ce8818637a3d95ba95286b4cd2c792cfe80840f9fc79e393e` |
| Base | Debian 13.7 trixie, amd64 |
| Kernel | `6.12.115+deb13.1-amd64` (unmodified Debian kernel) |
| KDE Plasma | `4:6.3.6-1` |
| Calamares | `3.3.14-1` |
| live-build | `20250505+deb13u1` |
| Installed packages | `1762` |
| Build tool | Debian `live-build` (`lb config` / `lb build`); no custom builder |

Earlier failed attempts and their fixes are listed under "FIXES" below.

## Verified desktop identity (Priority 2)

An original KDE Plasma identity is implemented with KDE's supported extension
mechanisms only: two `Plasma/LookAndFeel` KPackages (light/dark),
`SANORALight.colors` / `SANORADark.colors`, `sanora` / `sanora-dark` icon themes
inheriting upstream Breeze with an original launcher icon, a `sanora` Plasma
desktop theme with `FallbackTheme=default`, and
`contents/layouts/org.kde.plasma.desktop-layout.js` (verified Plasma 6
scripting API: `loadTemplate`, `panels`, `desktopsForActivity`, `writeConfig`).
No Plasma source is modified and no Apple asset is used.

**Clean-account QEMU check** (`out/boot-uefi/theme-checks.txt`, run
`41528961532`, published as check run `125580589395`): with `HOME` and
`XDG_CONFIG_HOME` pointed at an empty directory, `kreadconfig6` resolves to
`org.sanora.light.desktop`, `SANORALight` and icon theme `sanora`. All theme
assets are present, including `/usr/share/sanora/wallpapers/sanora-default.png`
(117,570 bytes). A real bug was found and fixed: the theme referenced
`sanora-default.png` while the package shipped only `sanora-wallpaper.png`;
the package now ships both names.

Not verified: a human visual review of the panel/wallpaper appearance; the
screenshot is captured but not judged here. Breeze KWin decoration, Plasma
style SVGs, splash animation and sound theme are intentionally inherited.

## Verified signed APT repository (Priority 4)

`build/scripts/build-repo.sh` builds a GPG-signed local archive
(`pool/`, `Packages[.gz]`, `Release`, `Release.gpg`, `InRelease`, armoured
public key) and verifies `Release.gpg` with `gpg --verify`; the build fails if
verification fails. `build/scripts/assemble-config.sh` wires it into live-build
through the supported `config/archives/` mechanism
(`deb [signed-by=/etc/apt/trusted.gpg.d/sanora.key.chroot.asc] file://... sanora main`
plus `sanora-base` in a package list). `lb build` installs `sanora-base` from
that signed archive with dependency resolution. The ephemeral development key
lives in `.sanora-dev-gnupg` (Git-ignored) and is stable across the two builds
of the same commit. Offline test `tests/test_repo.py` exercises the whole
generator with CLI test doubles. ADR-0012 documents key management; a public
release still needs an offline-managed key and HTTPS mirror.

## Reproducibility investigation (Priority 3)

`diffoscope` is installed and executed in CI. Two builds of the **same commit**
with the same `SOURCE_DATE_EPOCH` produce different ISOs
(`identical: false`), while `build-metadata.json` is byte-identical except for
`artifact.sha256` — so all build inputs, versions and package-list hashes are
identical.

- `diffoscope`/chroot file-list diff (run `41519403741`) identified the paths
  with wall-clock mtimes: `/var/lib/ucf`,
  `/var/lib/systemd/deb-systemd-user-helper-enabled`, `/var/lib/xml-core`,
  `/var/lib/xkb`, `/var/lib/vim`, dpkg trigger files.
- **`mksquashfs` already reads `SOURCE_DATE_EPOCH`** and clamps squashfs file
  mtimes. An explicit `-all-time` was tried and **rejected**: run
  `41527475099` failed with `FATAL ERROR: SOURCE_DATE_EPOCH and command line
  options can't be used at the same time to set timestamp(s)`. The option was
  removed; no ISO is manipulated post-hoc.
- A full-ISO `diffoscope` run unpacks two 2.4 GB images and **kills the
  GitHub-hosted runner** (runs `41505275082`, `41514773588` failed at that
  step). diffoscope is therefore scoped to the reproducibility evidence
  (chroot file lists, build metadata) and the cheap file-level diff. This is an
  honest environment limitation, documented, not hidden.
- Remaining differences are at ISO/bootloader level or in file contents; they
  are **not yet fully attributed**. No claim of reproducibility is made.

## Performance baseline (Priority 5)

`tests/boot/qemu_baseline.py` boots the official
`debian-live-13.7.0-amd64-kde.iso` with the same VM configuration (4096 MiB,
2 vCPU, KVM, `e1000`, OVMF) and records the same metrics. Result
(`out/baseline/baseline-comparison.json`, `status: MEASURED`, no errors):

| Metric | SANORA dev ISO | Debian 13 KDE | Delta |
|---|---|---|---|
| `systemd-analyze` total | 16.608 s | 19.408 s | −2.8 s |
| Idle RAM used (`free -m`) | 1483 MiB | 419 MiB | +1064 MiB |
| Boot to serial shell | 28.1 s | 21.9 s | +6.2 s |
| Processes | 189 | 134 | +55 |
| Load average | `3.06 0.75 0.25` | `0.79 0.19 0.06` | — |

**Baseline only.** No optimisation was applied and no performance achievement
is claimed. Live-ISO RAM figures include the squashfs page cache on both
systems; the Debian ISO was booted from its own kernel/initrd with a serial
console appended, which is a slightly different boot path. The SANORA ISO has
65 explicitly listed packages but APT resolves to 1762 installed packages, and
Debian KDE uses a different package set — so these are not like-for-like
product comparisons yet.

## Installer (Priority 1) — plain installation and reboot VERIFIED

Implemented:

- `installer/calamares/modules/partition.conf` using verified Calamares 3.3.14
  keys: `luksGeneration: luks2`, `enableLuksAutomatedPartitioning: true`,
  `partitionLayout` with an unencrypted `/boot` ext4 (`noEncrypt: true`) and a
  LUKS2 ext4 root; Calamares prepends the EFI System Partition. ADR-0011
  documents the GRUB/LUKS2/Argon2id investigation (GRUB 2.12 needs PBKDF2;
  Calamares 3.3.14 has no PBKDF key; PBKDF2 was rejected as weaker and
  requiring custom scripting — an unencrypted `/boot` keeps Argon2id and lets
  GRUB read the kernel without unlocking root). `cryptsetup-initramfs`,
  `grub-efi-amd64` and `libxcb-cursor0` are installed.
- `tests/install/qemu_install.py`: disposable UEFI QEMU VM with a 24G qcow2
  disk, persistent OVMF CODE/VARS pflash, serial console, boot-menu Enter
  injection, Calamares launch, GUI driver, power-off and a second boot **from
  the disk only**, with validation of identity, user, locale, GPT/ESP, GRUB,
  LUKS2, Wayland and theme. A running Calamares process is not treated as
  success.
- `tests/install/calamares_driver.py`: AT-SPI widget discovery plus a
  keyboard fallback using the verified Calamares 3.3.14 mnemonics
  (`&Next` = Alt+N, `&Install` = Alt+I), uploaded into the guest from the
  checkout so iterations need no ISO rebuild.
- `.github/workflows/install.yml` (fast, downloads a prior ISO artifact).
  The harness appends `console=ttyS0,115200` to the installed `grub.cfg`
  **for serial-console observability only** — no partition, filesystem or
  package data is altered.

**Verified end-to-end** (run `41629942048`, check run `125901228530`,
`out/install-plain/install-validation.json`):

- Calamares started (`SANORA OS Installer`, 1024x520), the driver navigated
  welcome -> locale -> keyboard -> partition -> users -> summary and activated
  Install. Calamares executed **all 41 jobs** (log shows
  `Starting job "Unmounting file systems..." ( 41 / 41 )`).
  `driver_verdict: SUCCESS`, `installation_completed: true`.
- The VM was powered off and rebooted **from the disk only**. OVMF loaded
  `Boot0008 "SANORA_OS"` -> `\EFI\SANORA_OS\shimx64.efi`.
  `installed_serial_login: true`.
- Installed-system evidence (`installed-checks.txt`):

| Check | Result |
|---|---|
| `/etc/os-release` | `NAME="SANORA OS"`, `ID="sanora"`, `ID_LIKE="debian"`, `DEFAULT_LANGUAGE="en"` |
| `sanora-info` | SANORA OS 0.1.0-dev, Debian 13 trixie, amd64, KDE Plasma (Wayland), Build ID `48fc623-1793655027` |
| User / hostname | `sanora` / `sanora-pc` |
| Locale | `LANG=en_US.UTF-8` |
| GPT layout | `vda1 300M vfat /boot/efi`, `vda2 1G ext4 /boot`, `vda3 22.7G ext4 /` |
| Root mount | `/dev/vda3 ext4 /` |
| GRUB / ESP | `EFI/BOOT/bootx64.efi`, `EFI/SANORA_OS/shimx64.efi`, `grubx64.efi`, `grub.cfg` |
| Global Theme | `org.sanora.light.desktop`, `SANORA_THEME_PRESENT` |
| Boot | `systemd-analyze`: 6.916 s total; `uname`: `Linux sanora-pc 6.12.115+deb13.1-amd64` |

`installed.checks` booleans `true`: `os_release_sanora`, `sanora_info`,
`correct_user`, `english_locale`, `root_filesystem`, `efi_system_partition`,
`grub_installed`, `sanora_theme`, `global_theme_selected`, `luks2` (forced
true for the plain scenario — LUKS is not applicable there).

A second scenario (`--mode luks`, run `41634541077`) also completed an
installation and rebooted into the installed system. **It produced a plain
ext4 root, not a LUKS2 volume**: `lsblk` still shows `vda3 22.7G ext4 /` and
`cryptsetup luksDump /dev/vda3` returns "Device /dev/vda3 is not a valid LUKS
device". The keyboard fallback does not automate the `En&crypt system`
checkbox and the two passphrase fields, so `--encrypt` had no effect. Both
scenarios therefore validate a **plain** installation; the LUKS2 scenario is
mislabelled in `install.yml` and is recorded here as a known gap.

**Not verified / PARTIAL:**

- `wayland: false` in `installed.checks`. Validation logs in over the serial
  console; SDDM was still at the greeter and no graphical user session was
  started, so the installed system's Wayland session was **not** verified.
  Wayland **is** verified on the live ISO by `qemu_boot.py` (session type
  `wayland`, `kwin_wayland` running). This gap is recorded explicitly as
  `installed.wayland_note`; no claim of Wayland on the installed system is
  made.
- **LUKS2 encryption is NOT validated.** No encrypted volume was created in
  either scenario. An encrypted installation with passphrase entry, LUKS2
  unlock at boot and a reboot into the decrypted root has not been performed.
  ADR-0011 remains a design decision, not a verified feature. `luks2: true`
  in the plain scenario's `installed.checks` is forced by the harness because
  LUKS is not applicable there — it is not evidence of encryption.

Overall harness verdict: `status: PARTIAL` — a real installation and a real
boot into the installed system were achieved (twice), with the two gaps above.
The green `install.yml` job exit code means "installation completed and
installed system booted", **not** "all checks passed". The JSON verdicts are
the source of truth.

## Regression tests

`./tests/run.sh`: **49 unit tests + shell syntax + Python syntax + ShellCheck
+ package-list check, all executed and passing** (2026-11-03). The phase-1
architecture document is still byte-identical (SHA-256 pinned). All new
user-facing content is English; the default locale remains `en_US.UTF-8` with
`kreadconfig6` clean-account checks and `nl_NL.UTF-8` still usable.

## Genuine remaining blockers

1. **LUKS2 encrypted installation**: the encryption checkbox, passphrase
   entry, LUKS2 unlock and reboot into the decrypted root are not automated or
   verified. ADR-0011 is still a design decision.
2. **Wayland on the installed system**: the serial-console validation never
   starts a graphical session; a GUI login check (or SDDM Wayland default)
   is needed. Wayland on the live ISO is verified.
3. **Full ISO reproducibility**: two same-commit ISOs still differ; a complete
   two-ISO `diffoscope` needs a runner with >20 GB free. The remaining
   differences are not fully attributed.
4. **Offline-managed release signing key and HTTPS SANORA repository**.
5. **ADR-0007 (NVIDIA)** — still `BLOCKED`, untouched.
6. The local sandbox still has no `live-build`, QEMU or Debian mirror access;
   all real builds and VM tests happen in CI.

## Next 5 tasks

1. Automate the LUKS2 scenario (Encrypt checkbox + passphrase fields) and
   verify `cryptsetup luksDump`, passphrase unlock and reboot.
2. Validate the installed graphical Wayland session (GUI login or SDDM default
   session) and the SANORA theme in that session.
3. Run full-ISO `diffoscope` on a larger runner and attribute/fix the remaining
   nondeterministic inputs with upstream-supported mechanisms.
4. Introduce an offline release signing key and a published signed SANORA APT
   repository.
5. Decide ADR-0007; only then consider NVIDIA licensing, driver pinning and
   MOK/Secure Boot work.
