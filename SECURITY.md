# Security Policy

## Supported versions

SANORA OS has **no released version yet**. `0.1.0-dev` is a development
milestone and receives no security support. Security support policy, release
cadence and an end-of-life schedule are still open decisions in the phase-1
architecture document (Q-11).

| Version | Status | Security support |
|---|---|---|
| `0.1.0-dev` | development ISO | none — do not deploy |

## Reporting a vulnerability

Please **do not** open a public issue for a suspected vulnerability. Use the
GitHub private vulnerability reporting / security advisory feature on
<https://github.com/bmeesss/SANORA-OS>. If that is unavailable, open a minimal
public issue asking for a private contact channel without disclosing details.

Include: affected component and version, reproduction steps, impact, and any
suggested mitigation. You will receive an acknowledgement when a maintainer has
triaged it. There is no bug bounty programme, no SLA and no dedicated security
team yet; this is an honest limitation of a one-person + AI project.

## Security baseline (current implementation)

The following is **implemented as configuration/package selection only** and is
**not yet boot-tested**. See
[docs/development/SECURITY_BASELINE.md](docs/development/SECURITY_BASELINE.md).

- Debian `main`, `contrib` and `non-free-firmware` from HTTPS mirrors with
  `--apt-secure true` and `debian-archive-keyring` (verified package sources).
- `apparmor`, `apparmor-utils`, `polkitd`, `polkit-kde-agent-1`, `pkexec`,
  `firewalld`, `plasma-firewall`, `sudo` and `cryptsetup` in the package set.
- `unattended-upgrades` enabled for Debian security updates via an apt
  periodic-update drop-in.
- `flatpak` and the Discover Flatpak backend for sandboxed applications.
- Debian's signed shim / GRUB chain via `live-build --uefi-secure-boot auto`.
  SANORA OS does **not** have its own Microsoft-signed shim.

## Known gaps (do not treat as implemented)

- LUKS2 encryption is available as a `cryptsetup` capability, but Calamares
  encryption/LUKS2 module configuration is **not** configured yet.
- There is no signed SANORA APT repository, no release signing key, no HSM,
  no SBOM/SLSA attestation and no reproducible-build attestation yet.
- AppArmor enforcement, firewalld default zone, polkit behaviour, Flatpak
  sandboxing and Secure Boot boot paths have not been verified on hardware.
- NVIDIA proprietary components are **not** bundled. Their licensing, MOK and
  Secure Boot implications are an open, gated decision; see
  [docs/decisions/0007-nvidia-in-default-iso.md](docs/decisions/0007-nvidia-in-default-iso.md).

## Statement

This document describes engineering intent, not a verified security posture.
No security claim is made until it has been tested and the result recorded in
`docs/architecture/STATUS.md`.
