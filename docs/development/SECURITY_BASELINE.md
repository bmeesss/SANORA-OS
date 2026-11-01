# Security baseline (`0.1.0-dev`)

> This is configuration intent, **not a verified security posture**. Everything
> below is `Implemented` as package selection/config files but `Not tested` at
> runtime, because no ISO has been booted. See
> `docs/architecture/STATUS.md`.

## What is configured

| Control | Implementation | Status |
|---|---|---|
| Verified package sources | `--apt-secure true`, `debian-archive-keyring`, HTTPS Debian mirrors, `trixie-security` + `trixie-updates` | `Implemented`, not boot-tested |
| Mandatory access control | `apparmor`, `apparmor-utils` | `Implemented`, enforcement unverified |
| Firewall | `firewalld`, `plasma-firewall` (KDE KCM) | `Implemented`, default zone unverified |
| Authorisation | `polkitd`, `pkexec`, `polkit-kde-agent-1` | `Implemented`, behaviour unverified |
| Privilege elevation | `sudo` (live-config) | `Implemented` |
| Automatic security updates | `unattended-upgrades` + `/etc/apt/apt.conf.d/99-sanora-security` (`APT::Periodic::Unattended-Upgrade "1"`) | `Implemented`, not observed running |
| LUKS2 capability | `cryptsetup` installed | `Implemented` (tooling only) |
| LUKS2 in installer | Calamares encryption module | **`Planned` — not configured** |
| Sandboxing | `flatpak` + Discover Flatpak backend + `kde-config-flatpak` | `Implemented`, not tested |
| Secure Boot | live-build `--uefi-secure-boot auto`, reusing Debian's signed shim/GRUB | `Implemented`, boot path unverified |
| Signed SANORA repository | none | `Planned` |
| Release signing / SBOM / SLSA | none | `Planned` |
| Own Microsoft-signed shim | none (deliberate, phase-1 risk R-01) | `Planned / not in v1` |

## Custom packages and secure APT

`sanora-base` is currently installed through live-build's
`config/packages.chroot/`. The Debian Live Manual states this mechanism
**cannot use secure APT**. Debian packages still come from verified signed
mirrors; the SANORA package itself is a local unsigned `.deb` whose SHA-256 is
recorded in `out/build-metadata.json`. Replacing `packages.chroot` with a
**signed local SANORA APT repository** is required before any release. This is
a known gap, not a hidden one.

## NVIDIA / MOK / Secure Boot

NVIDIA components are **not** bundled (ADR-0007 `BLOCKED`). Out-of-tree kernel
modules require MOK enrolment under Secure Boot; SANORA OS has no own MOK
policy, no signing key and no documentation for that flow yet. See
`docs/decisions/0007-nvidia-in-default-iso.md`. Do not bundle proprietary
components until the legal and Secure Boot review is complete.

## Verification checklist (not executed)

1. `aa-status` — AppArmor profiles loaded/enforced.
2. `firewall-cmd --get-default-zone` and `--state`.
3. `pkaction` / polkit agent prompt in a desktop session.
4. `systemctl status unattended-upgrades`, `apt-config dump | grep Periodic`.
5. `flatpak remotes`, sandbox permission test with a sample app.
6. Boot with Secure Boot enabled and disabled; record MOK behaviour.
7. Calamares LUKS2 install on a disposable VM (after the module is configured).
8. `sha256sum -c out/SHA256SUMS` for the ISO.

## Reporting

Security issues follow `SECURITY.md`. There is no supported release yet, no SLA
and no bug bounty programme. This honesty is part of the project's quality bar.
