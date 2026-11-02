# KDE / Plasma system defaults

These files become `/etc/xdg/` and `/etc/skel/.config/` entries in the image
through `build/scripts/assemble-config.sh`. This is the "configuration, not
forks" rule from the architecture: no upstream source file is modified.

| Source file | Destination in the image | Purpose |
|---|---|---|
| `kdeglobals` | `/etc/xdg/kdeglobals` | KDE reads defaults from `$XDG_CONFIG_DIRS`; this is where a future SANORA Global Theme is selected |
| `plasma-org.kde.plasma.desktop-appletsrc` | `/etc/skel/.config/` **and** `/etc/xdg/` | Best-effort default wallpaper. `/etc/skel` alone was overwritten by Plasma on first start (verified in QEMU boot test #6), so the KDE system default under `$XDG_CONFIG_DIRS` is shipped as well |

## Status: partially implemented, NOT boot-tested

`LookAndFeelPackage` in `/etc/xdg/kdeglobals` is the documented KDE mechanism
for setting a distribution default global theme (KDE developer blog,
"Setting a default global theme has just become much easier", 2021-12-17).
For `0.1.0-dev` it points at upstream Breeze, because SANORA OS does not yet
ship its own look-and-feel package. Pointing it at a non-existent package would
produce a broken default. Replacing it with `org.sanora.default.desktop` is a
later, explicitly reviewed step.

The wallpaper approach via `/etc/skel/.config/` is a known but imperfect
mechanism: KDE bug 487816 reports that a Look-and-Feel layout script
(`org.kde.plasma.desktop-layout.js`) is the robust way to set a default
wallpaper on first start. The `/etc/skel` file is therefore a **best effort**
and must be verified by booting the ISO. It is not claimed to work.

No Apple assets, macOS layout scripts or copied themes are used. The look of
SANORA OS will be built as an original KDE Global Theme in a later phase.
