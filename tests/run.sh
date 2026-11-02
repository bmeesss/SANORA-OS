#!/usr/bin/env bash
# SANORA OS offline validation suite. No root, no network, no live-build needed.
# Used by `./build.sh --check` and by the GitHub Actions validation workflow.

set -Eeuo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

echo "=== 1/5 Shell syntax (bash -n) ==="
SHELL_FILES=(
    build.sh
    build/scripts/preflight.sh
    build/scripts/build-package.sh
    build/scripts/assemble-config.sh
    build/scripts/collect-versions.sh
    build/live-build/options.sh
    build/live-build/hooks/normal/0010-sanora-locale.hook.chroot
    build/live-build/hooks/normal/0020-sanora-calamares-branding.hook.chroot
    packages/sanora-base/DEBIAN/preinst
    packages/sanora-base/DEBIAN/postrm
    packages/sanora-base/usr/bin/sanora-info
    tests/run.sh
)
for f in "${SHELL_FILES[@]}"; do
    bash -n "$f" || { echo "FAILED: bash -n $f" >&2; exit 1; }
    printf '  ok  %s\n' "$f"
done

echo "=== 2/5 Python syntax ==="
python3 -m py_compile \
    build/scripts/write-metadata.py \
    tests/helpers.py tests/test_static.py tests/test_package.py \
    tests/test_assemble.py tests/check_package_names.py tests/boot/qemu_boot.py
echo "  ok  py_compile (6 modules)"

echo "=== 3/5 Optional ShellCheck ==="
if command -v shellcheck >/dev/null 2>&1; then
    shellcheck -x -S warning "${SHELL_FILES[@]}" || { echo "FAILED: shellcheck" >&2; exit 1; }
    echo "  ok  shellcheck (warnings and above)"
else
    echo "  SKIPPED: shellcheck is not installed -- NOT reported as passed"
fi

echo "=== 4/5 Offline package-list check ==="
python3 tests/check_package_names.py | tail -3

echo "=== 5/5 Unit tests (static / package / assembly) ==="
PYTHONPATH="$REPO_ROOT/tests" python3 -m unittest discover \
    -s "$REPO_ROOT/tests" -p 'test_*.py' -v

echo
echo "=== RESULT: all executed checks passed ==="
echo "NOTE: no ISO build and no boot test is part of this suite."
