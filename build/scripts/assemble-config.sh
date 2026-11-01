#!/usr/bin/env bash
# Assemble all SANORA-owned inputs into a live-build `config/` tree.
#
# This script does NOT run `lb config` and does NOT build an ISO. It is a pure,
# deterministic copy/mapping step, so it can be executed and tested offline.
#
# Usage: assemble-config.sh [target-live-dir]
#        (default: build/work/live)
#
# Mapping (documented in docs/development/BUILDING.md):
#   config/packages/*.list.chroot  -> config/package-lists/
#   build/work/packages/*.deb      -> config/packages.chroot/
#   build/live-build/hooks/normal/ -> config/hooks/normal/
#   generated build identity       -> config/includes.chroot/etc/sanora/
#   branding/iso/                 -> config/includes.binary/
#
# All other SANORA files (/etc defaults, KDE defaults, Calamares branding,
# wallpaper, logo, metadata, helper script) are delivered by the sanora-base
# Debian package in config/packages.chroot/. There is exactly one copy of each.

set -Eeuo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
# shellcheck disable=SC1091
source "$REPO_ROOT/config/version.env"

TARGET="${1:-$REPO_ROOT/build/work/live}"
CONF="$TARGET/config"
INC="$CONF/includes.chroot"
BIN="$CONF/includes.binary"

need() {
    if [ ! -e "$1" ]; then
        echo "assemble-config: required input missing: $1" >&2
        exit 1
    fi
}

mkdir -p "$CONF/package-lists" "$CONF/packages.chroot" "$CONF/hooks/normal" \
         "$INC/etc/sanora" "$BIN/.disk"

# 1. Explicit, reviewed package lists.
shopt -s nullglob
LISTS=("$REPO_ROOT"/config/packages/*.list.chroot)
shopt -u nullglob
if [ "${#LISTS[@]}" -eq 0 ]; then
    echo "assemble-config: no package lists found in config/packages/" >&2
    exit 1
fi
cp "${LISTS[@]}" "$CONF/package-lists/"

# 2. SANORA Debian package(s) installed by live-build via packages.chroot.
DEBS=("$REPO_ROOT"/build/work/packages/*.deb)
if [ "${#DEBS[@]}" -ne 1 ]; then
    echo "assemble-config: expected exactly one built .deb in build/work/packages/, found ${#DEBS[@]}" >&2
    exit 1
fi
cp "${DEBS[0]}" "$CONF/packages.chroot/"

# 3. Chroot hooks (execute at the end of the chroot stage).
HOOKS=("$REPO_ROOT"/build/live-build/hooks/normal/*.hook.chroot)
if [ "${#HOOKS[@]}" -eq 0 ]; then
    echo "assemble-config: no chroot hooks found" >&2
    exit 1
fi
cp "${HOOKS[@]}" "$CONF/hooks/normal/"
chmod 0755 "$CONF"/hooks/normal/*.hook.chroot

# 4. Deterministic build identity inside the image. No wall-clock timestamps.
#    Everything else in /etc comes from the sanora-base package.
: "${SOURCE_DATE_EPOCH:=0}"
: "${SANORA_BUILD_ID:=unknown}"
cat > "$INC/etc/sanora/build-info" <<EOF
SANORA_VERSION=${SANORA_VERSION}
SANORA_CODENAME=${SANORA_CODENAME}
SANORA_BUILD_ID=${SANORA_BUILD_ID}
SOURCE_DATE_EPOCH=${SOURCE_DATE_EPOCH}
DEBIAN_SUITE=${DEBIAN_SUITE}
DEBIAN_VERSION=${DEBIAN_VERSION}
SANORA_ARCH=${SANORA_ARCH}
SANORA_DEFAULT_LOCALE=${SANORA_DEFAULT_LOCALE}
EOF

# 5. Files visible on the ISO medium before booting.
need "$REPO_ROOT/branding/iso/README.txt"
need "$REPO_ROOT/branding/iso/disk-info"
sed -e "s|@SANORA_VERSION@|${SANORA_VERSION}|g" \
    "$REPO_ROOT/branding/iso/README.txt" > "$BIN/README.txt"
cp "$REPO_ROOT/branding/iso/disk-info" "$BIN/.disk/info"

echo "assemble-config: assembled live-build config tree at $CONF"
echo "assemble-config: package lists=${#LISTS[@]} hooks=${#HOOKS[@]} deb=$(basename "${DEBS[0]}")"
