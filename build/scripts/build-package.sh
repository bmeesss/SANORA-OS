#!/usr/bin/env bash
# Build the sanora-base binary package with dpkg-deb (no debhelper needed yet).
#
# Source inputs (single source of truth, no duplicated copies):
#   packages/sanora-base/     DEBIAN metadata + usr/bin/sanora-info
#   config/version.env        version, identity, base distribution
#   config/system/*           /etc defaults
#   config/desktop/*          KDE defaults
#   branding/*                original logo + wallpaper (SVG and PNG)
#   installer/calamares/      Calamares branding.desc + show.qml
#
# Output: build/work/packages/sanora-base_<version>_all.deb
#
# The staging tree is assembled in a temporary directory; the repository is
# never modified. Version-dependent files are generated, not hard-coded.

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

for required in \
    "$STAGE_SRC/DEBIAN/control.in" \
    "$STAGE_SRC/DEBIAN/preinst" \
    "$STAGE_SRC/DEBIAN/postrm" \
    "$STAGE_SRC/DEBIAN/copyright" \
    "$STAGE_SRC/usr/bin/sanora-info" \
    "$REPO_ROOT/config/system/sanora.conf" \
    "$REPO_ROOT/config/system/99-sanora-security" \
    "$REPO_ROOT/config/system/10-sanora-user.conf" \
    "$REPO_ROOT/config/desktop/kdeglobals" \
    "$REPO_ROOT/config/desktop/plasma-org.kde.plasma.desktop-appletsrc" \
    "$REPO_ROOT/branding/sanora-logo.svg" \
    "$REPO_ROOT/branding/sanora-logo.png" \
    "$REPO_ROOT/branding/sanora-wallpaper.svg" \
    "$REPO_ROOT/branding/sanora-wallpaper.png" \
    "$REPO_ROOT/installer/calamares/branding/sanora/branding.desc" \
    "$REPO_ROOT/installer/calamares/branding/sanora/show.qml"
do
    if [ ! -e "$required" ]; then
        echo "build-package: required input missing: $required" >&2
        exit 1
    fi
done

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
cp -a "$STAGE_SRC/." "$TMP/"
# The staging tree's README.md is developer documentation, not a payload file.
rm -f "$TMP/README.md"

mkdir -p \
    "$TMP/etc/sanora" \
    "$TMP/etc/apt/apt.conf.d" \
    "$TMP/etc/live/config.conf.d" \
    "$TMP/etc/xdg" \
    "$TMP/etc/skel/.config" \
    "$TMP/etc/calamares/branding/sanora" \
    "$TMP/usr/share/sanora/branding" \
    "$TMP/usr/share/sanora/wallpapers" \
    "$TMP/usr/share/doc/sanora-base"

# 1. Package metadata.
sed -e "s|@SANORA_VERSION@|${SANORA_VERSION}|g" \
    "$STAGE_SRC/DEBIAN/control.in" > "$TMP/DEBIAN/control"
rm -f "$TMP/DEBIAN/control.in"

# 2. Generated version-dependent identity files.
cat > "$TMP/etc/os-release" <<EOF
PRETTY_NAME="SANORA OS ${SANORA_VERSION} (${SANORA_CODENAME})"
NAME="SANORA OS"
VERSION_ID="${SANORA_VERSION}"
VERSION="${SANORA_VERSION} (${SANORA_CODENAME})"
VERSION_CODENAME="${SANORA_CODENAME}"
ID="${SANORA_ID}"
ID_LIKE="debian"
HOME_URL="${SANORA_HOMEPAGE}"
SUPPORT_URL="${SANORA_HOMEPAGE}"
BUG_REPORT_URL="${SANORA_HOMEPAGE}/issues"
DEFAULT_LANGUAGE="en"
SANORA_BASE_DISTRIBUTION="Debian ${DEBIAN_VERSION} (${DEBIAN_SUITE})"
EOF

cat > "$TMP/etc/sanora/release" <<EOF
SANORA_NAME="SANORA OS"
SANORA_ID=${SANORA_ID}
SANORA_VERSION=${SANORA_VERSION}
SANORA_CODENAME=${SANORA_CODENAME}
SANORA_BASE=debian
SANORA_BASE_SUITE=${DEBIAN_SUITE}
SANORA_ARCH=${SANORA_ARCH}
SANORA_DEFAULT_LOCALE=${SANORA_DEFAULT_LOCALE}
SANORA_DEFAULT_LANGUAGE=en
EOF

# 3. /etc defaults (no upstream file is patched).
cp "$REPO_ROOT/config/system/sanora.conf"         "$TMP/etc/sanora/sanora.conf"
cp "$REPO_ROOT/config/system/99-sanora-security"  "$TMP/etc/apt/apt.conf.d/99-sanora-security"
cp "$REPO_ROOT/config/system/10-sanora-user.conf" "$TMP/etc/live/config.conf.d/10-sanora-user.conf"
cp "$REPO_ROOT/config/desktop/kdeglobals"          "$TMP/etc/xdg/kdeglobals"
cp "$REPO_ROOT/config/desktop/plasma-org.kde.plasma.desktop-appletsrc" \
                                                    "$TMP/etc/skel/.config/plasma-org.kde.plasma.desktop-appletsrc"

# 4. Original branding assets.
cp "$REPO_ROOT/branding/sanora-logo.svg"        "$TMP/usr/share/sanora/branding/"
cp "$REPO_ROOT/branding/sanora-logo.png"        "$TMP/usr/share/sanora/branding/"
cp "$REPO_ROOT/branding/sanora-wallpaper.svg"   "$TMP/usr/share/sanora/wallpapers/"
cp "$REPO_ROOT/branding/sanora-wallpaper.png"   "$TMP/usr/share/sanora/wallpapers/"

# 5. Calamares branding component (Debian's settings.conf/module configs are
#    reused; hook 0020 only switches the single `branding` key).
cp "$REPO_ROOT/installer/calamares/branding/sanora/branding.desc" \
   "$TMP/etc/calamares/branding/sanora/branding.desc"
cp "$REPO_ROOT/installer/calamares/branding/sanora/show.qml" \
   "$TMP/etc/calamares/branding/sanora/show.qml"
cp "$REPO_ROOT/branding/sanora-logo.png" \
   "$TMP/etc/calamares/branding/sanora/sanora-logo.png"

cp "$STAGE_SRC/DEBIAN/copyright" "$TMP/usr/share/doc/sanora-base/copyright"

# 6. Permissions.
chmod 0755 "$TMP/DEBIAN/preinst" "$TMP/DEBIAN/postrm" "$TMP/usr/bin/sanora-info"
find "$TMP/usr" -type f -exec chmod 0644 {} +
chmod 0755 "$TMP/usr/bin/sanora-info"
find "$TMP/etc" -type f -exec chmod 0644 {} +

# dpkg-deb records file mtimes in the data tarball. Clamp them to
# SOURCE_DATE_EPOCH so the package is byte-reproducible for a given commit,
# independent of when the developer checked out the repository.
: "${SOURCE_DATE_EPOCH:=0}"
find "$TMP" -exec touch -h -d "@${SOURCE_DATE_EPOCH}" {} +

mkdir -p "$OUT_DIR"
rm -f "$DEB"
dpkg-deb --build --root-owner-group "$TMP" "$DEB"

echo "build-package: created $DEB"
dpkg-deb --field "$DEB" Package Version Architecture
