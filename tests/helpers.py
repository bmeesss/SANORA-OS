"""Shared helpers for the SANORA OS offline test suite.

No third-party dependencies: Python 3 standard library only.
"""

import os
import pathlib
import subprocess

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
BUILD_EPOCH = "1793573836"  # fixed, deterministic epoch used by tests


def run(cmd, env=None, cwd=None, check=True):
    """Run a command, returning CompletedProcess. Raises on failure by default."""
    merged = os.environ.copy()
    if env:
        merged.update(env)
    return subprocess.run(
        cmd, cwd=cwd or str(REPO_ROOT), env=merged,
        capture_output=True, text=True, check=check,
    )


def read_version_env():
    values = {}
    for line in (REPO_ROOT / "config" / "version.env").read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def build_package():
    """Build exactly one sanora-base .deb with a deterministic epoch."""
    out_dir = REPO_ROOT / "build" / "work" / "packages"
    out_dir.mkdir(parents=True, exist_ok=True)
    for old in out_dir.glob("*.deb"):
        old.unlink()
    result = run(
        ["bash", str(REPO_ROOT / "build" / "scripts" / "build-package.sh")],
        env={"SOURCE_DATE_EPOCH": BUILD_EPOCH},
    )
    debs = sorted(out_dir.glob("*.deb"))
    if len(debs) != 1:
        raise AssertionError(
            f"expected exactly one .deb, got {len(debs)}; build output:\n{result.stdout}\n{result.stderr}"
        )
    return debs[0]


def package_names():
    """Return (name, source file) tuples from every package list."""
    entries = []
    for path in sorted((REPO_ROOT / "config" / "packages").glob("*.list.chroot")):
        for line in path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            entries.append((line, path.name))
    return entries
