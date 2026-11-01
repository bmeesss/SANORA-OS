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

Final offline run: **30 unit tests + shell/Python syntax + ShellCheck + package
list check, all executed and passing** (`2026-11-01`). Two assertions initially
failed because they checked literal strings while the code uses quoted
`os-release` values and `version.env` interpolation; the assertions were
corrected and the suite re-run. This is a test fix, not a product fix, and is
recorded here for transparency.

## What is NOT automated

- ISO creation (blocked in this sandbox by missing `live-build` and no Debian
  mirror; see `docs/architecture/STATUS.md`).
- Boot validation, installer completion, LUKS2, Secure Boot/MOK, GPU and
  Wi-Fi/Bluetooth hardware behaviour, AppArmor/firewalld enforcement.
- Performance KPIs. No benchmark numbers exist yet and none are claimed.
- ISO reproducibility comparison (`diffoscope`).
- Translation catalogues.

## Rules

- A test that did not run is reported as `SKIPPED` or `Unknown`, never as
  passed.
- `out/build-metadata.json` contains `boot_tested: false` and
  `reproducibility_verified: false` until proven otherwise.
- After any real ISO build, record filename, size, SHA-256 and boot result in
  `docs/architecture/STATUS.md`.
