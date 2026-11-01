# System defaults

These are plain `/etc` configuration files. They are copied by
`build/scripts/assemble-config.sh` into live-build's
`config/includes.chroot/`, so they land in the image **after** package
installation. No upstream package file or source tree is modified.

| Source file | Destination | Purpose |
|---|---|---|
| `sanora.conf` | `/etc/sanora/sanora.conf` | Non-sensitive SANORA system defaults read by `sanora-info` |
| `99-sanora-security` | `/etc/apt/apt.conf.d/99-sanora-security` | Periodic apt refresh and unattended Debian security upgrades |
| `10-sanora-user.conf` | `/etc/live/config.conf.d/10-sanora-user.conf` | live-config user groups (from the Debian Live Manual example) |

## Security baseline notes

- `99-sanora-security` enables `APT::Periodic::Unattended-Upgrade`. The set of
  allowed origins is the Debian default in
  `/etc/apt/apt.conf.d/50unattended-upgrades` shipped by the
  `unattended-upgrades` package; SANORA OS does not override it.
- AppArmor enforcement, the firewalld default zone, polkit behaviour and
  Flatpak sandboxing are **not verified** until an ISO is booted.
- LUKS2: `cryptsetup` is installed, but the Calamares encryption module is not
  configured. Do not describe LUKS2 as working yet.
- Secure Boot: the ISO reuses Debian's signed shim via live-build
  `--uefi-secure-boot auto`. SANORA OS has no own signing key or MOK policy.

## Internationalisation

English (`en_US.UTF-8`, keyboard `us`) is the default and is set both as a
live-boot parameter in `build/live-build/options.sh` and for the installed
system by hook `0010-sanora-locale.hook.chroot`. No Dutch or country-specific
defaults are present. Additional locales are added by extending the hook and
the font/input-method package lists, not by changing application code.
