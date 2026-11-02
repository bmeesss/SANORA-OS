#!/usr/bin/env bash
# Measure actual component versions from the live-build chroot after a build.
# Written to build/work/versions.json and merged into out/build-metadata.json
# by write-metadata.py. Guesses are never written: a missing value is null.

set -Eeuo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
CHROOT="$REPO_ROOT/build/work/live/chroot"
OUT="$REPO_ROOT/build/work/versions.json"

kernel_versions=""
plasma_desktop=""
plasma_workspace=""
kwin_wayland=""
calamares=""
sddm=""
base_files=""
live_build_ver=""
debian_release=""

if [ -x "$CHROOT/usr/bin/dpkg-query" ]; then
    q() { chroot "$CHROOT" dpkg-query -W -f='${Version}' "$1" 2>/dev/null || true; }
    kernel_versions="$(chroot "$CHROOT" /bin/sh -c \
        'ls /boot/vmlinuz-* 2>/dev/null | sed "s|.*/vmlinuz-||"' | tr '\n' ' ' | sed 's/ *$//')"
    plasma_desktop="$(q plasma-desktop)"
    plasma_workspace="$(q plasma-workspace)"
    kwin_wayland="$(q kwin-wayland)"
    calamares="$(q calamares)"
    sddm="$(q sddm)"
    base_files="$(q base-files)"
    if [ -r "$CHROOT/etc/debian_version" ]; then
        debian_release="$(tr -d '\n' < "$CHROOT/etc/debian_version")"
    fi
fi
if command -v lb >/dev/null 2>&1; then
    live_build_ver="$(lb --version 2>/dev/null || true)"
fi

KERNEL_VERSIONS="$kernel_versions" \
PLASMA_DESKTOP="$plasma_desktop" \
PLASMA_WORKSPACE="$plasma_workspace" \
KWIN_WAYLAND="$kwin_wayland" \
CALAMARES="$calamares" \
SDDM="$sddm" \
BASE_FILES="$base_files" \
LIVE_BUILD="$live_build_ver" \
DEBIAN_RELEASE="$debian_release" \
python3 - "$OUT" <<'PY'
import json, os, sys

def val(key):
    v = os.environ.get(key, "").strip()
    return v if v else None

data = {
    "measured": bool(os.environ.get("PLASMA_DESKTOP", "").strip()),
    "kernel_image_versions": (
        os.environ.get("KERNEL_VERSIONS", "").split() or None
    ),
    "plasma_desktop": val("PLASMA_DESKTOP"),
    "plasma_workspace": val("PLASMA_WORKSPACE"),
    "kwin_wayland": val("KWIN_WAYLAND"),
    "calamares": val("CALAMARES"),
    "sddm": val("SDDM"),
    "base_files": val("BASE_FILES"),
    "live_build": val("LIVE_BUILD"),
    "debian_release": val("DEBIAN_RELEASE"),
}
with open(sys.argv[1], "w", encoding="utf-8") as fh:
    json.dump(data, fh, indent=2, sort_keys=True)
    fh.write("\n")
print("collect-versions: wrote " + sys.argv[1])
print(json.dumps(data, indent=2, sort_keys=True))
PY
