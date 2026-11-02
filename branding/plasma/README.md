# SANORA KDE Plasma identity (original artwork)

This directory contains SANORA OS's own KDE Plasma identity, built entirely
with KDE's supported extension mechanisms. **No Plasma source is modified and
no Apple/macOS asset or interface is copied.** macOS is only a quality
reference.

## Mechanisms used (all upstream KDE)

| Mechanism | Installed path | Purpose |
|---|---|---|
| Plasma/LookAndFeel KPackage (light) | `/usr/share/plasma/look-and-feel/org.sanora.light.desktop/` | Default Global Theme |
| Plasma/LookAndFeel KPackage (dark) | `/usr/share/plasma/look-and-feel/org.sanora.dark.desktop/` | Selectable dark Global Theme |
| `contents/defaults` | inside each KPackage | Color scheme, icon theme, widget style, Plasma style, splash, KWin decoration, cursor |
| `contents/layouts/org.kde.plasma.desktop-layout.js` | inside each KPackage | Panel/dock layout and wallpaper on first start |
| KDE color schemes | `/usr/share/color-schemes/SANORALight.colors`, `SANORADark.colors` | Consistent system colors |
| Plasma desktop theme | `/usr/share/plasma/desktoptheme/sanora/` | Panel/widget styling, falls back to Breeze |
| Icon themes | `/usr/share/icons/sanora/`, `/usr/share/icons/sanora-dark/` | Original `start-here` launcher icon; inherits Breeze / Breeze Dark |
| Wallpapers and logo | `/usr/share/sanora/wallpapers/`, `/usr/share/sanora/branding/` | Original SVG + PNG assets from `branding/` |

The Global Themes are selected through `LookAndFeelPackage` in
`/etc/xdg/kdeglobals` (KDE reads system defaults from `$XDG_CONFIG_DIRS`).
That means a **clean new user account** with no `~/.config` gets the SANORA
theme on first login, not just the live session.

## Layout script

`org.kde.plasma.desktop-layout.js` uses the documented Plasma scripting API
(`loadTemplate`, `panels()`, `desktopsForActivity`, `writeConfig`) verified
against Plasma 6 `shell/scripting` in the KDE plasma-workspace source tree:

- loads the upstream default panel template (which already contains the
  Kickoff application launcher, Task Manager, system tray and clock),
- restyles it into a compact, floating, centre-aligned bottom panel,
- sets the SANORA wallpaper on every desktop in the current activity.

It deliberately does **not** remove or replace upstream widgets; it only
configures them. This avoids fragile widget-ID assumptions.

## Light / dark

Both Global Themes share the same layout script and icon artwork. They differ
in `metadata.json` (Id, Name, Description) and `contents/defaults`
(`ColorScheme`, icon theme). `SANORALight.colors` and `SANORADark.colors` are
ordinary KDE color-scheme files; users can switch with System Settings →
Appearance → Global Theme.

## Verification

`config/desktop/README.md` and `docs/development/BRANDING.md` describe how the
theme is tested on a clean account in the QEMU boot harness. Theme files are
checked by `tests/test_theme.py` offline (valid JSON, valid INI, required
keys, no Apple references) and by the guest checks in CI.

## Not yet done

- Original KWin decoration, Plasma style SVGs, splash QML animation and sound
  theme (upstream Breeze is inherited; no fork).
- Full icon set; only the launcher/start-here icons are original so far, all
  other icons inherit from Breeze upstream.
- Localised theme names; product names are intentionally not translated.
