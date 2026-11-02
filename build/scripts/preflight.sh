#!/usr/bin/env bash
# Verify that the host can actually run a Debian live-build ISO build.
# Exits non-zero with an actionable message; never silently skips a check.

set -Eeuo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
# shellcheck disable=SC1091
source "$REPO_ROOT/config/version.env"

SKIP_NETWORK="${SANORA_SKIP_NETWORK_CHECK:-0}"
FAIL=0

note() { printf '[preflight] %s\n' "$*"; }
warn() { printf '[preflight] MISSING: %s\n' "$*" >&2; FAIL=1; }

note "SANORA OS ${SANORA_VERSION} / Debian ${DEBIAN_SUITE} / ${SANORA_ARCH}"
note "repository: ${REPO_ROOT}"
note "host: $(. /etc/os-release && printf '%s %s' "$ID" "$VERSION_ID")"
note "user: uid=$(id -u)"

if [ "$(id -u)" -ne 0 ]; then
    warn "root privileges required for 'lb build'; run: sudo ./build.sh"
fi

REQUIRED_COMMANDS=(
    lb debootstrap xorriso mksquashfs dpkg-deb
    python3 git curl cp find sha256sum
)
for cmd in "${REQUIRED_COMMANDS[@]}"; do
    if command -v "$cmd" >/dev/null 2>&1; then
        note "command ok: $cmd -> $(command -v "$cmd")"
    else
        warn "command '$cmd' not found (install live-build, debootstrap, xorriso, squashfs-tools, dpkg-dev, git, python3, curl, coreutils)"
    fi
done

# Bootloader assets are files, not commands. live-build needs them for
# iso-hybrid with syslinux (BIOS) and grub-efi (UEFI).
REQUIRED_FILES=(
    /usr/lib/ISOLINUX/isolinux.bin
)
for f in "${REQUIRED_FILES[@]}"; do
    if [ -f "$f" ]; then
        note "asset ok: $f"
    else
        warn "asset '$f' not found (install the Debian 'isolinux' package)"
    fi
done

REQUIRED_DIRS=(
    /usr/lib/grub/x86_64-efi
)
for d in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$d" ]; then
        note "asset ok: $d"
    else
        warn "asset directory '$d' not found (install grub-efi-amd64-bin)"
    fi
done

if command -v lb >/dev/null 2>&1; then
    note "live-build version: $(lb --version 2>/dev/null || echo unknown)"
fi

if [ "$SKIP_NETWORK" -eq 1 ]; then
    note "network check explicitly skipped (SANORA_SKIP_NETWORK_CHECK=1)"
else
    URL="${SANORA_DEBIAN_MIRROR}dists/${DEBIAN_SUITE}/Release"
    note "checking Debian mirror: $URL"
    if curl -fsSI --max-time 15 "$URL" >/dev/null 2>&1; then
        note "Debian mirror reachable"
    else
        warn "Debian mirror unreachable: $URL (live-build needs network access to deb.debian.org)"
    fi
fi

if [ "$FAIL" -ne 0 ]; then
    printf '\n[preflight] FAILED. Fix the items above, then run: sudo ./build.sh\n' >&2
    exit 1
fi

note "OK: host is ready for an ISO build attempt"
