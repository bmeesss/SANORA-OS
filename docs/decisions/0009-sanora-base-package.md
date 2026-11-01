# ADR-0009 — `sanora-base` Debian package

- **Status:** Accepted for the `0.1.0-dev` milestone (implementation kickoff).
- **Decision:** deliver SANORA identity and system defaults through a real
  Debian package named `sanora-base`, built with `dpkg-deb --build` from
  `packages/sanora-base/`. No debhelper/source package yet; migration to
  `dpkg-buildpackage` is a later explicit task.
- **Rationale:** "SANORA OS is not Debian with a wallpaper". A package makes
  identity installable, upgradable and removable, gives one owner per file and
  avoids a second copy in the live-build overlay. Keep it small and modular.
- **Contents:** `/etc/os-release` (via `dpkg-divert`), `/etc/sanora/release`,
  `/etc/sanora/sanora.conf`, apt security drop-in, live-config user groups,
  `/etc/xdg/kdeglobals`, `/etc/skel` wallpaper config, Calamares branding,
  original logo/wallpaper assets, `sanora-info`, copyright file.
- **Modularity:** planned later split into `sanora-defaults`,
  `sanora-branding`, `sanora-tools`, `sanora-release`. No giant package, no
  fork of `base-files` or Plasma.
- **Reproducibility:** all staged file mtimes are clamped to
  `SOURCE_DATE_EPOCH`; `tests/test_package.py` verifies two builds are
  byte-identical.
- **Delivery:** live-build `config/packages.chroot/` (no secure APT for local
  packages — see ADR-0003 and `SECURITY_BASELINE.md`).
- **Not verified:** actual installation inside a trixie chroot. The
  `dpkg-divert` of `/etc/os-release` is a real system-level change and is
  marked `Partially tested`, not claimed to work.
