# sanora-base

The first SANORA OS Debian package. It is a **binary package staging tree**
built with `dpkg-deb --build` by `build/scripts/build-package.sh` — no
debhelper, no source package and no upstream fork yet. Migrating to a full
`debian/` source package with `dpkg-buildpackage` is a later, explicit task.

## Why a package at all

SANORA OS should be more than "Debian with a wallpaper", but the identity must
be delivered through the distribution's own package manager, not by copying
files into an ISO. A package makes the identity installable, upgradable and
removable, and gives us one place to record ownership and licensing.

## What it ships (all generated from single-source inputs)

| Path in the image | Source of truth |
|---|---|
| `/etc/os-release` (via `dpkg-divert`) | `config/version.env` |
| `/etc/sanora/release` | `config/version.env` |
| `/etc/sanora/sanora.conf` | `config/system/sanora.conf` |
| `/etc/sanora/build-info` | `build/scripts/assemble-config.sh` (live-build includes) |
| `/etc/apt/apt.conf.d/99-sanora-security` | `config/system/99-sanora-security` |
| `/etc/live/config.conf.d/10-sanora-user.conf` | `config/system/10-sanora-user.conf` |
| `/etc/xdg/kdeglobals` | `config/desktop/kdeglobals` |
| `/etc/skel/.config/plasma-org.kde.plasma.desktop-appletsrc` | `config/desktop/` |
| `/etc/calamares/branding/sanora/*` | `installer/calamares/`, `branding/sanora-logo.png` |
| `/usr/share/sanora/branding/*`, `/usr/share/sanora/wallpapers/*` | `branding/` |
| `/usr/bin/sanora-info` | `packages/sanora-base/usr/bin/sanora-info` |
| `/usr/share/doc/sanora-base/copyright` | `DEBIAN/copyright` |

`/etc/sanora/build-info` is deliberately **not** in the package: it contains
build-specific data (git commit, `SOURCE_DATE_EPOCH`) and is written into the
image by the build configuration, so a package rebuild does not change it.

## Modularity

This is one small package for the `0.1.0-dev` milestone. The intended split for
later phases is `sanora-defaults` (`/etc`), `sanora-branding` (assets and KDE
theme), `sanora-tools` (helpers) and `sanora-release` (metadata). No giant
package and no fork of `base-files`, Plasma or Calamares.

## `/etc/os-release` and dpkg-divert

`base-files` owns `/etc/os-release`. `DEBIAN/preinst` adds a `dpkg-divert` to
`/etc/os-release.debian` and `DEBIAN/postrm` removes it. This is the standard
Debian way to replace a file owned by another package.

**Regression fixed after ISO build #3.** `debootstrap` (used by live-build)
leaves a *local* diversion of `/etc/os-release` to
`/etc/os-release.debootstrap`, which clashed with our diversion and aborted
`lb build`. live-build's own `scripts/build/chroot_hacks` removes that local
diversion, but only **after** packages are installed. `preinst` now removes it
first with the same command live-build uses
(`dpkg-divert --local --remove --no-rename /etc/os-release`) and then registers
the SANORA diversion. This is a real fix, verified by the subsequent ISO build.

## Internationalisation

`sanora-info` uses `gettext` with `TEXTDOMAIN=sanora-base`. There are no `.po`
files yet; adding a language means shipping a compiled catalogue at
`/usr/share/locale/<lang>/LC_MESSAGES/sanora-base.mo`, with no code changes.
See `docs/development/INTERNATIONALIZATION.md`. It also accepts an optional
`SANORA_ROOT` prefix used only by the offline tests to read a fake `/etc`
without root privileges.
