# Calamares installer configuration

SANORA OS uses **upstream Calamares unmodified** (`calamares` +
`calamares-settings-debian` from Debian trixie). There is no fork, no custom
module and no reimplemented installer.

## What SANORA OS supplies

`branding/sanora/` is a Calamares branding component installed by
`sanora-base` at `/etc/calamares/branding/sanora/`:

| File | Purpose |
|---|---|
| `branding.desc` | Product name, window size, colours, URLs, logo, slideshow |
| `show.qml` | Minimal installation slideshow; sentences use `qsTr()` |
| `sanora-logo.png` | Copied from `branding/sanora-logo.png` at package build time |

`branding.desc` uses `${NAME}`, `${VERSION_ID}`, `${HOME_URL}` and
`${BUG_REPORT_URL}` from `/etc/os-release`, so there is one source of truth for
version and identity (Calamares supports this substitution).

## The one documented patch

Debian's `calamares-settings-debian` ships `/etc/calamares/settings.conf` with
`branding: debian` **and** the Debian-specific module sequence and module
configuration (`unpackfs`, `bootloader`, `fstab`, ...). Calamares has a single
top-level settings file with no drop-in directory for that key. Rather than
forking the Debian config, hook
`build/live-build/hooks/normal/0020-sanora-calamares-branding.hook.chroot`
changes only `branding: debian` to `branding: sanora`. This is an explicit,
documented patch to an upstream-supplied configuration file — not a source
modification.

## What is NOT implemented yet

- **LUKS2 / encryption in the installer.** `cryptsetup` is installed in the
  package set, but Calamares partition/encryption module configuration has not
  been reviewed or written. LUKS2 support is therefore `Planned`, not
  `Implemented`. See `docs/development/SECURITY_BASELINE.md`.
- Btrfs + Snapper rollback configuration, OEM setup, online log uploading,
  custom partitioning presets.
- Any validation by actually booting the ISO and running the installer.
  Calamares 3.3.14 in trixie may differ from the newer upstream
  `branding.desc` format used as a reference; the first boot test must confirm
  the branding loads without errors.

## Upstream references

- Calamares branding keys and `settings.conf` structure: the archived upstream
  GitHub repository `calamares/calamares` (`src/branding/default/branding.desc`,
  `settings.conf`), retrieved 2026-11-01.
- Debian trixie package `calamares` 3.3.14-1 and
  `calamares-settings-debian` 13.0.13-1:
  <https://packages.debian.org/trixie/calamares>.
- The architecture document notes the GitHub Calamares repo is archived since
  2025-08-18 and that Codeberg is the canonical upstream; phase 4 must
  re-validate installer documentation against the current Codeberg docs.
