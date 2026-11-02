# Branding strategy (initial)

## Principle

SANORA OS is an original distribution, not a reskinned copy of another OS.
macOS is only a quality reference from the phase-1 vision; **no Apple asset,
trademark, wallpaper, icon, sound or interface layout is copied**. The current
assets are original vector geometry and contain no Apple/macOS references in
the artwork itself.

## Delivered in `0.1.0-dev`

| Element | Implementation | Status |
|---|---|---|
| OS name / identity | `/etc/os-release` (`NAME="SANORA OS"`, `ID=sanora`, `ID_LIKE=debian`) via `sanora-base` dpkg-divert | `Implemented`, not boot-verified |
| Version metadata | `config/version.env` → `/etc/sanora/release`, `/etc/sanora/build-info`, `sanora-info` | `Implemented` + `Tested` offline |
| Logo | `branding/sanora-logo.svg` + 256×256 PNG | `Implemented` + inspected |
| Wallpaper | `branding/sanora-wallpaper.svg` + 1920×1080 PNG | `Implemented` + inspected |
| Desktop theme config | `/etc/xdg/kdeglobals` with `LookAndFeelPackage=org.kde.breeze.desktop` | `Implemented`, best-effort, untested |
| Default wallpaper wiring | `/etc/skel/.config/` + `/etc/xdg/plasma-org.kde.plasma.desktop-appletsrc` | `Implemented`, **verified NOT effective** — see below |
| Installer branding | `/etc/calamares/branding/sanora/` (branding.desc, show.qml, logo) | `Implemented`, untested |
| Boot medium | `/README.txt` and `/.disk/info` on the ISO; `--iso-volume SANORA-DEV`, `--iso-application`, `--iso-publisher` | `Implemented`, untested |
| Session/login identity | SDDM reads `/etc/os-release` | `Unknown` until boot test |

## Why Breeze is still selected

KDE reads distribution defaults from `$XDG_CONFIG_DIRS` (normally
`/etc/xdg`), and `LookAndFeelPackage` in `/etc/xdg/kdeglobals` is the
documented mechanism for setting a default Global Theme. SANORA OS does not yet
ship a look-and-feel package, so the value points at upstream Breeze. Pointing
at a non-existent `org.sanora.default.desktop` would break first boot. Creating
that package is the next branding task, not a silent config change.

## Why the wallpaper wiring is best-effort

The `/etc/skel/.config/plasma-org.kde.plasma.desktop-appletsrc` approach is
widely used but KDE bug 487816 reports that a Global Theme layout script
(`contents/layouts/org.kde.plasma.desktop-layout.js`) is the robust way to set
a first-start wallpaper. **QEMU boot tests (runs `41462790740` and
`41469346725`) confirmed the config does NOT take effect**: Plasma overwrites
it on first start. A second copy under `/etc/xdg` (KDE's `$XDG_CONFIG_DIRS`
defaults) was added, but the guest check still reports the default is not
applied. The fix is an original SANORA Plasma Global Theme with a layout
script — a new feature deferred to the next phase. The wallpaper asset itself
is present in the image at
`/usr/share/sanora/wallpapers/sanora-default.png`.

## Not yet done (do not claim)

- SANORA KDE Global Theme, icon theme, sound theme, SDDM theme.
- GRUB/isolinux splash, Plymouth, boot animation.
- Light/dark variants, per-resolution wallpapers, accent-colour rules.
- A separate licence decision for documentation and branding assets
  (ADR-0006 / Q-01). Until then assets ship with `sanora-base` under
  `GPL-2.0-or-later`.
- Localised marketing text (product names are not translated).

## Regenerating PNG assets

The SVGs are canonical. On a Debian host with `librsvg2-bin`:

```sh
cd branding
rsvg-convert -w 256  -h 256  sanora-logo.svg      -o sanora-logo.png
rsvg-convert -w 1920 -h 1080 sanora-wallpaper.svg -o sanora-wallpaper.png
```

The committed PNGs were rasterised from the same geometry in the development
sandbox (where `rsvg-convert` was unavailable) using Pillow in a temporary
virtual environment. Builds never need an SVG renderer because the PNGs are
checked in.
