#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""Drive the Calamares installer GUI from inside a disposable SANORA VM.

Runs INSIDE the guest, started by tests/install/qemu_install.py over the
serial console. It uses AT-SPI to discover widgets by accessible name (so it
does not depend on hardcoded screen coordinates) and xdotool to type and
click. Every step is logged; the final verdict is written as JSON.

Usage:
  calamares_driver.py [--encrypt] [--timeout 1800] [--user sanora]
                      [--password 'Sanora-Dev-2026!']

Requires: python3-pyatspi, xdotool, at-spi2-core (all in the dev ISO).
Calamares must be launched with QT_ACCESSIBILITY=1 and
QT_LINUX_ACCESSIBILITY_ALWAYS_ON=1.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time

LOG_PATH = "/tmp/sanora-calamares-driver.log"
RESULT_PATH = "/tmp/sanora-calamares-driver.json"

# Accessible names come from Calamares 3.3.14 .ui files:
#   users/page_usersetup.ui and partition/gui/EncryptWidget.ui
FIELD_VALUES = {
    "Your Full Name": "user",
    "login": "user",
    "Computer Name": "host",
    "Password": "password",
    "Repeat Password": "password",
    "Passphrase": "luks",
    "Confirm passphrase": "luks",
}

NEXT_NAMES = ("next", "install", "install now")


def log(msg: str) -> None:
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    print(line, flush=True)
    with open(LOG_PATH, "a", encoding="utf-8") as fh:
        fh.write(line + "\n")


def finish(status: str, detail: str, steps: list) -> None:
    result = {
        "status": status,
        "detail": detail,
        "steps": steps,
        "log": LOG_PATH,
    }
    with open(RESULT_PATH, "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, sort_keys=True)
    log(f"RESULT: {status} - {detail}")
    sys.exit(0 if status == "SUCCESS" else 1)


def xdo(*args: str) -> str:
    env = os.environ.copy()
    env.setdefault("DISPLAY", ":0")
    try:
        proc = subprocess.run(
            ["xdotool", *args], env=env, capture_output=True,
            text=True, timeout=30,
        )
        return proc.stdout.strip()
    except (OSError, subprocess.TimeoutExpired) as exc:
        log(f"xdotool {args[:2]} failed: {exc}")
        return ""


def app_node():
    import pyatspi

    desktop = pyatspi.Registry.getDesktop(0)
    for app in desktop:
        try:
            name = (app.name or "").lower()
        except Exception:  # noqa: BLE001
            continue
        if "calamares" in name:
            return app
    return None


def walk(node, depth=0, out=None, max_depth=18):
    if out is None:
        out = []
    if depth > max_depth or node is None:
        return out
    try:
        role = node.getRoleName()
        name = node.name or ""
        desc = node.description or ""
        x = y = w = h = 0
        try:
            comp = node.queryComponent()
            x, y, w, h = comp.getExtents(0)  # DESKTOP_COORDS
        except Exception:  # noqa: BLE001
            pass
        enabled = True
        try:
            state = node.getState()
            enabled = state.contains(pyatspi.STATE_SENSITIVE) and state.contains(
                pyatspi.STATE_ENABLED
            )
        except Exception:  # noqa: BLE001
            pass
        out.append({
            "depth": depth, "role": role, "name": name,
            "desc": desc, "x": x, "y": y, "w": w, "h": h,
            "enabled": enabled, "node": node,
        })
    except Exception:  # noqa: BLE001
        return out
    try:
        for child in node:
            walk(child, depth + 1, out, max_depth)
    except Exception:  # noqa: BLE001
        pass
    return out


def click(item: dict) -> None:
    x, y, w, h = item["x"], item["y"], item["w"], item["h"]
    if w <= 0 or h <= 0:
        try:
            comp = item["node"].queryAction()
            comp.doAction(0)
            return
        except Exception:  # noqa: BLE001
            pass
    xdo("mousemove", str(x + w // 2), str(y + h // 2), "click", "1")


def type_into(item: dict, text: str) -> None:
    # Prefer AT-SPI editable text (sets the value directly). Fall back to
    # focus + xdotool typing, which Qt also accepts.
    try:
        editable = item["node"].queryEditableText()
        editable.setTextContents(text)
        log(f"  set via AT-SPI: {item['name']!r}")
        return
    except Exception:  # noqa: BLE001
        pass
    click(item)
    xdo("key", "--clearmodifiers", "ctrl+a")
    xdo("type", "--clearmodifiers", "--delay", "20", text)
    log(f"  typed via xdotool: {item['name']!r}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--encrypt", action="store_true")
    ap.add_argument("--timeout", type=int, default=1800)
    ap.add_argument("--user", default="sanora")
    ap.add_argument("--password", default="Sanora-Dev-2026!")
    ap.add_argument("--luks-passphrase", default="Sanora-Luks-2026!")
    args = ap.parse_args()

    open(LOG_PATH, "w", encoding="utf-8").close()
    values = {
        "user": f"{args.user} User",
        "host": f"{args.user}-pc",
        "password": args.password,
        "luks": args.luks_passphrase,
    }

    try:
        import pyatspi  # noqa: F401
    except ImportError as exc:
        finish("FAILED", f"pyatspi unavailable: {exc}", [])

    deadline = time.time() + args.timeout
    steps: list[str] = []
    last_signature = ""
    encrypted_clicked = False

    while time.time() < deadline:
        app = app_node()
        if app is None:
            time.sleep(2)
            continue
        items = walk(app)
        signature = "|".join(f"{i['role']}:{i['name']}" for i in items[:80])
        if signature != last_signature:
            log("--- widget tree ---")
            for i in items:
                if i["name"] or i["role"] in ("push button", "check box", "password text", "entry"):
                    log(
                        f"  {i['depth']:02d} {i['role']:<18} "
                        f"{i['name'][:60]!r} at ({i['x']},{i['y']},{i['w']},{i['h']}) "
                        f"enabled={i['enabled']}"
                    )
            last_signature = signature

        # Finished page?
        joined = " ".join((i["name"] + " " + i["desc"]).lower() for i in items)
        if "installation complete" in joined or "all done" in joined or "finished" in joined:
            steps.append("reached finished page")
            finish("SUCCESS", "Calamares reported installation complete", steps)

        # Encryption checkbox and passphrase (partition page).
        if args.encrypt and not encrypted_clicked:
            for i in items:
                if i["role"] == "check box" and "encrypt" in i["name"].lower():
                    try:
                        state = i["node"].getState()
                        checked = state.contains(pyatspi.STATE_CHECKED)
                    except Exception:  # noqa: BLE001
                        checked = False
                    if not checked:
                        click(i)
                        log("clicked 'Encrypt system' checkbox")
                        steps.append("enabled encryption")
                        time.sleep(1)
                    encrypted_clicked = True
                    break

        # Fill every recognisable empty text field.
        for i in items:
            if i["role"] not in ("entry", "password text", "text"):
                continue
            key = None
            for pattern, kind in FIELD_VALUES.items():
                if pattern.lower() in i["name"].lower():
                    key = kind
                    break
            if key is None:
                continue
            try:
                text_iface = i["node"].queryText()
                existing = text_iface.getText(0, text_iface.characterCount)
            except Exception:  # noqa: BLE001
                existing = None
            if existing:
                continue
            type_into(i, values[key])
            steps.append(f"filled {i['name']!r}")
            time.sleep(0.3)

        time.sleep(1.0)

        # Advance with the enabled Next / Install button.
        for i in items:
            if i["role"] != "push button" or not i["enabled"]:
                continue
            label = i["name"].replace("&", "").strip().lower()
            if any(label.startswith(n) or n in label for n in NEXT_NAMES):
                click(i)
                steps.append(f"clicked {i['name']!r}")
                log(f"clicked {i['name']!r}")
                time.sleep(3)
                break
        else:
            time.sleep(2)

    finish("TIMEOUT", f"no finished page within {args.timeout}s", steps)


if __name__ == "__main__":
    raise SystemExit(main())
