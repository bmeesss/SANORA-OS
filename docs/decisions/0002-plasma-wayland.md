# ADR-0002 — KDE Plasma on Wayland

- **Status:** Accepted 2026-11-01 (architecture ADR-0002; confirmed by user)
- **Decision:** KDE Plasma with KWin as the Wayland compositor, XWayland for
  legacy X11 applications, no X11 session as default, no custom compositor.
- **Rationale:** Plasma's Global Themes, KWin scripts/effects and KDE
  configuration defaults are official extension points, giving SANORA an own
  identity without forking a desktop. KDE is moving to Wayland-only sessions;
  Xfce's Wayland support is still experimental; GNOME offers fewer sanctioned
  extension points.
- **Consequences:** Qt6/KF6 version coupling, ~4-month upstream Plasma cadence,
  XWayland gaps for some legacy apps, Debian trixie ships Plasma 6.3.6.
- **Implementation:** `config/packages/10-plasma.list.chroot`
  (`plasma-desktop`, `plasma-workspace`, `kwin-wayland`, `xwayland`, `sddm`,
  `breeze`), `config/desktop/kdeglobals`, `--initramfs live-boot`,
  `--initsystem systemd`.
- **Caveat:** Debian trixie's `sddm` is still described as an X11 display
  manager and depends on `xserver-xorg`. Whether the Wayland session is selected
  correctly must be confirmed by a boot test; it is not claimed to work yet.
