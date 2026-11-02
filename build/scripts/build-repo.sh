#!/usr/bin/env bash
# Build a small, GPG-signed local SANORA APT repository for the ISO build.
#
# This replaces permanent reliance on live-build's `config/packages.chroot/`
# (which the Debian Live Manual states cannot use secure APT). The repository
# is build-time only: live-build bind-mounts the file:// URI into the chroot,
# imports the public key, and installs `sanora-base` from the signed archive.
#
# Outputs (all under build/work/, ignored by git):
#   repo/pool/main/...                       the .deb
#   repo/dists/sanora/main/binary-amd64/     Packages, Packages.gz
#   repo/dists/sanora/Release               Release metadata
#   repo/dists/sanora/Release.gpg           detached signature
#   repo/dists/sanora/InRelease             clear-signed Release
#   repo/sanora-archive-key.asc             armoured public key
#   repo-key-id                             key fingerprint used
#
# Key management:
#   * SANORA_REPO_KEY_ID   - use an existing key in the default keyring.
#   * SANORA_REPO_AUTO_KEY=1 - generate an EPHEMERAL development key in
#     build/work/gnupg. This is for dev/CI ISOs only. A release archive must
#     use an offline-managed key; see repo/README.md (ADR-0012).
#
# Requires: apt-utils (apt-ftparchive), gnupg, dpkg-dev, gzip.

set -Eeuo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
# shellcheck disable=SC1091
source "$REPO_ROOT/config/version.env"

WORK="$REPO_ROOT/build/work"
REPO="$WORK/repo"
DEB="$WORK/packages/sanora-base_${SANORA_VERSION}_all.deb"
GPG_BIN="${SANORA_GPG_BIN:-gpg}"

: "${SOURCE_DATE_EPOCH:=0}"
EPOCH_DATE="$(date -u -d "@${SOURCE_DATE_EPOCH}" '+%a, %d %b %Y %H:%M:%S UTC')"

for tool in "$GPG_BIN" apt-ftparchive gzip; do
    if ! command -v "$tool" >/dev/null 2>&1; then
        echo "build-repo: required tool missing: $tool" >&2
        exit 1
    fi
done
if [ ! -f "$DEB" ]; then
    echo "build-repo: missing $DEB (run build-package.sh first)" >&2
    exit 1
fi

KEY_ID="${SANORA_REPO_KEY_ID:-}"
# Keep the development keyring OUTSIDE build/work: `build.sh --clean` removes
# build/work before the reproducibility second build, and a new random key on
# each build would make the two signed archives (and any traces in the image)
# differ. A stable per-checkout key keeps both builds identical.
GNUPGHOME="${SANORA_REPO_GNUPGHOME:-$REPO_ROOT/.sanora-dev-gnupg}"
export GNUPGHOME
mkdir -p "$GNUPGHOME"
chmod 0700 "$GNUPGHOME"
# The fingerprint must live with the persistent keyring, NOT in build/work:
# `build.sh --clean` wipes build/work before the reproducibility second build.
KEY_ID_FILE="$GNUPGHOME/repo-key-id"

if [ -z "$KEY_ID" ] && [ -f "$KEY_ID_FILE" ]; then
    KEY_ID="$(tr -d '\n' < "$KEY_ID_FILE")"
fi
if [ -z "$KEY_ID" ]; then
    if [ "${SANORA_REPO_AUTO_KEY:-0}" != "1" ]; then
        echo "build-repo: no signing key. Set SANORA_REPO_KEY_ID or SANORA_REPO_AUTO_KEY=1." >&2
        echo "build-repo: refusing to fall back to an unsigned archive." >&2
        exit 1
    fi
    "$GPG_BIN" --batch --pinentry-mode loopback --passphrase '' \
        --quick-generate-key "SANORA OS development archive <archive@sanora.invalid>" \
        rsa3072 sign 0 >/dev/null 2>&1
    KEY_ID="$("$GPG_BIN" --list-secret-keys --with-colons \
        | awk -F: '/^fpr:/ {print $10; exit}')"
    if [ -z "$KEY_ID" ]; then
        echo "build-repo: could not determine generated key fingerprint" >&2
        exit 1
    fi
    printf '%s\n' "$KEY_ID" > "$KEY_ID_FILE"
    echo "build-repo: generated EPHEMERAL development key $KEY_ID"
fi
printf '%s\n' "$KEY_ID" > "$WORK/repo-key-id"

rm -rf "$REPO"
mkdir -p "$REPO/pool/main/s/sanora-base" \
         "$REPO/dists/sanora/main/binary-amd64"
cp "$DEB" "$REPO/pool/main/s/sanora-base/"

( cd "$REPO" && apt-ftparchive packages pool/main \
    > dists/sanora/main/binary-amd64/Packages )
# -n omits the gzip timestamp so the archive metadata is deterministic.
gzip -9 -n -c "$REPO/dists/sanora/main/binary-amd64/Packages" \
    > "$REPO/dists/sanora/main/binary-amd64/Packages.gz"

# Write Release outside the directory being scanned, then move it in, so the
# partially written file cannot be included in its own checksum list.
( cd "$REPO" && apt-ftparchive \
    -o "APT::FTPArchive::Release::Origin=SANORA OS" \
    -o "APT::FTPArchive::Release::Label=SANORA OS" \
    -o "APT::FTPArchive::Release::Suite=sanora" \
    -o "APT::FTPArchive::Release::Codename=${SANORA_CODENAME}" \
    -o "APT::FTPArchive::Release::Architectures=${SANORA_ARCH}" \
    -o "APT::FTPArchive::Release::Components=main" \
    -o "APT::FTPArchive::Release::Description=SANORA OS development archive" \
    -o "APT::FTPArchive::Release::Date=${EPOCH_DATE}" \
    release dists/sanora > "$WORK/Release.generated" )
mv "$WORK/Release.generated" "$REPO/dists/sanora/Release"

"$GPG_BIN" --batch --yes --pinentry-mode loopback --passphrase '' \
    --armor --detach-sign \
    -o "$REPO/dists/sanora/Release.gpg" "$REPO/dists/sanora/Release" >/dev/null 2>&1
"$GPG_BIN" --batch --yes --pinentry-mode loopback --passphrase '' \
    --clearsign -o "$REPO/dists/sanora/InRelease" \
    "$REPO/dists/sanora/Release" >/dev/null 2>&1
"$GPG_BIN" --batch --armor --export "$KEY_ID" \
    > "$REPO/sanora-archive-key.asc" 2>/dev/null

"$GPG_BIN" --batch --verify "$REPO/dists/sanora/Release.gpg" \
    "$REPO/dists/sanora/Release" >/dev/null 2>&1 \
    || { echo "build-repo: signature verification FAILED" >&2; exit 1; }

cat > "$WORK/repo-metadata.json" <<EOF
{
  "key_fingerprint": "${KEY_ID}",
  "key_is_ephemeral": $([ -f "$KEY_ID_FILE" ] && echo true || echo false),
  "suite": "sanora",
  "component": "main",
  "architecture": "${SANORA_ARCH}",
  "packages": ["sanora-base"],
  "signature_verified": true,
  "source_date_epoch": ${SOURCE_DATE_EPOCH}
}
EOF

echo "build-repo: signed repository at $REPO (key $KEY_ID)"
