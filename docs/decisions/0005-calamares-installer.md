# ADR-0005 — Calamares with Debian settings

- **Status:** Partially implemented. Architecture ADR-0005 was `Voorgesteld`;
  the kickoff fixed Calamares as the installer.
- **Decision:** install upstream `calamares` and
  `calamares-settings-debian` unmodified. Reuse Debian's module sequence and
  module configuration. SANORA supplies only a branding component.
- **Rationale:** Debian's Calamares settings contain the distribution-specific
  `unpackfs`, `bootloader`, `fstab` and `users` configuration. Forking it would
  create a maintenance burden for one person + AI support.
- **Documented patch:** Calamares has a single top-level `settings.conf` with no
  drop-in directory for the `branding` key. Hook
  `0020-sanora-calamares-branding.hook.chroot` changes only
  `branding: debian` → `branding: sanora`. This is a patch to an
  upstream-supplied configuration file, not to upstream source.
- **Not implemented:** LUKS2/encryption module configuration, Btrfs/Snapper
  rollback, OEM setup. `cryptsetup` is installed but encryption in the
  installer is `Planned`. No installer has been launched.
- **Caveat:** trixie ships Calamares 3.3.14; the branding format was checked
  against the archived upstream GitHub source, and Codeberg is now canonical.
  Phase 4 must re-validate against current docs.
