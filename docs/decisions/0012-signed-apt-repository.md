# ADR-0012 — Signed SANORA APT repository for build-time package delivery

- **Status:** Accepted 2026-11-02. Implements ADR-0003's open
  "signed SANORA APT repository" item; no approved architecture decision is
  changed.
- **Problem:** `config/packages.chroot/` (local `.deb` files copied into the
  ISO build) is explicitly documented by the Debian Live Manual as unable to
  use secure APT. It also does not resolve dependencies through APT and gives
  no update path for SANORA packages.
- **Decision:** generate a small GPG-signed APT repository at build time with
  `apt-ftparchive` + `gpg`, and install SANORA packages from it via
  live-build's supported `config/archives/` mechanism (`*.list.chroot`,
  `*.key.chroot`, `*.list` package lists with `signed-by`).
- **Alternatives considered:**
  1. Keep `packages.chroot` — rejected: no secure APT, no dependency
     resolution, no updates.
  2. Vendor a forked `debian-archive-keyring` — rejected: modifies an upstream
     package and adds SANORA keys to a global trust anchor.
  3. Publish a public HTTPS repository immediately — rejected: requires key
     management, mirror infrastructure and a release policy before any public
     release exists.
  4. Disable `apt-secure` — rejected: weakens the security baseline.
- **Key management:** development/CI builds use an ephemeral key
  (`SANORA_REPO_AUTO_KEY=1`) stored only in `build/work/gnupg` (Git-ignored).
  A public release requires an offline-managed key, rotation/expiry policy and
  HTTPS distribution. The private key is never committed or logged.
- **Consequences:** `gnupg` and `apt-utils` become build-time host
  dependencies. `Release`/`InRelease` are deterministic (date from
  `SOURCE_DATE_EPOCH`, `gzip -n`). The repository is bind-mounted into the
  chroot only during the build and is removed from the final image.
- **Verification:** `build-repo.sh` runs `gpg --verify` on `Release.gpg` and
  fails the build on error; `lb build` must install `sanora-base` from the
  signed archive. Offline layout checks live in `tests/test_repo.py`.
- **References:** Debian Live Manual §8.3.2; live-build `1:20250505+deb13u1`
  `scripts/build/chroot_archives`; `repo/README.md`.
