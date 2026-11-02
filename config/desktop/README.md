# KDE / Plasma system defaults

These files become `/etc/xdg/` and `/etc/skel/.config/` entries in the image
through `build/scripts/build-package.sh` (they ship inside `sanora-base`).
This follows the "configuration, not forks" rule: no upstream source file is
modified.

| Source file | Destination in the image | Purpose |
|---|---|---|
| `kdeglobals` | `/etc/xdg/kdeglobals` | Selects the original SANORA Global Theme, color scheme and icon theme for clean accounts via `$XDG_CONFIG_DIRS` |
| `plasma-org.kde.plasma.desktop-appletsrc` | `/etc/skel/.config/` **and** `/etc/xdg/` | Best-effort wallpaper fallback. Both copies were verified NOT effective on Plasma's first start; the authoritative mechanism is the Global Theme layout script |

## SANORA Global Theme

`LookAndFeelPackage=org.sanora.light.desktop` in `/etc/xdg/kdeglobals` selects
the original KPackage shipped by `sanora-base` at
`/usr/share/plasma/look-and-feel/org.sanora.light.desktop/`. A dark variant
(`org.sanora.dark.desktop`) is also shipped. The Global Theme contains
`contents/defaults` (color scheme, icon theme, Plasma style, KWin decoration,
cursor, splash) and `contents/layouts/org.kde.plasma.desktop-layout.js`, which
styles the panel and sets the SANORA wallpaper on first start. See
[`branding/plasma/README.md`](../../branding/plasma/README.md) for the full
structure and the verified KDE API references.

KDE reads defaults from `$XDG_CONFIG_DIRS`, so a new user account with no
`~/.config` gets the SANORA theme. `tests/boot/qemu_boot.py` verifies this with
`kreadconfig6` against an empty temporary home directory.

## Why the plain config files are only a fallback

QEMU boot tests proved that Plasma overwrites
`plasma-org.kde.plasma.desktop-appletsrc` on first start. KDE bug 487816
documents that a Global Theme layout script is the robust way to set a
first-start wallpaper. The `/etc/skel` and `/etc/xdg` copies remain as a
harmless fallback; the layout script is authoritative.

No Apple assets, macOS layout scripts or copied themes are used.
