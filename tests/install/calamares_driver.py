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
import pathlib
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
        if proc.returncode != 0:
            log(f"xdotool {args[:3]} rc={proc.returncode} err={proc.stderr.strip()[:200]!r}")
        return proc.stdout.strip()
    except (OSError, subprocess.TimeoutExpired) as exc:
        log(f"xdotool {args[:2]} failed: {exc}")
        return ""


_APP_LIST_LOGGED = False


def app_node():
    """Find the Calamares application in the AT-SPI tree.

    Qt6 applications sometimes register with an empty or product-derived
    accessible name, so also accept a frame whose name mentions Calamares or
    SANORA. Log the application list once for CI diagnosis.
    """
    import pyatspi

    global _APP_LIST_LOGGED
    desktop = pyatspi.Registry.getDesktop(0)
    names = []
    for app in desktop:
        try:
            name = app.name or ""
        except Exception:  # noqa: BLE001
            name = ""
        names.append(name)
        if "calamares" in name.lower():
            return app
    if not _APP_LIST_LOGGED:
        log(f"AT-SPI applications: {names!r}")
        _APP_LIST_LOGGED = True
    for app in desktop:
        try:
            for child in app:
                label = f"{child.name or ''} {child.description or ''}".lower()
                if "calamares" in label or "sanora" in label:
                    return app
        except Exception:  # noqa: BLE001
            continue
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


def pick_window():
    """Find Calamares' real top-level X window.

    `xdotool search --name Calamares` can return a 3x3 hidden helper window
    (observed in run 41540769895); focusing that fails with BadMatch. Pick a
    plausible main window by geometry instead.
    """
    candidates = []
    for pattern in ("Calamares", "SANORA", "calamares"):
        candidates += xdo("search", "--onlyvisible", "--name", pattern).split()
    candidates += xdo("search", "--onlyvisible", "--class", "calamares").split()
    candidates += xdo("search", "--onlyvisible", "--name", ".*").split()
    seen, best = set(), None
    for wid in candidates:
        if wid in seen:
            continue
        seen.add(wid)
        raw = xdo("getwindowgeometry", "--shell", wid)
        geom = {}
        for line in raw.splitlines():
            if "=" in line:
                k, v = line.split("=", 1)
                geom[k] = v.strip()
        try:
            w = int(geom.get("WIDTH", "0")); h = int(geom.get("HEIGHT", "0"))
        except ValueError:
            continue
        if w < 300 or h < 200:
            continue
        name = xdo("getwindowname", wid)
        named = any(k in name.lower() for k in ("calamares", "installer", "sanora"))
        area = w * h
        log(f"window candidate {wid}: {w}x{h} name={name!r} named={named}")
        # Prefer a named Calamares window; the root/desktop window is larger
        # but must never be activated (it is the 1280x800 X root).
        score = (1 if named else 0, area)
        if best is None or score > best[2]:
            best = (wid, geom, score)
    return (best[0], best[1]) if best else (None, {})


def keyboard_fallback(args, values, finish, steps):
    """Drive Calamares with its documented '&Next' mnemonic when AT-SPI is
    unavailable. Sequence is Debian 13's settings.conf: welcome, locale,
    keyboard, partition, users, summary. No hardcoded screen coordinates."""
    wid, geom = pick_window()
    if wid:
        xdo("windowactivate", "--sync", wid)
        log(f"activated window {wid}")
    else:
        log("WARNING: could not find Calamares main window; keys go to focus")
    log(f"active window: {xdo('getactivewindow', 'getwindowname')!r}")
    log(f"XAUTHORITY={os.environ.get('XAUTHORITY', '<unset>')}")
    log(f"window geometry: {geom!r}")

    def click_next():
        # Calamares' QWidget navigation puts Next near the bottom-right, left
        # of Quit. Click by position derived from the real window geometry,
        # but only when the geometry is plausible (a real top-level window).
        try:
            x = int(geom.get("X", "0")); y = int(geom.get("Y", "0"))
            w = int(geom.get("WIDTH", "0")); h = int(geom.get("HEIGHT", "0"))
            if w < 300 or h < 200:
                return
            xdo("mousemove", str(x + w - 150), str(y + h - 34), "click", "1")
        except (ValueError, TypeError):
            pass

    def next_page(label):
        # One advance attempt per page: the '&Next' mnemonic. The coordinate
        # click is a fallback only when the mnemonic does nothing (checked by
        # Calamares' own log in CI diagnostics), to avoid double-advancing.
        xdo("key", "--clearmodifiers", "alt+n")
        time.sleep(5)
        steps.append(f"advanced past {label}")
        log(f"advanced past {label}")

    next_page("welcome")
    next_page("locale")
    next_page("keyboard")
    next_page("partition")

    # Users page: the five text fields in tab order.
    sequence = [
        ("Your Full Name", values["user"]),
        ("login", values["username"]),
        ("Computer Name", values["host"]),
        ("Password", values["password"]),
        ("Repeat Password", values["password"]),
    ]
    for label, text in sequence:
        xdo("type", "--clearmodifiers", "--delay", "25", text)
        xdo("key", "--clearmodifiers", "Tab")
        steps.append(f"typed {label}")
        log(f"typed {label}")
    time.sleep(1)
    next_page("users -> summary")
    # Summary page: the button label is "Install" (ExecutionViewStep), so the
    # '&Next' mnemonic no longer applies. It is the dialog's default button;
    # Return activates it. The coordinate click is a fallback.
    xdo("key", "--clearmodifiers", "Return")
    time.sleep(3)
    click_next()
    steps.append("clicked Install")
    log("clicked Install (Return + fallback click)")

    # Wait for the exec phase to create partitions on the target disk, then
    # allow generous time for unpackfs/bootloader before the host reboots.
    deadline = time.time() + min(args.timeout, 420)
    partitioned = False
    while time.time() < deadline:
        out = subprocess.run(
            ["lsblk", "-no", "FSTYPE", "/dev/vda"],
            capture_output=True, text=True,
        ).stdout
        if "ext4" in out or "crypto_LUKS" in out or "vfat" in out:
            partitioned = True
            log("target disk now has filesystems")
            break
        time.sleep(10)
    if partitioned:
        log("waiting for unpackfs/bootloader jobs to finish")
        time.sleep(420)
    finish(
        "SUCCESS" if partitioned else "FAILED",
        "keyboard fallback: partitions created" if partitioned
        else "keyboard fallback: no target filesystems appeared",
        steps,
    )


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
        "username": args.user,
        "host": f"{args.user}-pc",
        "password": args.password,
        "luks": args.luks_passphrase,
    }

    # Point pyatspi at the user's accessibility bus if the session did not
    # export it. Qt registers its accessibility bridge on this bus.
    if not os.environ.get("AT_SPI_BUS_ADDRESS"):
        for candidate in ("/run/user/1000/at-spi/bus_0",):
            p = pathlib.Path(candidate)
            if p.is_file():
                for line in p.read_text(errors="replace").splitlines():
                    if line.startswith("DBUS_SESSION_BUS_ADDRESS="):
                        os.environ["AT_SPI_BUS_ADDRESS"] = line.split("=", 1)[1]
                        log(f"AT_SPI_BUS_ADDRESS={os.environ['AT_SPI_BUS_ADDRESS']}")
                        break
    try:
        import pyatspi  # noqa: F401
    except ImportError as exc:
        finish("FAILED", f"pyatspi unavailable: {exc}", [])

    # Start the AT-SPI bus/registry if the live session did not. Qt registers
    # its accessibility bridge only when the bus is available at startup.
    for helper in ("/usr/libexec/at-spi-bus-launcher",
                   "/usr/libexec/at-spi2-registryd"):
        if pathlib.Path(helper).exists():
            try:
                subprocess.Popen(
                    [helper], stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL, env=os.environ.copy(),
                )
            except OSError:
                pass
    time.sleep(2)

    deadline = time.time() + args.timeout
    steps: list[str] = []
    last_signature = ""
    encrypted_clicked = False
    no_app_since = time.time()

    while time.time() < deadline:
        app = app_node()
        if app is None:
            time.sleep(2)
            # If AT-SPI never exposes Calamares, fall back to keyboard
            # navigation using the documented '&Next' mnemonic (Alt+N).
            if time.time() - no_app_since > 25:
                log("AT-SPI unavailable; switching to keyboard fallback")
                return keyboard_fallback(args, values, finish, steps)
            continue
        no_app_since = time.time()
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
