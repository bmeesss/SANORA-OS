#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""Perform a real Calamares installation in a disposable QEMU VM and reboot.

Phase 1: boot the SANORA ISO in UEFI mode with an empty qcow2 disk, start
         Calamares, drive its GUI with tests/install/calamares_driver.py.
Phase 2: shut down, then boot the SAME disk without the ISO and validate the
         installed system over the serial console.

Everything observed is written to <out>/install-validation.json. A running
Calamares process is NOT treated as success; only a completed installation
plus a boot into the installed system is.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import pathlib
import re
import shlex
import shutil
import signal
import socket
import struct
import subprocess
import sys
import time
import zlib

try:
    import pexpect
except ImportError:
    pexpect = None


# ---------------------------------------------------------------------------
# helpers shared with the boot harness
# ---------------------------------------------------------------------------
def ppm_to_png(src: pathlib.Path, dst: pathlib.Path, scale: int = 2):
    raw = src.read_bytes()
    fields, i = [], 0
    while len(fields) < 4 and i < len(raw):
        while i < len(raw) and raw[i : i + 1].isspace():
            i += 1
        if raw[i : i + 1] == b"#":
            while i < len(raw) and raw[i : i + 1] not in (b"\n", b"\r"):
                i += 1
            continue
        j = i
        while j < len(raw) and not raw[j : j + 1].isspace():
            j += 1
        fields.append(raw[i:j])
        i = j
    if len(fields) < 4 or fields[0] != b"P6":
        return None
    w, h = int(fields[1]), int(fields[2])
    i += 1
    pixels = raw[i : i + w * h * 3]
    if len(pixels) < w * h * 3:
        return None
    # Nearest-neighbour downscale keeps the file small enough for a check run.
    nw, nh = w // scale, h // scale
    rows = bytearray()
    for y in range(nh):
        rows.append(0)
        src_row = (y * scale) * w * 3
        for x in range(nw):
            off = src_row + x * scale * 3
            rows.extend(pixels[off : off + 3])

    def chunk(kind, data):
        return (
            struct.pack(">I", len(data)) + kind + data
            + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        )

    png = (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", nw, nh, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(bytes(rows), 9))
        + chunk(b"IEND", b"")
    )
    dst.write_bytes(png)
    return nw, nh


class HMP:
    def __init__(self, path):
        self.sock = None
        for _ in range(50):
            try:
                s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                s.settimeout(2)
                s.connect(path)
                self.sock = s
                break
            except OSError:
                time.sleep(0.2)
        if self.sock:
            try:
                self.sock.settimeout(0.3)
                self.sock.recv(4096)
            except OSError:
                pass

    def cmd(self, command):
        if not self.sock:
            return ""
        try:
            self.sock.settimeout(4)
            self.sock.sendall((command + "\n").encode())
            time.sleep(0.4)
            return self.sock.recv(65536).decode("utf-8", "replace")
        except OSError:
            return ""

    def close(self):
        if self.sock:
            try:
                self.sock.close()
            except OSError:
                pass


def guest_cmd(child, command, tag, timeout=180):
    b, e = f"SANORA_{tag}_BEGIN", f"SANORA_{tag}_END"
    child.sendline(f"echo SANORA\"\"_{tag}_BEGIN; {command}; echo SANORA\"\"_{tag}_END")
    child.expect_exact(b, timeout=60)
    child.expect_exact(e, timeout=timeout)
    return child.before or ""


# Named sections: (key, shell command). Evidence is built from the same order,
# so adding a check cannot silently shift positional indices (that broke an
# earlier iteration). No command may contain the literal "SEP".
SUDO = "printf '%s\n' 'Sanora-Dev-2026!' | sudo -S "
VALIDATE_SECTIONS = [
    ("os_release", "cat /etc/os-release"),
    ("sanora_info", "sanora-info"),
    ("user_host", "whoami; hostname"),
    ("locale", "grep -E '^(LANG|LANGUAGE)=' /etc/default/locale"),
    ("lsblk", "lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINTS"),
    ("root_mount", "findmnt -no SOURCE,FSTYPE,TARGET /"),
    ("efi_boot_files", "ls -R /boot/efi/EFI 2>/dev/null | head -30"),
    ("luks_dump", SUDO + "cryptsetup luksDump /dev/vda3 2>&1 | head -40"),
    ("crypttab", SUDO + "cat /etc/crypttab 2>&1"),
    ("dmsetup", SUDO + "dmsetup ls --target crypt 2>&1"),
    ("initramfs_crypto", SUDO +
     "sh -c 'lsinitramfs /boot/initrd.img-$(uname -r) 2>/dev/null "
     "| grep -iE \"cryptsetup|cryptroot|crypttab|dm-crypt|askpass|keyfile\" "
     "| head -40'"),
    ("efibootmgr", SUDO + "efibootmgr -v 2>&1 | head -20"),
    ("look_and_feel", "kreadconfig6 --file kdeglobals --group KDE --key LookAndFeelPackage"),
    ("icon_theme", "kreadconfig6 --file kdeglobals --group Icons --key Theme"),
    ("theme_present",
     "test -f /usr/share/plasma/look-and-feel/org.sanora.light.desktop/metadata.json "
     "&& echo SANORA_THEME_PRESENT || echo SANORA_THEME_MISSING"),
    ("wallpaper",
     "grep -R 'sanora-default' ~/.config/plasma-org.kde.plasma.desktop-appletsrc 2>/dev/null "
     "| head -5; test -f /usr/share/sanora/wallpapers/sanora-default.png "
     "&& echo WALLPAPER_PRESENT || echo WALLPAPER_MISSING"),
    ("desktop_widgets",
     "grep -E 'org.kde.plasma.taskmanager|org.kde.plasma.kickoff|org.kde.panel' "
     "~/.config/plasma-org.kde.plasma.desktop-appletsrc 2>/dev/null | head -20"),
    ("sessions", "loginctl list-sessions --no-legend"),
    ("session_types",
     "for s in $(loginctl list-sessions --no-legend | awk '{print $1}'); do "
     "loginctl show-session -p Type --value $s; done"),
    ("kwin_wayland_processes", "pgrep -af 'kwin_wayland|startplasma-wayland|plasmashell'"),
    ("graphical_env",
     "for p in $(pgrep -u $(id -u) -x plasmashell | head -2); do "
     "tr '\000' '\n' < /proc/$p/environ | "
     "grep -E '^(XDG_SESSION_TYPE|WAYLAND_DISPLAY|XDG_CURRENT_DESKTOP|DISPLAY|"
     "XDG_SESSION_DESKTOP)=' || true; done"),
    ("desktop_apps",
     "for b in dolphin konsole plasma-discover flatpak fwupdmgr; do "
     "command -v $b || echo MISSING:$b; done"),
    ("services",
     "echo NETWORKMANAGER=$(systemctl is-active NetworkManager); "
     "echo PIPEWIRE=$(systemctl --user is-active pipewire); "
     "echo PIPEWIRE_PULSE=$(systemctl --user is-active pipewire-pulse); "
     "echo WIREPLUMBER=$(systemctl --user is-active wireplumber); "
     "echo NM_RUNNING=$(nmcli -t -f RUNNING general 2>&1)"),
    ("sddm",
     "echo SDDM_ACTIVE=$(systemctl is-active sddm); "
     "loginctl list-sessions --no-legend | grep -i sddm || true"),
    ("systemd_analyze", "systemd-analyze"),
    ("free", "free -m"),
    ("process_count", "ps -e --no-headers | wc -l"),
    ("branding", "cat /etc/calamares/branding/sanora/branding.desc | head -5"),
    ("uname", "uname -a"),
]

VALIDATE = "sleep 15; " + "; echo SEP; ".join(cmd for _, cmd in VALIDATE_SECTIONS)


# QEMU HMP `sendkey` key names. One key per call avoids modifier-accumulation
# ambiguity (uppercase letters use "shift-<letter>"). The keystrokes are
# injected into the emulated keyboard, so they reach the X11 SDDM greeter
# regardless of which XAUTHORITY file the greeter uses.
QEMU_KEYS = {
    " ": "spc", "-": "minus", "_": "shift-minus", "!": "shift-1",
    ".": "dot", ",": "comma", "/": "slash", ":": "shift-semicolon",
    "@": "shift-2", "#": "shift-3", "$": "shift-4", "%": "shift-5",
    "^": "shift-6", "&": "shift-7", "*": "shift-8", "(": "shift-9",
    ")": "shift-0", "=": "equal", "+": "shift-equal", "?": "shift-slash",
}


def hmp_send_text(hmp, text, press_return=True):
    """Type a string into the guest via the QEMU human monitor."""
    for ch in text:
        key = "shift-" + ch.lower() if ch.isupper() else QEMU_KEYS.get(ch, ch)
        hmp.cmd(f"sendkey {key}")
    if press_return:
        hmp.cmd("sendkey ret")


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--iso", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--mode", choices=["plain", "luks"], default="plain")
    ap.add_argument("--timeout", type=int, default=2400)
    ap.add_argument("--user", default="sanora")
    ap.add_argument("--password", default="Sanora-Dev-2026!")
    ap.add_argument("--luks-passphrase", default="Sanora-Luks-2026!")
    ap.add_argument("--driver", default=None,
                    help="upload this driver into the guest (fast iteration without a new ISO)")
    ap.add_argument("--baseline", default=None,
                    help="optional stock Debian KDE ISO to measure for comparison")
    args = ap.parse_args()

    out = pathlib.Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    result = {
        "schema": "sanora.install-validation/1",
        "mode": args.mode,
        "iso": args.iso,
        "status": "SKIPPED",
        "phases": {},
        "errors": [],
        "evidence": {},
    }

    def finish(code):
        (out / "install-validation.json").write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        print(json.dumps(result, indent=2, sort_keys=True))
        return code

    iso = pathlib.Path(args.iso)
    if not iso.is_file():
        result["errors"].append("ISO missing; installation SKIPPED (not passed)")
        return finish(0)
    if pexpect is None:
        result["errors"].append("python3-pexpect missing; SKIPPED")
        return finish(0)

    digest = hashlib.sha256()
    for block in _stream(iso):
        digest.update(block)
    result["iso_sha256"] = digest.hexdigest()

    work = out / "vm"
    work.mkdir(parents=True, exist_ok=True)
    disk = work / "sanora-disk.qcow2"
    vars_fd = work / "OVMF_VARS.fd"
    shutil.copyfile("/usr/share/OVMF/OVMF_VARS_4M.fd", vars_fd)
    subprocess.run(
        ["qemu-img", "create", "-f", "qcow2", str(disk), "24G"],
        check=True, capture_output=True, text=True,
    )

    kvm = os.path.exists("/dev/kvm") and os.access("/dev/kvm", os.W_OK)
    # qemu_boot.py (verified working) uses the combined OVMF image with
    # `-bios`. A split CODE/VARS pflash pair did not produce a serial console
    # in the first install run, so use the same proven firmware path here and
    # keep the VARS file only as a fallback for the installed-system reboot.
    combined_fd = "/usr/share/qemu/OVMF.fd"
    code_fd = "/usr/share/OVMF/OVMF_CODE_4M.fd"

    mon = f"/tmp/sanora-install-{args.mode}.sock"
    for p in (mon,):
        try:
            os.unlink(p)
        except OSError:
            pass

    def qemu_args(with_iso: bool):
        a = [
            "qemu-system-x86_64", "-no-reboot", "-m", "4096", "-smp", "2",
            "-machine", "q35",
            # Split CODE/VARS pflash with a PERSISTENT vars file: GRUB's
            # efibootmgr entry must survive the reboot from ISO to disk, which
            # a combined read-only `-bios` image cannot do. The earlier pflash
            # failure was the missing boot-menu Enter, now handled by run_phase.
            "-drive", f"if=pflash,format=raw,readonly=on,file={code_fd}",
            "-drive", f"if=pflash,format=raw,file={vars_fd}",
            "-drive", f"file={disk},if=virtio,format=qcow2",
            "-vga", "std", "-display", "none",
            "-serial", "stdio",
            "-monitor", f"unix:{mon},server=on,wait=off",
            "-netdev", "user,id=n0", "-device", "e1000,netdev=n0",
            "-rtc", "base=utc", "-pidfile", str(work / "qemu.pid"),
        ]
        if with_iso:
            a += ["-cdrom", str(iso.resolve()), "-boot", "d"]
        else:
            a += ["-boot", "c"]
        a += ["-enable-kvm", "-cpu", "host"] if kvm else ["-cpu", "max"]
        return a

    result["vm"] = {
        "ram_mb": 4096, "vcpus": 2, "disk": "24G qcow2 virtio",
        "firmware": code_fd, "accel": "kvm" if kvm else "tcg",
        "network": "qemu user-mode e1000", "uefi_vars_persisted": True,
    }
    screenshots_b64 = []

    def capture(hmp, label):
        ppm = work / f"{label}.ppm"
        hmp.cmd(f"screendump {ppm}")
        if not ppm.is_file():
            return
        png = out / f"{label}.png"
        dims = ppm_to_png(ppm, png, scale=3)
        if dims:
            data = base64.b64encode(png.read_bytes()).decode()
            screenshots_b64.append({"label": label, "dimensions": dims, "base64_len": len(data)})
            (out / f"{label}.png.b64").write_text(data, encoding="utf-8")

    def run_phase(cmd, phase_name, timeout_seconds):
        """Spawn QEMU, get a serial shell, run `fn(child, hmp)`."""
        # A previous QEMU may have left the monitor socket behind; remove it so
        # the new process can bind. Needed for the extra LUKS2 wrong-passphrase
        # boot attempt, which starts QEMU a third time.
        try:
            os.unlink(mon)
        except OSError:
            pass
        logfile = out / f"{phase_name}-serial.log"
        errlog = out / f"{phase_name}-qemu-stderr.log"
        shell_cmd = " ".join(shlex.quote(x) for x in cmd) + " 2>" + shlex.quote(str(errlog))
        handle = logfile.open("w", encoding="utf-8", errors="replace")
        child = None
        hmp = None
        try:
            child = pexpect.spawn(
                "/bin/bash", ["-c", shell_cmd], timeout=60,
                encoding="utf-8", codec_errors="replace", dimensions=(24, 140),
            )
            child.logfile_read = handle
            hmp = HMP(mon)
            # live-build's isolinux/GRUB menu uses `timeout 0` and waits for a
            # keypress (Debian Live Manual §11.1). qemu_boot.py sends Enter via
            # the QEMU human monitor; the install harness must do the same or
            # the VM never reaches the kernel and no serial console appears.
            time.sleep(8)
            hmp.cmd("sendkey ret")
            return child, hmp, handle
        except Exception as exc:  # noqa: BLE001
            result["errors"].append(f"{phase_name} spawn failed: {exc}")
            if child:
                try:
                    child.close(force=True)
                except Exception:
                    pass
            handle.close()
            return None, None, None

    def kill(child, hmp, handle):
        if hmp:
            hmp.close()
        if child:
            try:
                child.close(force=True)
            except Exception:
                pass
        pidfile = work / "qemu.pid"
        if pidfile.is_file():
            try:
                os.kill(int(pidfile.read_text().strip()), signal.SIGTERM)
            except (ValueError, OSError):
                pass
        handle.close()
        time.sleep(2)

    # ---------------- Phase 1: install ----------------
    print("=== PHASE 1: Calamares installation ===", flush=True)
    child, hmp, handle = run_phase(qemu_args(True), "install", args.timeout)
    if child is None:
        return finish(1)

    install_ok = False
    try:
        # A serial login prompt must appear quickly. Do NOT wait the whole
        # installation timeout here (that masked the first run's boot failure).
        deadline = time.time() + 240
        shell = False
        while time.time() < deadline:
            try:
                idx = child.expect(
                    [r"login:", r"Password:", r"\$ ", pexpect.TIMEOUT, pexpect.EOF],
                    timeout=min(60, max(5, deadline - time.time())),
                )
            except pexpect.TIMEOUT:
                idx = 3
            if idx == 0:
                child.sendline("user")
            elif idx == 1:
                child.sendline("live")
            elif idx == 2:
                shell = True
                break
            elif idx == 4:
                result["errors"].append("QEMU exited during install boot")
                break
        result["phases"]["install_serial_shell"] = shell
        if not shell:
            result["errors"].append("no serial shell in live VM")
            return finish(1)

        child.sendline("stty -echo")
        time.sleep(0.4)

        # Make sure the GUI automation dependencies exist (the development ISO
        # ships them; a downloaded older ISO may need them installed).
        guest_cmd(
            child,
            "command -v xdotool >/dev/null && python3 -c 'import pyatspi' 2>/dev/null || "
            "(sudo -n apt-get update -qq && sudo -n apt-get install -y -qq xdotool python3-pyatspi)",
            "TOOLS", timeout=300,
        )

        # Upload the current driver from the checkout so the automation can be
        # iterated without rebuilding the ISO. Chunked base64 over the serial
        # console avoids any dependency on guest networking or file transfer.
        driver_path = "/usr/share/sanora/tests/calamares_driver.py"
        if args.driver and pathlib.Path(args.driver).is_file():
            payload = base64.b64encode(pathlib.Path(args.driver).read_bytes()).decode()
            child.sendline("rm -f /tmp/sanora-driver.b64 /tmp/calamares_driver.py")
            for n in range(0, len(payload), 700):
                child.sendline(f"printf '%s' '{payload[n:n+700]}' >> /tmp/sanora-driver.b64")
            child.sendline("base64 -d /tmp/sanora-driver.b64 > /tmp/calamares_driver.py && "
                           "chmod 755 /tmp/calamares_driver.py")
            driver_path = "/tmp/calamares_driver.py"
            result["evidence"]["driver_uploaded_from_checkout"] = True

        # Start the AT-SPI bus BEFORE Calamares: Qt6 only registers its
        # accessibility bridge when the bus exists at application startup.
        guest_cmd(
            child,
            "pgrep -f at-spi-bus-launcher >/dev/null 2>&1 || "
            "(/usr/libexec/at-spi-bus-launcher >/dev/null 2>&1 &); "
            "pgrep -f at-spi2-registryd >/dev/null 2>&1 || "
            "(/usr/libexec/at-spi2-registryd >/dev/null 2>&1 &); sleep 2",
            "ATSPI", timeout=30,
        )

        # Qt's AT-SPI bridge registers on the ACCESSIBILITY bus, not the
        # session bus. Calamares must be given its address at startup, or it
        # never appears in pyatspi's desktop tree (verified in runs
        # 41533764392 and 41609868964). Read the address written by
        # at-spi-bus-launcher and pass it to both Calamares and the driver.
        a11y = guest_cmd(
            child,
            "grep -m1 '^DBUS_SESSION_BUS_ADDRESS=' /run/user/1000/at-spi/bus_0 "
            "2>/dev/null | cut -d= -f2-; "
            "ls -l /run/user/1000/at-spi/ 2>/dev/null | head -5",
            "A11Y", timeout=30,
        ).strip().splitlines()
        a11y_addr = a11y[0].strip() if a11y else ""
        result["evidence"]["at_spi_bus_address_present"] = bool(a11y_addr)
        a11y_env = f"AT_SPI_BUS_ADDRESS={shlex.quote(a11y_addr)} " if a11y_addr else ""

        # Discover the SDDM Xauthority and start Calamares with accessibility on.
        xauth = guest_cmd(
            child,
            "ls /run/user/1000/xauth_* 2>/dev/null | head -1",
            "XAUTH", timeout=30,
        ).strip().splitlines()
        xauth = xauth[-1].strip() if xauth else ""
        result["evidence"]["xauthority"] = xauth
        capture(hmp, "install-00-live-desktop")

        launch = (
            f"sudo -n -b env DISPLAY=:0 XAUTHORITY={shlex.quote(xauth)} "
            "QT_QPA_PLATFORM=xcb QT_ACCESSIBILITY=1 "
            "QT_LINUX_ACCESSIBILITY_ALWAYS_ON=1 "
            "DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus "
            "XDG_RUNTIME_DIR=/run/user/1000 " + a11y_env +
            "calamares -D6 > /tmp/sanora-calamares.log 2>&1; "
            "sleep 8; pgrep -a calamares || echo CALAMARES_NOT_RUNNING"
        )
        launch_out = guest_cmd(child, launch, "LAUNCH", timeout=90)
        result["phases"]["calamares_launched"] = "CALAMARES_NOT_RUNNING" not in launch_out
        result["evidence"]["calamares_launch"] = launch_out[-1500:]
        capture(hmp, "install-01-calamares-welcome")
        if not result["phases"]["calamares_launched"]:
            result["errors"].append("Calamares did not start")
            return finish(1)

        encrypt_flag = "--encrypt" if args.mode == "luks" else ""
        driver = (
            "sudo -n -u user env "
            f"DISPLAY=:0 XAUTHORITY={shlex.quote(xauth)} "
            "HOME=/home/user "
            "DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus "
            "XDG_RUNTIME_DIR=/run/user/1000 " + a11y_env +
            f"python3 {driver_path} {encrypt_flag} "
            f"--timeout {args.timeout} --user {shlex.quote(args.user)} "
            f"--password {shlex.quote(args.password)} "
            f"--luks-passphrase {shlex.quote(args.luks_passphrase)} "
            "; echo DRIVER_RC=$?"
        )
        child.sendline(driver)
        # Wait for the driver's final RESULT line (it also writes a JSON file).
        driver_deadline = time.time() + args.timeout
        driver_result = ""
        while time.time() < driver_deadline:
            try:
                idx = child.expect(
                    [r"RESULT: SUCCESS", r"RESULT: (FAILED|TIMEOUT)",
                     r"SANORA_PAGE_PARTITION", pexpect.TIMEOUT, pexpect.EOF],
                    timeout=30,
                )
            except pexpect.TIMEOUT:
                idx = 3
            if idx in (0, 1):
                driver_result = "SUCCESS" if idx == 0 else "FAILED"
                capture(hmp, "install-02-finished")
                break
            if idx == 2:
                # The driver is on the partition page: capture the encryption
                # widget / partition layout as visual evidence.
                capture(hmp, "install-partition-page")
                result["phases"]["partition_page_reached"] = True
                continue
            if idx == 4:
                break
            progress_shots = result["phases"].setdefault("progress_screenshots", 0)
            if progress_shots < 3:
                capture(hmp, f"install-progress-{progress_shots}")
                result["phases"]["progress_screenshots"] = progress_shots + 1
        result["phases"]["driver_verdict"] = driver_result or "NO_VERDICT"
        try:
            drv = guest_cmd(
                child, "cat /tmp/sanora-calamares-driver.json 2>/dev/null; "
                       "echo '--- driver log tail ---'; "
                       "tail -80 /tmp/sanora-calamares-driver.log 2>/dev/null; "
                       "echo '--- calamares log tail ---'; "
                       "tail -60 /tmp/sanora-calamares.log 2>/dev/null",
                "DRIVERLOG", timeout=90,
            )
            (out / "install-driver-log.txt").write_text(drv, encoding="utf-8")
            result["evidence"]["driver_log"] = str(out / "install-driver-log.txt")
        except (pexpect.TIMEOUT, pexpect.EOF) as exc:
            result["errors"].append(f"could not read driver log: {exc}")

        install_ok = driver_result == "SUCCESS"
        result["phases"]["installation_completed"] = install_ok
        if not install_ok:
            result["errors"].append("Calamares did not report installation complete")
            return finish(1)

        # The installed system's GRUB config does not carry the live ISO's
        # `console=ttyS0` boot parameter. Add it to the installed grub.cfg so
        # the post-reboot validation can use the serial console. This is a
        # TEST-HARNESS adaptation for observability only: no partition,
        # filesystem or package data is altered.
        try:
            prep = guest_cmd(
                child,
                "sudo -n sh -c '"
                "mkdir -p /mnt/sanora-target; "
                "for p in /dev/vda2 /dev/vda1 /dev/vda3; do "
                "  mount -o rw \"$p\" /mnt/sanora-target 2>/dev/null || continue; "
                "  if [ -f /mnt/sanora-target/grub/grub.cfg ]; then "
                "    sed -i \"s/quiet/quiet console=ttyS0,115200/\" "
                "      /mnt/sanora-target/grub/grub.cfg; "
                "    echo GRUB_SERIAL_ADDED; "
                "  fi; "
                "  umount /mnt/sanora-target; "
                "done'; echo SANORA_GRUB_PREP_DONE",
                "GRUBPREP", timeout=120,
            )
            result["phases"]["installed_grub_serial_added"] = (
                "GRUB_SERIAL_ADDED" in prep
            )
        except (pexpect.TIMEOUT, pexpect.EOF) as exc:
            result["errors"].append(f"GRUB serial prep failed: {exc}")

        # Power off cleanly before booting the disk.
        try:
            child.sendline("sudo -n poweroff")
            time.sleep(8)
        except Exception:  # noqa: BLE001
            pass
    finally:
        kill(child, hmp, handle)

    # ---------------- Phase 2: boot installed system ----------------
    print("=== PHASE 2: boot installed system from disk ===", flush=True)
    time.sleep(3)

    def boot_installed(label, passphrase, timeout=420, max_prompt_replies=3):
        """Boot the disk only. If `passphrase` is set, answer the initramfs
        LUKS unlock prompt that many times. Returns the live pexpect child,
        HMP handle, log handle, login state and prompt count.
        """
        child, hmp, handle = run_phase(qemu_args(False), label, timeout)
        if child is None:
            return None
        deadline = time.time() + timeout
        logged_in = False
        prompt_seen = 0
        prompt_replies = 0
        while time.time() < deadline:
            try:
                idx = child.expect(
                    [r"(?i)(please unlock|enter passphrase|unlocking the disk|"
                     r"cryptsetup|passphrase for|unlock disk)",
                     r"login:", r"Password:", r"\$ ",
                     pexpect.TIMEOUT, pexpect.EOF],
                    timeout=min(45, max(5, deadline - time.time())),
                )
            except pexpect.TIMEOUT:
                idx = 4
            if idx == 0:
                prompt_seen += 1
                if passphrase and prompt_replies < max_prompt_replies:
                    child.sendline(passphrase)
                    prompt_replies += 1
                continue
            if idx == 1:
                child.sendline(args.user)
            elif idx == 2:
                child.sendline(args.password)
            elif idx == 3:
                logged_in = True
                break
            elif idx == 5:
                break
        return {
            "child": child, "hmp": hmp, "handle": handle,
            "logged_in": logged_in, "prompt_seen": prompt_seen,
            "label": label,
        }

    # --- Priority 1: proof that a WRONG LUKS passphrase is rejected ---
    wrong_attempt = None
    if args.mode == "luks":
        print("=== PHASE 2a: wrong passphrase must be rejected ===", flush=True)
        wrong = args.luks_passphrase + "-WRONG"
        wrong_attempt = boot_installed(
            "installed-wrong-passphrase", wrong, timeout=200,
            max_prompt_replies=1,
        )
        if wrong_attempt is None:
            result["errors"].append("wrong-passphrase boot could not start")
        else:
            kill(wrong_attempt["child"], wrong_attempt["hmp"],
                 wrong_attempt["handle"])
            wlog = (out / "installed-wrong-passphrase-serial.log").read_text(
                errors="replace")
            (out / "wrong-passphrase-serial.txt").write_text(wlog, encoding="utf-8")
            rejection = bool(re.search(
                r"(?i)(no key available|maximum number of tries|failed to unlock|"
                r"cryptsetup.*failed|incorrect passphrase|bad passphrase|"
                r"not a valid luks|no usable keyslot", wlog))
            # Two or more unlock prompts after a single wrong reply is also
            # proof that the first passphrase was refused.
            retried = wrong_attempt["prompt_seen"] >= 2
            rejected = (rejection or retried) and not wrong_attempt["logged_in"]
            result["installed"]["wrong_passphrase"] = {
                "status": "PASS" if rejected else "FAIL",
                "wrong_passphrase_used": wrong,
                "unlock_prompts_seen": wrong_attempt["prompt_seen"],
                "rejection_text_found": rejection,
                "login_obtained_with_wrong_passphrase": wrong_attempt["logged_in"],
                "serial_log": "out/wrong-passphrase-serial.txt",
            }
            if not rejected:
                result["errors"].append(
                    "wrong LUKS passphrase was not proven to be rejected")
            time.sleep(3)

    # --- Priority 1/2: boot with the correct passphrase (or plain boot) ---
    correct_passphrase = args.luks_passphrase if args.mode == "luks" else None
    boot = boot_installed("installed", correct_passphrase, timeout=420)
    if boot is None:
        return finish(1)
    child2, hmp2, handle2 = boot["child"], boot["hmp"], boot["handle"]
    logged_in = boot["logged_in"]
    result["phases"]["installed_serial_login"] = logged_in
    result["phases"]["luks_unlock_prompts_seen"] = boot["prompt_seen"]
    capture(hmp2, "installed-00-desktop")
    if not logged_in:
        result["errors"].append("could not log into installed system")
        kill(child2, hmp2, handle2)
        return finish(1)

    try:
        child2.sendline("stty -echo")
        time.sleep(0.4)

        # --- Priority 2: an actual graphical user session, not just the greeter ---
        # First try a real interactive SDDM login by injecting keystrokes into the
        # emulated keyboard (no dependency on the greeter's XAUTHORITY path).
        sddm_state = guest_cmd(
            child2,
            "systemctl is-active sddm; loginctl list-sessions --no-legend | "
            "grep -i sddm || true; ls /usr/share/wayland-sessions/ 2>/dev/null | head -10",
            "SDDM", timeout=90,
        )
        result["installed"]["sddm_state"] = sddm_state
        hmp_send_text(hmp2, args.password)
        time.sleep(35)
        gcheck = guest_cmd(
            child2,
            "loginctl list-sessions --no-legend; "
            "for s in $(loginctl list-sessions --no-legend | awk '{print $1}'); do "
            "loginctl show-session -p Type --value $s; done; "
            "pgrep -af plasmashell | head -5",
            "GCHECK", timeout=90,
        )
        interactive = ("wayland" in gcheck.lower()
                       and "plasmashell" in gcheck.lower())
        result["installed"]["sddm_interactive_login"] = interactive
        if not interactive:
            # Harness adaptation for observability: enable autologin and restart
            # SDDM so a real graphical session exists. Documented, not hidden.
            sess = guest_cmd(
                child2,
                "ls /usr/share/wayland-sessions/ 2>/dev/null | grep -i plasma | head -1",
                "WSESS", timeout=60,
            ).strip().splitlines()
            session_file = sess[-1].strip() if sess else "plasmawayland.desktop"
            guest_cmd(
                child2,
                "printf '%s\\n' 'Sanora-Dev-2026!' | sudo -S sh -c '"
                "mkdir -p /etc/sddm.conf.d; "
                "printf \"[Autologin]\\nUser=sanora\\nSession=" + session_file +
                "\\nRelogin=false\\n\" > /etc/sddm.conf.d/zz-sanora-test.conf; "
                "systemctl restart sddm'; echo SANORA_SDDM_AUTOLOGIN_READY",
                "SDDMAUTO", timeout=120,
            )
            time.sleep(45)
        result["installed"]["graphical_session_source"] = (
            "interactive SDDM login via QEMU keyboard" if interactive
            else "SDDM autologin (harness adaptation, documented)"
        )
        capture(hmp2, "installed-graphical")

        # --- Validate from the installed system (now with a graphical session) ---
        text = guest_cmd(child2, VALIDATE, "VALIDATE", timeout=240)
        (out / "installed-checks.txt").write_text(text, encoding="utf-8")
        secs = [s.strip() for s in text.split("SEP")]
        keys = [k for k, _ in VALIDATE_SECTIONS]
        evidence = {
            key: (secs[i] if i < len(secs) else "")
            for i, key in enumerate(keys)
        }
        r = result.setdefault("installed", {})
        r.update(evidence)
        r["evidence_section_count"] = len(secs)

        if args.mode == "luks":
            luks_ok = (
                ("Version:       2" in evidence["luks_dump"]
                 or "LUKS2" in evidence["luks_dump"].upper())
                and "crypto_LUKS" in evidence["lsblk"]
                and bool(evidence["crypttab"].strip())
            )
            initramfs_ok = bool(re.search(
                r"cryptsetup|cryptroot|crypttab|dm-crypt|askpass|keyfile",
                evidence["initramfs_crypto"], re.I))
            wp = result["installed"].get("wrong_passphrase", {})
            wrong_ok = wp.get("status") == "PASS"
            result["installed"]["luks2_validation"] = {
                "luks2_header_and_crypttab": "PASS" if luks_ok else "FAIL",
                "initramfs_crypto_components": "PASS" if initramfs_ok else "FAIL",
                "wrong_passphrase_rejected": "PASS" if wrong_ok else "FAIL",
                "correct_passphrase_prompts_seen": boot["prompt_seen"],
                "passphrase_required_at_boot": (
                    "PASS" if boot["prompt_seen"] >= 1 else "FAIL")
            }
        else:
            luks_ok = True       # plain scenario: LUKS not applicable
            initramfs_ok = True  # plain scenario: crypto initramfs not applicable
            wrong_ok = True
            result["installed"]["luks2_validation"] = {
                "luks2_header_and_crypttab": "NOT TESTED (plain scenario)",
                "initramfs_crypto_components": "NOT TESTED (plain scenario)",
                "wrong_passphrase_rejected": "NOT TESTED (plain scenario)",
            }

        checks = {
            "os_release_sanora": 'NAME="SANORA OS"' in evidence["os_release"]
                                  and 'ID="sanora"' in evidence["os_release"],
            "sanora_info": "SANORA OS" in evidence["sanora_info"],
            "correct_user": args.user in evidence["user_host"],
            "english_locale": "en_US" in evidence["locale"],
            "root_filesystem": "ext4" in evidence["root_mount"],
            "efi_system_partition": bool(re.search(r"EFI|BOOT", evidence["efi_boot_files"])),
            "grub_installed": "grub" in evidence["efi_boot_files"].lower()
                              or "SANORA" in evidence["efi_boot_files"],
            "luks2": luks_ok,
            "initramfs_crypto": initramfs_ok,
            "wrong_passphrase_rejected": wrong_ok,
            "sddm_authenticated_session": interactive,
            "wayland": ("XDG_SESSION_TYPE=wayland" in evidence["graphical_env"]
                        and "wayland" in evidence["session_types"].lower()),
            "sanora_theme": "SANORA_THEME_PRESENT" in evidence["theme_present"],
            "global_theme_selected": "org.sanora" in evidence["look_and_feel"],
            "icon_theme": "sanora" in evidence["icon_theme"].lower(),
            "wallpaper": "WALLPAPER_PRESENT" in evidence["wallpaper"],
            "desktop_widgets": bool(re.search(
                r"org\.kde\.plasma\.taskmanager|org\.kde\.plasma\.kickoff|org\.kde\.panel",
                evidence["desktop_widgets"])),
            "desktop_apps": "MISSING:" not in evidence["desktop_apps"],
            "graphical_session_running": (
                "plasmashell" in evidence["kwin_wayland_processes"]
                and "WAYLAND_DISPLAY=" in evidence["graphical_env"]
            ),
            "services": "SDDM_ACTIVE=active" in evidence["sddm"],
            "pipewire": all(
                f"{k}=active" in evidence["services"]
                for k in ("PIPEWIRE", "PIPEWIRE_PULSE", "WIREPLUMBER")),
            "networkmanager": "NETWORKMANAGER=active" in evidence["services"],
        }
        r["checks"] = checks
        r["checks_status"] = {
            k: ("PASS" if v else "FAIL") for k, v in checks.items()
        }
        result["status"] = "SUCCESS" if all(checks.values()) else "PARTIAL"
        r["verdict_note"] = (
            "PASS = observed in the installed VM. PARTIAL = installation and "
            "reboot succeeded but at least one check failed. NOT TESTED is used "
            "explicitly for scenario-inapplicable items."
        )
        capture(hmp2, "installed-01-desktop")

    except (pexpect.TIMEOUT, pexpect.EOF, OSError, ValueError) as exc:
        result["errors"].append(f"installed-system validation raised: {exc}")
        result["status"] = "PARTIAL"
    finally:
        kill(child2, hmp2, handle2)

    result["evidence"]["screenshots"] = screenshots_b64
    # A completed installation plus a successful boot into the installed
    # system is the milestone; PARTIAL verdicts (e.g. unverified Wayland or
    # LUKS2) stay visible in the JSON but must not stop the workflow from
    # running the second scenario. Never reported as an unqualified SUCCESS.
    ok = (
        result.get("phases", {}).get("installation_completed") is True
        and result.get("phases", {}).get("installed_serial_login") is True
    )
    return finish(0 if ok else 1)


def _stream(path):
    """Yield file chunks (kept separate for the hash helper above)."""
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            yield block


if __name__ == "__main__":
    sys.exit(main())
