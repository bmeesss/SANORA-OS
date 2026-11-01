# Building a SANORA OS development ISO

This is the developer guide for the `0.1.0-dev` milestone. The output is a
**development** ISO: bootable in principle, not a release, not security
supported and not yet boot-tested in this repository. Check
`docs/architecture/STATUS.md` for the current verified state before you start.

## 1. Requirements

Recommended host: **Debian 13 "trixie" amd64**, because host bootloader tools
must match the target distribution (`live-build` warns that mismatched
syslinux/GRUB tools can produce non-bootable images). A `debian:trixie`
container with `--privileged` also works and is what
`.github/workflows/iso.yml` uses.

| Requirement | Reason |
|---|---|
| root privileges | `lb build` creates a chroot and filesystem images |
| ~20 GB free disk | Debian live images need substantial temporary space (the Debian Live Manual cites ~17 GB for a GNOME image) |
| network access to `deb.debian.org` and `security.debian.org` | `debootstrap` and `apt` download all packages |
| `live-build`, `debootstrap` | upstream Debian build toolchain |
| `xorriso` | ISO9660 image creation |
| `squashfs-tools` | `mksquashfs` for the live filesystem |
| `syslinux-common` | BIOS/isolinux bootloader assets (`/usr/lib/ISOLINUX/isolinux.bin`) |
| `grub-efi-amd64-bin`, `dosfstools`, `mtools` | UEFI bootloader assets |
| `dpkg-dev` (`dpkg-deb`) | building `sanora-base` |
| `git`, `python3`, `curl`, `coreutils` | metadata, scripts and preflight |

Install on Debian trixie:

```sh
sudo apt update
sudo apt install live-build debootstrap xorriso squashfs-tools \
                 syslinux-common grub-efi-amd64-bin dosfstools mtools \
                 dpkg-dev git python3 curl ca-certificates
```

> Host-side caveat: `lb config` may read `/etc/live/build.conf` and
> `/etc/live/build/`. On a shared machine, check those files; SANORA OS does
> not override system-wide live-build defaults silently.

## 2. Commands

```sh
./build.sh --help           # usage
./build.sh --check          # offline validation, no root/network needed
./build.sh --config-only    # build sanora-base + assemble config tree, offline
sudo ./build.sh             # full ISO build into ./out/
./build.sh --clean          # remove build/work and clear out/
SANORA_SKIP_NETWORK_CHECK=1 sudo ./build.sh   # only if you know the mirror is local
./build.sh --config-only --skip-network-check # flags may be combined
```

`./build.sh` is the **only** supported build entrypoint. There is no custom ISO
builder: it calls upstream `lb config` and `lb build`.

## 3. What `./build.sh` does, step by step

Nothing important is hidden in an undocumented script. Each step and its file:

| Step | Action | Script / input |
|---|---|---|
| 1 | Verify host dependencies, root, bootloader assets and mirror reachability | `build/scripts/preflight.sh` |
| 2 | Build `sanora-base_<version>_all.deb` with `dpkg-deb --build` | `build/scripts/build-package.sh` → `packages/sanora-base/` |
| 3 | Run `lb config` with the canonical options in a clean work dir | `build/live-build/options.sh` |
| 4 | Copy SANORA inputs into the generated `config/` tree | `build/scripts/assemble-config.sh` |
| 5 | Run `lb build` (bootstrap → chroot → binary → ISO) | upstream live-build |
| 6 | Copy the ISO and live-build checksum file into `out/` | `build.sh` |
| 7 | Write `build-metadata.json` and `SHA256SUMS` | `build/scripts/write-metadata.py` |

On failure, `build.sh` still writes `out/build-metadata.json` with
`"status": "failed"` and the error text. It never reports success without an
ISO.

### Script reference

| Script | Purpose | Inputs | Outputs |
|---|---|---|---|
| `preflight.sh` | fail fast with actionable messages | `config/version.env`, host state | log lines, exit code |
| `build-package.sh` | assemble a `dpkg-deb` staging tree in a temp dir | `packages/sanora-base`, `config/`, `branding/`, `installer/`, `config/version.env` | `build/work/packages/*.deb` |
| `assemble-config.sh` | deterministic copy/mapping, no live-build needed | package lists, hooks, built `.deb`, `branding/iso/` | `build/work/live/config/` |
| `write-metadata.py` | JSON metadata + checksums | repo, `config/packages/`, `out/` | `out/build-metadata.json`, `out/SHA256SUMS` |

### Config tree mapping

`lb config` generates `config/common`, `config/bootstrap`, `config/chroot`,
`config/binary`, `config/source`. Those are **never committed**. SANORA inputs
are then overlaid:

| Source | Destination |
|---|---|
| `config/packages/*.list.chroot` | `config/package-lists/` |
| `build/work/packages/*.deb` | `config/packages.chroot/` |
| `build/live-build/hooks/normal/*.hook.chroot` | `config/hooks/normal/` |
| generated build identity | `config/includes.chroot/etc/sanora/build-info` |
| `branding/iso/README.txt`, `disk-info` | `config/includes.binary/README.txt`, `.disk/info` |

All other SANORA files (release metadata, `/etc` defaults, KDE defaults,
Calamares branding, logo, wallpaper, `sanora-info`) are delivered by the
`sanora-base` Debian package — one copy, one owner.

### Hooks

| Hook | Action |
|---|---|
| `0010-sanora-locale.hook.chroot` | write `/etc/locale.gen` + `/etc/default/locale`, run `locale-gen` for `en_US.UTF-8` |
| `0020-sanora-calamares-branding.hook.chroot` | switch `/etc/calamares/settings.conf` from `branding: debian` to `branding: sanora` (documented patch; Calamares has no drop-in for that key) |

## 4. Output

```
out/
├── sanora-0.1.0-dev-amd64.iso     (only after a successful build)
├── build-metadata.json             (always, also on failure)
├── SHA256SUMS                      (checksums of artifacts that exist)
└── live-build-SHA256SUMS           (live-build's own checksum file, if present)
```

`build-metadata.json` records: product/version, Debian suite and architecture,
desktop, kernel policy, default language/keyboard, git commit,
`SOURCE_DATE_EPOCH`, live-build version, host OS/architecture, SHA-256 of every
package list, the `sanora-base` .deb, and the ISO (filename, size, SHA-256).
It contains explicit gates: `nvidia_in_iso`, `boot_tested`,
`reproducibility_verified`.

## 5. Reproducibility

- `SOURCE_DATE_EPOCH` defaults to the current git commit timestamp
  (`git log -1 --format=%ct`), never the wall clock; override with an
  environment variable for a pinned build.
- `build.sh` exports `TZ=UTC`, `LC_ALL=C`, `LANG=C`.
- `build-package.sh` clamps all staged file mtimes to `SOURCE_DATE_EPOCH`, so
  the `.deb` is byte-identical across rebuilds (tested in `test_package.py`).
- `lb config` uses `--checksums sha256`, `--utc-time true`, `--zsync false`,
  `--source false` and fixed ISO metadata.
- **Not yet verified:** full ISO reproducibility. The Debian wiki reports
  trixie 13.2 live images were not fully reproducible (boot screens /
  firmware patterns). `diffoscope` comparison of two ISO builds is a later
  task, not a claim.

## 6. Troubleshooting

| Symptom | Cause / action |
|---|---|
| `[preflight] MISSING: command 'lb' not found` | install `live-build` |
| `E: Unable to locate package live-build` | `apt update` failed; check network/mirror |
| `Debian mirror unreachable` | egress restriction or proxy; use a local mirror and override `SANORA_DEBIAN_MIRROR` in `config/version.env` |
| `lb build` fails in `bootstrap_debootstrap` | mirror, keyring or `non-free-firmware` area issue; inspect `build/work/live/build.log` |
| `mksquashfs` / `xorriso` error | missing `squashfs-tools` / `xorriso` |
| Bootloader warnings | host syslinux/GRUB version mismatch; build on trixie |
| No `.iso` after `lb build` | `build.sh` reports this explicitly instead of succeeding |

## 7. After a successful build

1. `sha256sum -c out/SHA256SUMS`.
2. Read `out/build-metadata.json`.
3. Follow the manual boot checklist in `tests/README.md`.
4. Update `docs/architecture/STATUS.md` with the real ISO filename, size,
   checksum and boot result. **Never** claim "it boots" without step 3.

## 8. CI

- `.github/workflows/validate.yml` — on every push/PR: pinned ShellCheck,
  `./build.sh --check`, `./build.sh --config-only`. No ISO.
- `.github/workflows/iso.yml` — `workflow_dispatch`, published releases and a
  weekly schedule only; runs in a privileged `debian:trixie` container and
  uploads the ISO. It has **not** been executed yet.

See `docs/development/TESTING.md` for the test matrix.
