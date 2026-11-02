# SANORA APT repository (build-time signed archive)

SANORA OS must not rely permanently on live-build's `config/packages.chroot/`,
because the Debian Live Manual states that mechanism **cannot use secure APT**.
`build/scripts/build-repo.sh` therefore builds a small, GPG-signed local APT
repository at build time, and `build/scripts/assemble-config.sh` wires it into
live-build through the supported `config/archives/` mechanism.

## What is generated (all under `build/work/`, ignored by Git)

```
repo/
├── pool/main/s/sanora-base/sanora-base_<version>_all.deb
├── dists/sanora/main/binary-amd64/Packages
├── dists/sanora/main/binary-amd64/Packages.gz
├── dists/sanora/Release
├── dists/sanora/Release.gpg          (detached armoured signature)
├── dists/sanora/InRelease            (clear-signed Release)
└── sanora-archive-key.asc            (armoured public key)
repo-key-id                           key fingerprint
repo-metadata.json                    provenance record
gnupg/                                ephemeral keyring (development only)
```

`apt-ftparchive` generates `Packages` and `Release`; `Release` carries
`Origin`, `Label`, `Suite`, `Codename`, `Architectures`, `Components` and a
`Date` derived from `SOURCE_DATE_EPOCH` (never the wall clock). `gzip -n`
omits timestamp metadata. The script verifies `Release.gpg` with
`gpg --verify` and **fails the build** if verification fails.

## How live-build consumes it

Verified against live-build `1:20250505+deb13u1`
`scripts/build/chroot_archives`:

| Generated file | live-build destination |
|---|---|
| `config/archives/sanora.list.chroot` | `chroot/etc/apt/sources.list.d/sanora.list` |
| `config/archives/sanora.key.chroot` | `chroot/etc/apt/trusted.gpg.d/sanora.key.chroot.asc` (armoured key) |
| `config/package-lists/sanora-repo.list.chroot` | apt package selection: `sanora-base` |

The `.list` uses
`deb [signed-by=/etc/apt/trusted.gpg.d/sanora.key.chroot.asc] file://<repo> sanora main`.
live-build's `Chroot_try_bind_path_from_list` bind-mounts that `file://` path
into the chroot. The result is a normal, signature-verified `apt install
sanora-base`, with dependency resolution (`base-files`, `gettext-base`).

## Key management

- `SANORA_REPO_KEY_ID=<fingerprint>` — use an existing key from the default
  GPG keyring. This is the mode a release build should use.
- `SANORA_REPO_AUTO_KEY=1` — generate an **ephemeral** development key in
  `build/work/gnupg`. Used by CI for development ISOs. The fingerprint is
  recorded in `repo-key-id` and `repo-metadata.json`.
- No key and no auto-key: the script **refuses** to build an unsigned archive.
  It never silently disables `apt-secure`.

**Release policy (not yet implemented):** a public SANORA repository needs an
offline-managed signing key (hardware token / HSM), a documented key
rotation and expiry policy, a published `InRelease`, and an HTTPS mirror.
The private key must never be stored in this repository or in CI logs. The
ephemeral CI key exists only to prove the signing path works end-to-end.

## Package versioning

`SANORA_VERSION` in `config/version.env` is the single source of truth; the
`.deb` file name and `Version:` field are generated from it. Releases must
use a Debian-policy-compliant version and a changelog before publication
(`packages/sanora-base/` currently uses a `dpkg-deb` staging tree, not a
full Debian source package — that migration is a later task).

## Update compatibility

Because the package is installed through APT rather than `dpkg -i` on a local
file, a future signed online repository can deliver updates with ordinary
`apt upgrade`. The build-time `file://` repository is removed from the image
at the end of the chroot stage; the installed system keeps only the SANORA
package metadata, not the build host's key.

## Offline validation

`tests/test_repo.py` checks the repository layout and the generated
`config/archives/` files without requiring GPG. The full signed path is
verified by the CI ISO build (`gpg --verify` inside `build-repo.sh` plus
`lb build` installing `sanora-base` from the signed archive).
