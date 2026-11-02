# SANORA OS branding (initial, deliberately minimal)

This is a **foundation**, not a finished visual design. The goal of
`0.1.0-dev` is that the OS name, release metadata, installer, boot medium and
desktop all consistently say "SANORA OS" using original assets.

## Assets

| File | Purpose | Format |
|---|---|---|
| `sanora-logo.svg` / `.png` | Canonical mark: a stylised "S" ribbon with one accent node | SVG source + 256×256 PNG |
| `sanora-wallpaper.svg` / `.png` | Abstract dark-teal wallpaper | SVG source + 1920×1080 PNG; shipped in the image as `sanora-default.svg` / `.png` (the canonical name referenced by the KDE Global Theme and `/etc/xdg` defaults) |
| `iso/README.txt` | Text shown at the root of the bootable ISO medium | plain text |
| `iso/disk-info` | ISO `.disk/info` identification string | one line |

## Ownership and licensing

All artwork here is **original** vector geometry created for SANORA OS. No
Apple assets, macOS screenshots, dock rendering, icons, wallpapers, sounds,
trademarks or interface copies are used. There is no round bitten fruit, no
macOS-style menu bar and no copied Aqua/Big Sur gradients.

The SVG files are the canonical source. The PNG files are derived, checked-in
assets so that a build never needs an SVG renderer. On a Debian host they can
be regenerated with `librsvg2-bin`:

```sh
rsvg-convert -w 256   -h 256   sanora-logo.svg      -o sanora-logo.png
rsvg-convert -w 1920  -h 1080  sanora-wallpaper.svg -o sanora-wallpaper.png
```

In this development sandbox `rsvg-convert` was unavailable, so the committed
PNGs were rasterised from the same geometry with Pillow in a temporary virtual
environment. The SVG files remain authoritative. A formal licence for
branding assets is still an open decision (ADR-0006 / Q-01); until then they
are distributed with `sanora-base` under `GPL-2.0-or-later` — see
`THIRD_PARTY.md`.

## Where the assets are used

`build/scripts/build-package.sh` puts the SVGs and PNGs into the
`sanora-base` package at `/usr/share/sanora/branding/` and
`/usr/share/sanora/wallpapers/`, and the logo PNG into the Calamares branding
directory. `config/desktop/plasma-org.kde.plasma.desktop-appletsrc` points the
default wallpaper at the PNG. `branding/iso/` files are copied to the ISO root
by `build/scripts/assemble-config.sh`.

## Not yet implemented (do not claim otherwise)

- A SANORA KDE Plasma Global Theme / look-and-feel package.
  `/etc/xdg/kdeglobals` still selects upstream Breeze because pointing at a
  non-existent theme would break first boot.
- Custom icon theme, sound theme, SDDM theme, GRUB/isolinux splash, Plymouth.
- Light/dark variants, wallpaper sets per resolution, dark/light accent rules.
- Localised marketing text. UI strings use gettext conventions; product names
  are not translated.
