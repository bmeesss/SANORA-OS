#!/usr/bin/env python3
"""Validate package names against the official Debian package database.

Offline (default): parse and list the names, no network.
Online (--online): GET https://packages.debian.org/<suite>/<name> for every
unique package and assert the page is a real "Details of package" page.

This check is optional in CI because it depends on a third-party web service.
When the network is unavailable it reports UNKNOWN and exits non-zero -- it
never claims success without evidence.
"""

import argparse
import sys
import urllib.error
import urllib.request

from helpers import package_names, read_version_env


def check_online(names, suite, timeout):
    problems = []
    session_cache = {}
    for name in names:
        if name in session_cache:
            continue
        url = f"https://packages.debian.org/{suite}/{name}"
        try:
            with urllib.request.urlopen(url, timeout=timeout) as response:
                body = response.read().decode("utf-8", "replace")
            ok = f"Package: {name} " in body or f"Package: {name}</" in body
            if not ok:
                ok = "Details of package" in body and f"in {suite}" in body
            session_cache[name] = ok
            print(f"  {'OK     ' if ok else 'MISSING'} {name}")
            if not ok:
                problems.append(name)
        except (urllib.error.URLError, OSError) as exc:
            print(f"  UNKNOWN {name}: {exc}", file=sys.stderr)
            problems.append(f"{name} (network error)")
    return problems


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--online", action="store_true",
                        help="query packages.debian.org (needs network)")
    parser.add_argument("--suite", default=None,
                        help="Debian suite (default: DEBIAN_SUITE from version.env)")
    parser.add_argument("--timeout", type=int, default=15)
    args = parser.parse_args()

    suite = args.suite or read_version_env()["DEBIAN_SUITE"]
    unique = sorted({name for name, _ in package_names()})
    print(f"SANORA OS package set: {len(unique)} unique packages, suite={suite}")

    if not args.online:
        for name in unique:
            print(f"  {name}")
        print("Offline syntax check only. Re-run with --online to verify names.")
        return 0

    problems = check_online(unique, suite, args.timeout)
    if problems:
        print(f"\nFAILED: {len(problems)} package(s) could not be verified:",
              file=sys.stderr)
        for item in problems:
            print(f"  - {item}", file=sys.stderr)
        return 1
    print(f"\nOK: all {len(unique)} package names exist in Debian {suite}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
