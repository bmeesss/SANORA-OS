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
#   config/desktop/, config/system/, branding/, installer/
#                                  -> config/includes.chroot/
#   branding/iso/                 -> config/includes.binary/

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
         "$INC/etc/sanora" "$INC/etc/apt/apt.conf.d" \
         "$INC/etc/live/config.conf.d" "$INC/etc/xdg" \
         "$INC/etc/skel/.config" "$INC/etc/calamares/branding/sanora" \
         "$INC/usr/share/sanora/branding" "$INC/usr/share/sanora/wallpapers" \
         "$BIN/.disk"

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

# 4. /etc and system defaults (upstream files are never edited directly).
need "$REPO_ROOT/config/system/sanora.conf"
need "$REPO_ROOT/config/system/99-sanora-security"
need "$REPO_ROOT/config/system/10-sanora-user.conf"
need "$REPO_ROOT/config/desktop/kdeglobals"
need "$REPO_ROOT/config/desktop/plasma-org.kde.plasma.desktop-appletsrc"

cp "$REPO_ROOT/config/system/sanora.conf"            "$INC/etc/sanora/sanora.conf"
cp "$REPO_ROOT/config/system/99-sanora-security"     "$INC/etc/apt/apt.conf.d/99-sanora-security"
cp "$REPO_ROOT/config/system/10-sanora-user.conf"    "$INC/etc/live/config.conf.d/10-sanora-user.conf"
cp "$REPO_ROOT/config/desktop/kdeglobals"             "$INC/etc/xdg/kdeglobals"
cp "$REPO_ROOT/config/desktop/plasma-org.kde.plasma.desktop-appletsrc" \
                                                      "$INC/etc/skel/.config/plasma-org.kde.plasma.desktop-appletsrc"

# 5. Original branding assets.
for asset in sanora-logo.svg sanora-logo.png; do
    need "$REPO_ROOT/branding/$asset"
    cp "$REPO_ROOT/branding/$asset" "$INC/usr/share/sanora/branding/$asset"
done
for asset in sanora-wallpaper.svg sanora-wallpaper.png; do
    need "$REPO_ROOT/branding/$asset"
    cp "$REPO_ROOT/branding/$asset" "$INC/usr/share/sanora/wallpapers/$asset"
done

# 6. Calamares branding directory (settings.conf comes from Debian and is
#    patched by hook 0020, which keeps the upstream module sequence intact).
for f in branding.desc show.qml sanora-logo.png; do
    need "$REPO_ROOT/installer/calamares/branding/sanora/$f"
    cp "$REPO_ROOT/installer/calamares/branding/sanora/$f" \
       "$INC/etc/calamares/branding/sanora/$f"
done

# 7. Deterministic build identity inside the image. No wall-clock timestamps.
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

# 8. Files visible on the ISO medium before booting.
need "$REPO_ROOT/branding/iso/README.txt"
need "$REPO_ROOT/branding/iso/disk-info"
sed -e "s|@SANORA_VERSION@|${SANORA_VERSION}|g" \
    "$REPO_ROOT/branding/iso/README.txt" > "$BIN/README.txt"
cp "$REPO_ROOT/branding/iso/disk-info" "$BIN/.disk/info"

echo "assemble-config: assembled live-build config tree at $CONF"
echo "assemble-config: package lists=${#LISTS[@]} hooks=${#HOOKS[@]} deb=$(basename "${DEBS[0]}")"
