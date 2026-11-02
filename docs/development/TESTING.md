# Testing

Full test documentation, including the manual boot checklist, lives in
[`tests/README.md`](../../tests/README.md). This page is the short developer
summary.

## Run offline (no root, no network, no live-build)

```sh
./build.sh --check          # equivalent to ./tests/run.sh
./tests/run.sh              # full offline suite
python3 tests/check_package_names.py            # list package names
python3 tests/check_package_names.py --online  # verify against packages.debian.org
```

## What is automated today

| Area | Test | Status |
|---|---|---|
| Shell syntax | `bash -n` on 11 scripts/hooks/maintainer scripts | executed, passing |
| Python syntax | `py_compile` on 5 modules | executed, passing |
| Shell lint | `shellcheck -S warning` (ShellCheck 0.11.0, pinned in CI) | executed locally with 0.11.0, passing; printed as `SKIPPED` if unavailable |
| `lb config` options | subset of transcribed trixie `lb_config(1)` synopsis | executed, passing |
| Package lists | syntax, uniqueness, count, no NVIDIA | executed, passing |
| i18n defaults | `en_US.UTF-8`, `us`, no `nl_NL` | executed, passing |
| Branding | SVG XML validity, PNG magic, no Apple references in artwork | executed, passing |
| Architecture doc | SHA-256 pinned, unchanged | executed, passing |
| `sanora-base` | build, extract, control fields, payload, ownership, os-release, `sanora-info` output, mtime clamping, byte-reproducibility | executed, passing |
| Config assembly | real script run in temp dir, exact tree, idempotence, no NVIDIA, no duplicate overlays | executed, passing |
| Documentation | required files present, `.gitignore` coverage, metadata gates present | executed, passing |

Final offline run: **32 unit tests + shell/Python syntax + ShellCheck + package
list check, all executed and passing** (`2026-11-02`). Two assertions initially
failed because they checked literal strings while the code uses quoted
`os-release` values and `version.env` interpolation; the assertions were
corrected and the suite re-run. This is a test fix, not a product fix, and is
recorded here for transparency.

## Automated in CI (verified runs `41462790740` and `41469346725`)

`tests/boot/qemu_boot.py` boots the real ISO in QEMU for UEFI and legacy BIOS,
drives the guest serial console with `pexpect`, captures framebuffer screenshots
via the QEMU human monitor, runs guest-side checks (`cat /etc/os-release`,
`sanora-info`, `loginctl`, `pgrep kwin_wayland`, `systemctl`, `fwupdmgr`,
`locale-gen`, Calamares start, `lsblk`, performance commands) and writes
`boot-validation.json` with explicit booleans. Both modes reported
`status: BOOTED`. The same workflow performs a second build of the same commit
and writes `reproducibility.json` plus byte-level diffs.

## What is NOT automated / NOT verified

- Local ISO creation in this sandbox (no `live-build`, no Debian mirror); real
  builds happen only in the CI container.
- Completing a Calamares installation, LUKS2 unlock and reboot into the
  installed system.
- Secure Boot/MOK, GPU, Wi-Fi/Bluetooth and physical audio output on real
  hardware; AppArmor/firewalld enforcement at runtime.
- Wallpaper display (Plasma overwrites the shipped config — see
  `docs/development/BRANDING.md`).
- Full `diffoscope` comparison of the two ISOs; only `cmp`/`od` byte-level
  analysis was run.
- Translation catalogues and KPI comparisons against stock Debian 13 + Plasma.

## Rules

- A test that did not run is reported as `SKIPPED` or `Unknown`, never as
  passed.
- `out/build-metadata.json` is written at build time and therefore keeps
  `boot_tested: false` / `reproducibility_verified: false`; the **actual** boot
  evidence is in `out/boot-*/boot-validation.json` and
  `out/reproducibility.json`. Do not treat the build-time flags as the final
  verdict.
- After any real ISO build, record filename, size, SHA-256 and boot result in
  `docs/architecture/STATUS.md`.
