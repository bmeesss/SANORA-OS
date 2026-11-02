# SANORA desktop identity (Phase 3)

## Principle

SANORA OS is an original distribution, not a reskinned copy of another OS.
macOS is only a quality reference; **no Apple asset, trademark, wallpaper,
icon, sound or interface layout is copied**. All SANORA artwork is original
vector geometry and is checked by `tests/test_theme.py`.

The identity is built with KDE's supported extension mechanisms only:
`Plasma/LookAndFeel` KPackages, KDE color schemes, Plasma desktop themes,
icon themes inheriting upstream Breeze, and Plasma layout scripts. Plasma
itself is never modified or forked. Full source layout is documented in
[`branding/plasma/README.md`](../../branding/plasma/README.md).

## Delivered

| Element | Implementation | Status |
|---|---|---|
| OS name / identity | `/etc/os-release` via `sanora-base` dpkg-divert | `Implemented` + verified in QEMU guest |
| Version metadata | `config/version.env` → `/etc/sanora/release`, `/etc/sanora/build-info`, `sanora-info` | `Implemented` + `Tested` |
| Logo | `branding/sanora-logo.svg` + 256×256 PNG | `Implemented` + inspected |
| Wallpaper | `branding/sanora-wallpaper.svg` + 1920×1080 PNG | `Implemented` + inspected |
| Global Theme (light) | `/usr/share/plasma/look-and-feel/org.sanora.light.desktop/` | `Implemented`, clean-account check in CI |
| Global Theme (dark) | `/usr/share/plasma/look-and-feel/org.sanora.dark.desktop/` | `Implemented`, clean-account check in CI |
| Light / dark colors | `/usr/share/color-schemes/SANORALight.colors`, `SANORADark.colors` | `Implemented` + `Tested` offline |
| Icon themes | `/usr/share/icons/sanora/`, `sanora-dark/` with original launcher icon; inherit Breeze | `Implemented` + `Tested` offline |
| Plasma desktop theme | `/usr/share/plasma/desktoptheme/sanora/` with `FallbackTheme=default` | `Implemented` + `Tested` offline |
| Panel / dock / launcher | `org.kde.plasma.desktop-layout.js`: compact floating bottom-centre panel, upstream Kickoff + Task Manager retained | `Implemented`, boot verification in CI |
| Wallpaper on first start | layout script `writeConfig("Image", ...)` — the KDE-recommended mechanism | `Implemented`, boot verification in CI |
| System defaults | `/etc/xdg/kdeglobals` selects `org.sanora.light.desktop`, `SANORALight`, `sanora` icons | `Implemented` + `Tested` offline |
| Installer branding | `/etc/calamares/branding/sanora/` | `Implemented`, Calamares start verified in QEMU |
| Boot medium | `/README.txt`, `/.disk/info`, ISO metadata | `Implemented` |

## Why a layout script for the wallpaper

QEMU boot tests (`41462790740`, `41469346725`) proved that writing
`~/.config/plasma-org.kde.plasma.desktop-appletsrc` (via `/etc/skel` or
`/etc/xdg`) does **not** survive Plasma's first start. KDE bug 487816 confirms
that a Global Theme's `contents/layouts/org.kde.plasma.desktop-layout.js` is
the robust, supported mechanism. The SANORA layout script uses the verified
Plasma 6 scripting API (`loadTemplate`, `panels()`, `desktopsForActivity`,
`writeConfig`) to set the wallpaper and restyle the panel. The plain config
files remain as a best-effort fallback only.

## Clean-account verification

`tests/boot/qemu_boot.py` runs `kreadconfig6` with `HOME` and
`XDG_CONFIG_HOME` pointed at an **empty temporary directory** so no
`~/.config` exists. It asserts the effective defaults resolve to
`org.sanora.light.desktop`, `SANORALight` and icon theme `sanora`, and that all
theme assets and the layout script are present in the image. Result is written
to `out/boot-uefi/theme-checks.txt` / `boot-validation.json`.

## Not yet done (do not claim)

- Original KWin decoration, Plasma style SVGs, splash QML animation and sound
  theme; upstream Breeze is inherited intentionally, not forked.
- Full original icon set; only the launcher/start-here icons are original so
  far. All other icons inherit from Breeze / Breeze Dark upstream.
- Localised theme names (product names are deliberately not translated).
- Visual review of the desktop screenshot by a human designer.
