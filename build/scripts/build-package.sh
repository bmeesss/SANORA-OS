#!/usr/bin/env bash
# Build the sanora-base binary package with dpkg-deb (no debhelper needed yet).
#
# Source:  packages/sanora-base/  (a dpkg-deb staging tree)
# Output:  build/work/packages/sanora-base_<version>_all.deb
#
# The staging tree is copied to a temporary directory so that the repository is
# never modified. DEBIAN/control is generated from control.in with the version
# from config/version.env, which is the single source of truth.

set -Eeuo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
# shellcheck disable=SC1091
source "$REPO_ROOT/config/version.env"

STAGE_SRC="$REPO_ROOT/packages/sanora-base"
OUT_DIR="$REPO_ROOT/build/work/packages"
DEB="$OUT_DIR/sanora-base_${SANORA_VERSION}_all.deb"

if ! command -v dpkg-deb >/dev/null 2>&1; then
    echo "build-package: dpkg-deb is required (package: dpkg)" >&2
    exit 1
fi
if [ ! -f "$STAGE_SRC/DEBIAN/control.in" ]; then
    echo "build-package: missing $STAGE_SRC/DEBIAN/control.in" >&2
    exit 1
fi

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
cp -a "$STAGE_SRC/." "$TMP/"

sed -e "s|@SANORA_VERSION@|${SANORA_VERSION}|g" \
    "$STAGE_SRC/DEBIAN/control.in" > "$TMP/DEBIAN/control"
rm -f "$TMP/DEBIAN/control.in"

# Maintainer scripts and helper binaries must be executable in the package.
chmod 0755 "$TMP/DEBIAN/preinst" "$TMP/DEBIAN/postrm" \
           "$TMP/usr/bin/sanora-info"

mkdir -p "$OUT_DIR"
rm -f "$DEB"
dpkg-deb --build --root-owner-group "$TMP" "$DEB"

echo "build-package: created $DEB"
dpkg-deb --field "$DEB" Package Version Architecture
