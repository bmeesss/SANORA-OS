#!/usr/bin/env bash
# SANORA OS development ISO build entrypoint.
#
#   ./build.sh --check          offline validation (no root, no network)
#   ./build.sh --config-only    build sanora-base + assemble live-build config
#   sudo ./build.sh             full ISO build into ./out/
#   ./build.sh --clean          remove generated build/work and out contents
#   ./build.sh --help           this text
#
# This script is intentionally explicit. Every step, mapping and dependency is
# documented in docs/development/BUILDING.md. It calls upstream Debian
# live-build (`lb config` / `lb build`); there is no custom ISO builder.

set -Eeuo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPTS="$REPO_ROOT/build/scripts"
WORK="$REPO_ROOT/build/work"
LIVE="$WORK/live"
OUT="$REPO_ROOT/out"

# shellcheck disable=SC1091
source "$REPO_ROOT/config/version.env"
# shellcheck disable=SC1091
source "$REPO_ROOT/build/live-build/options.sh"

MODE="build"
SKIP_NETWORK="0"

usage() {
    sed -n '2,12p' "$0" | sed 's/^# \{0,1\}//'
}

while [ "$#" -gt 0 ]; do
    case "$1" in
        --check) MODE="check" ;;
        --config-only) MODE="config-only" ;;
        --clean) MODE="clean" ;;
        --skip-network-check) SKIP_NETWORK="1" ;;
        --help|-h) usage; exit 0 ;;
        *) printf 'build.sh: unknown argument: %s\n' "$1" >&2; usage >&2; exit 2 ;;
    esac
    shift
done

# Reproducible environment. SOURCE_DATE_EPOCH is derived from the git commit,
# not from the wall clock, so two checkouts of the same commit agree.
if [ -z "${SOURCE_DATE_EPOCH:-}" ]; then
    SOURCE_DATE_EPOCH="$(git -C "$REPO_ROOT" log -1 --format=%ct 2>/dev/null || echo 0)"
fi
export SOURCE_DATE_EPOCH
export TZ=UTC LC_ALL=C LANG=C
SANORA_BUILD_ID="$(git -C "$REPO_ROOT" rev-parse --short HEAD 2>/dev/null || echo unknown)-${SOURCE_DATE_EPOCH}"
export SANORA_BUILD_ID
export SANORA_SKIP_NETWORK_CHECK="$SKIP_NETWORK"

write_metadata() {
    local status="$1" error="${2:-}"
    python3 "$SCRIPTS/write-metadata.py" \
        --out "$OUT" --work "$LIVE" --repo "$REPO_ROOT" \
        --mode "$MODE" --status "$status" --error "$error"
}

fail() {
    printf '\nbuild.sh: FAILED: %s\n' "$1" >&2
    mkdir -p "$OUT"
    write_metadata "failed" "$1" || true
    exit 1
}

log() { printf '\n==> %s\n' "$*"; }

case "$MODE" in
    check)
        log "Running offline validation suite"
        if [ ! -x "$REPO_ROOT/tests/run.sh" ]; then
            echo "build.sh: tests/run.sh is missing" >&2
            exit 1
        fi
        exec "$REPO_ROOT/tests/run.sh"
        ;;

    clean)
        log "Cleaning generated files"
        rm -rf "$WORK"
        if [ -d "$OUT" ]; then
            find "$OUT" -mindepth 1 -delete
        fi
        echo "build.sh: removed build/work and contents of out/"
        exit 0
        ;;
esac

mkdir -p "$WORK" "$OUT"

if [ "$MODE" = "build" ]; then
    log "Step 1/7 - host preflight"
    "$SCRIPTS/preflight.sh" || fail "host preflight failed (see [preflight] MISSING lines above)"
fi

log "Step 2/7 - build sanora-base Debian package"
"$SCRIPTS/build-package.sh" || fail "could not build sanora-base package"

log "Step 3/7 - configure Debian live-build"
rm -rf "$LIVE/config"
mkdir -p "$LIVE"
if command -v lb >/dev/null 2>&1; then
    ( cd "$LIVE" && lb config "${LB_OPTIONS[@]}" ) \
        || fail "lb config failed"
    echo "build.sh: lb config completed with ${#LB_OPTIONS[@]} argument tokens"
else
    if [ "$MODE" = "build" ]; then
        fail "lb (live-build) is not installed; preflight should have caught this"
    fi
    printf 'build.sh: WARNING: lb not installed; assembling SANORA inputs only (no generated config/{common,bootstrap,chroot,binary})\n' >&2
fi

log "Step 4/7 - assemble SANORA configuration, defaults and branding"
"$SCRIPTS/assemble-config.sh" "$LIVE" || fail "configuration assembly failed"

if [ "$MODE" = "config-only" ]; then
    log "Configuration-only mode: stopping before ISO build"
    write_metadata "success" "" || fail "could not write build metadata"
    printf '\nbuild.sh: assembled config tree at %s/config\n' "$LIVE"
    printf 'build.sh: metadata at %s/build-metadata.json\n' "$OUT"
    exit 0
fi

log "Step 5/7 - lb build (ISO)"
# `if !` suppresses set -e for this pipeline; pipefail ensures a failing
# lb build is still reported even though tee succeeds.
if ! ( cd "$LIVE" && lb build 2>&1 ) | tee "$LIVE/build.log"; then
    fail "lb build failed; inspect $LIVE/build.log"
fi

log "Step 6/7 - collect ISO artifact"
ISO="$(find "$LIVE" -maxdepth 1 -type f -name '*.iso' -print -quit)"
if [ -z "$ISO" ]; then
    fail "lb build finished but produced no .iso in $LIVE"
fi
ISO_OUT="$OUT/sanora-${SANORA_VERSION}-${SANORA_ARCH}.iso"
cp "$ISO" "$ISO_OUT"
echo "build.sh: ISO -> $ISO_OUT ($(stat -c %s "$ISO_OUT") bytes)"

# live-build may also emit its own SHA256SUMS; keep it next to our artifact.
for extra in SHA256SUMS sha256sums.txt; do
    if [ -f "$LIVE/$extra" ]; then
        cp "$LIVE/$extra" "$OUT/live-build-$extra"
    fi
done

log "Step 7/7 - write build metadata and checksums"
write_metadata "success" "" || fail "could not write build metadata"
printf '\nbuild.sh: DONE. Verify the ISO before claiming it boots.\n'
