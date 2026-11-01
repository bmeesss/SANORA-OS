#!/usr/bin/env python3
"""Write deterministic build metadata and SHA256 checksums for SANORA OS.

This is deliberately plain Python 3 with no third-party dependencies so that
it also runs in offline CI. Timestamps come from SOURCE_DATE_EPOCH (never from
the wall clock) so metadata does not by itself make a build non-reproducible.
"""

import argparse
import datetime
import hashlib
import json
import os
import pathlib
import shutil
import subprocess


def sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_version_env(path: pathlib.Path) -> dict:
    values = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def run(cmd: list) -> str:
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, help="output directory (e.g. ./out)")
    parser.add_argument("--work", required=True, help="live-build work directory")
    parser.add_argument("--repo", required=True, help="repository root")
    parser.add_argument("--mode", required=True, choices=["build", "config-only"])
    parser.add_argument("--status", required=True, choices=["success", "failed"])
    parser.add_argument("--error", default="", help="failure description")
    args = parser.parse_args()

    repo = pathlib.Path(args.repo)
    out = pathlib.Path(args.out)
    work = pathlib.Path(args.work)
    out.mkdir(parents=True, exist_ok=True)

    env = read_version_env(repo / "config" / "version.env")
    epoch = int(os.environ.get("SOURCE_DATE_EPOCH", "0"))
    build_id = os.environ.get("SANORA_BUILD_ID", "unknown")
    commit = run(["git", "-C", str(repo), "rev-parse", "HEAD"])
    live_build_version = (
        run(["lb", "--version"]) if shutil.which("lb") else "not-installed"
    )

    package_lists = {}
    for path in sorted((repo / "config" / "packages").glob("*.list.chroot")):
        package_lists[path.name] = sha256(path)

    deb_dir = repo / "build" / "work" / "packages"
    debs = sorted(deb_dir.glob("*.deb"))
    sanora_base = (
        {"filename": debs[0].name, "sha256": sha256(debs[0]), "size_bytes": debs[0].stat().st_size}
        if debs
        else None
    )

    isos = sorted(out.glob("*.iso"))
    iso_info = None
    if isos:
        iso = isos[0]
        iso_info = {
            "filename": iso.name,
            "size_bytes": iso.stat().st_size,
            "sha256": sha256(iso),
        }

    metadata = {
        "schema": "sanora.build-metadata/1",
        "status": args.status,
        "mode": args.mode,
        "error": args.error or None,
        "product": {
            "name": env.get("SANORA_NAME", "SANORA OS"),
            "id": env.get("SANORA_ID", "sanora"),
            "version": env.get("SANORA_VERSION"),
            "codename": env.get("SANORA_CODENAME"),
            "homepage": env.get("SANORA_HOMEPAGE"),
        },
        "build": {
            "build_id": build_id,
            "source_date_epoch": epoch,
            "build_date_utc": datetime.datetime.fromtimestamp(
                epoch, datetime.timezone.utc
            ).isoformat().replace("+00:00", "Z"),
            "git_commit": commit,
            "live_build_version": live_build_version,
            "work_directory": str(work),
            "host_os": run(["bash", "-c", '. /etc/os-release; echo "$PRETTY_NAME"']),
            "host_architecture": run(["dpkg", "--print-architecture"]),
        },
        "base": {
            "distribution": "Debian",
            "suite": env.get("DEBIAN_SUITE"),
            "version": env.get("DEBIAN_VERSION"),
            "architecture": env.get("SANORA_ARCH"),
            "desktop": "KDE Plasma on Wayland",
            "kernel": "Debian linux-image-amd64 (no custom kernel)",
            "build_tool": "Debian live-build (lb config / lb build)",
        },
        "defaults": {
            "language": env.get("SANORA_DEFAULT_LOCALE"),
            "keyboard": env.get("SANORA_DEFAULT_KEYBOARD"),
            "ui_language": "en",
            "international": True,
        },
        "inputs": {
            "package_lists_sha256": package_lists,
            "sanora_base_deb": sanora_base,
        },
        "artifact": iso_info,
        "gates": {
            "nvidia_in_iso": "BLOCKED - ADR-0007 awaiting confirmation",
            "boot_tested": False,
            "reproducibility_verified": False,
        },
    }

    (out / "build-metadata.json").write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    # Checksums for artifacts that actually exist. Never list a missing ISO.
    checksum_entries = []
    for path in sorted(out.iterdir()):
        if path.is_file() and path.name not in {"SHA256SUMS", "build-metadata.json"}:
            checksum_entries.append(f"{sha256(path)}  {path.name}\n")
    (out / "SHA256SUMS").write_text("".join(checksum_entries), encoding="utf-8")

    print(f"metadata: wrote {out / 'build-metadata.json'}")
    print(f"metadata: status={args.status} mode={args.mode} iso={iso_info['filename'] if iso_info else 'none'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
