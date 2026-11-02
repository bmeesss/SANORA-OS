# Architecture decision records (English)

These ADRs are the English implementation-facing record of decisions. The
authoritative phase-1 research and its Dutch ADR table live unchanged in
`SANORA_OS_ARCHITECTURE.md` (§0.5 and Bijlage A). Where this index and that
document differ in *status*, the more recent explicit user decision wins, and
the difference is noted in the ADR.

Approved decisions are **not** changed silently. A material change requires a
new ADR with rationale and an explicit decision.

| ADR | Title | Status |
|---|---|---|
| [0001](0001-debian-trixie-base.md) | Debian 13 trixie stable (amd64) as the base | Accepted 2026-11-01 |
| [0002](0002-plasma-wayland.md) | KDE Plasma on Wayland | Accepted 2026-11-01 |
| [0003](0003-package-management.md) | apt/dpkg + own signed repo + Flatpak | Partially accepted; signed repo still open |
| [0004](0004-live-build-iso.md) | Debian live-build for ISO creation | Accepted (kickoff 2026-11-01) |
| [0005](0005-calamares-installer.md) | Calamares with Debian settings | Partially implemented |
| [0006](0006-license.md) | GPL-2.0-or-later for SANORA code | Accepted for code; docs/assets open |
| [0007](0007-nvidia-in-default-iso.md) | NVIDIA in the default ISO | **BLOCKED — awaiting confirmation** |
| [0008](0008-english-default-i18n.md) | English default, international by design | Accepted (kickoff 2026-11-01) |
| [0009](0009-sanora-base-package.md) | `sanora-base` Debian package | Accepted for `0.1.0-dev` |
| [0010](0010-luks2-installer-config.md) | LUKS2 via Calamares `partition.conf` | Config implemented; install/boot not validated |

## Open questions carried over from phase 1

Q-03 minimum hardware, Q-05 Plasma version, Q-07 image-based updates, Q-08
PackageKit, Q-09 default apps/Flathub remote, Q-10 ARM64, Q-11 release policy,
Q-12 statistics, Q-13 ChatGPT collaboration. None of these were decided during
the implementation kickoff and none were silently decided here.

## Decision needed from the project owner

**ADR-0007.** The architecture document still asks for confirmation of the
NVIDIA-in-ISO deviation, including licence delivery, driver/firmware/userspace
version pinning, MOK / Secure Boot behaviour and image-size impact. Per the
kickoff stop conditions, NVIDIA implementation is stopped and flagged; no
NVIDIA component is bundled. See `0007-nvidia-in-default-iso.md`.
