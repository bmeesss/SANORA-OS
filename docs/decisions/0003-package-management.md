# ADR-0003 — Package management

- **Status:** Partially accepted. Architecture ADR-0003 was `Voorgesteld`;
  the kickoff fixed apt/dpkg, Flatpak and AppStream but did not ratify the
  signed-repository design. Q-08 (PackageKit) remains open.
- **Decision (implemented for `0.1.0-dev`):** `apt`/`dpkg` from signed Debian
  mirrors; Flatpak for applications; AppStream metadata; KDE Discover; fwupd;
  no snap as a default channel. `packagekit` is installed provisionally so
  Discover can manage Debian packages.
- **Decision (still open):** a **signed SANORA APT repository**. Today the
  `sanora-base` package is delivered through live-build's
  `config/packages.chroot/`, which the Debian Live Manual states cannot use
  secure APT. This is a known gap recorded in `THIRD_PARTY.md` and
  `docs/development/SECURITY_BASELINE.md`.
- **Consequences:** no SANORA updates until the signed repository exists; no
  third-party remote (Flathub) is preconfigured by default (Q-09).
- **Implementation:** `config/packages/30-software.list.chroot`,
  `build/live-build/options.sh` (`--apt-secure true`, HTTPS mirrors),
  `build/scripts/assemble-config.sh` (`packages.chroot`).
