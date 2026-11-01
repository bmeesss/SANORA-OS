# Repository architecture

SANORA OS reuses upstream projects and keeps its own work small and legible.
This document explains where each kind of change belongs.

## Top level

| Path | Ownership | Purpose |
|---|---|---|
| `README.md` | SANORA | Project entrypoint, quick start, licensing, blockers |
| `LICENSE`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, `THIRD_PARTY.md` | SANORA | Governance and licensing |
| `SANORA_OS_ARCHITECTURE.md` | phase-1 research (Dutch) | Historical approved research; **do not edit without an ADR** |
| `build.sh` | SANORA | Single build entrypoint |
| `.gitignore` | SANORA | Excludes `out/`, `build/work/`, `*.deb`, Python caches |
| `config/version.env` | SANORA | Single source of truth for version, base, arch, locales, mirrors |

## Implementation areas

| Path | What belongs here | What does NOT |
|---|---|---|
| `build/live-build/` | `lb config` options, chroot hooks | generated `config/*` files, custom ISO builders |
| `build/scripts/` | preflight, package build, config assembly, metadata | undocumented one-off shell magic |
| `config/packages/` | explicit `*.list.chroot` package lists | metapackages that pull hundreds of apps |
| `config/desktop/` | KDE `/etc/xdg` and `/etc/skel` defaults | forks of Plasma, copied themes |
| `config/system/` | `/etc` defaults, apt drop-ins, live-config | editing upstream package files |
| `branding/` | original SVG/PNG assets, ISO text | Apple assets, finished visual design |
| `packages/sanora-base/` | the first SANORA Debian package | a giant package containing everything |
| `installer/calamares/` | Calamares branding component | a fork of Calamares or Debian's settings |
| `tests/` | offline automated tests + manual test checklists | claims of passing tests that never ran |
| `.github/` | workflows, issue forms, PR template | ISO builds on every PR |
| `docs/development/` | developer guides | repeated architecture theory |
| `docs/architecture/STATUS.md` | verified implementation status | marketing |
| `docs/decisions/` | English ADRs | silent changes to approved decisions |

## Generated vs committed

Committed: everything in the table above except generated files. Generated and
ignored: `build/work/` (live-build config tree, chroot, binary), `out/` (ISO,
metadata, checksums), `*.deb`, Python caches. A fresh clone plus
`./build.sh --config-only` recreates the whole build configuration offline.

## Data flow

```
config/version.env ──► build.sh ──► build/live-build/options.sh ──► lb config
config/packages/   ──┐
build/live-build/hooks/ ──┤
branding/iso/      ──┼──► assemble-config.sh ──► build/work/live/config/
config/system,desktop ─┐  │
branding/, installer/ ─┴──► build-package.sh ──► sanora-base_*.deb ──┘
                                                     │
                                           installed by live-build
                                                     ▼
                                                lb build ──► out/*.iso
```

The package is the delivery mechanism for SANORA files; the live-build config
tree only carries package lists, hooks, the `.deb`, the deterministic build
identity and ISO-medium text. There is exactly one copy of each SANORA file.

## Configuration philosophy

- Prefer `/etc` configuration, KDE defaults, systemd drop-ins, packages and
  documented patches over forks.
- The only upstream-supplied file currently patched is
  `/etc/calamares/settings.conf` (one key: `branding`), by hook 0020. Reason:
  Calamares has no drop-in directory for that key, and SANORA reuses Debian's
  module sequence rather than maintaining a fork.
- `/etc/os-release` is replaced through a `dpkg-divert` in `sanora-base`,
  because `base-files` owns the path. This is documented in
  `packages/sanora-base/README.md` and is not yet boot-verified.

## Branch and git conventions

Work happens on `arena/fa064594-sanora-os`. Small commits with prefixes
`build:`, `config:`, `system:`, `branding:`, `installer:`, `tests:`, `ci:`,
`docs:`, `fix:`. See `CONTRIBUTING.md`.
