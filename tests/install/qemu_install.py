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


VALIDATE = (
    "cat /etc/os-release; echo SEP; sanora-info; echo SEP; "
    "whoami; hostname; echo SEP; "
    "grep -E '^(LANG|LANGUAGE)=' /etc/default/locale; echo SEP; "
    "lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINTS; echo SEP; "
    "findmnt -no SOURCE,FSTYPE,TARGET /; echo SEP; "
    "ls -R /boot/efi/EFI 2>/dev/null | head -30; echo SEP; "
    "sudo -n cryptsetup luksDump /dev/vda3 2>&1 | head -30; echo SEP; "
    "sudo -n efibootmgr -v 2>&1 | head -20; echo SEP; "
    "kreadconfig6 --file kdeglobals --group KDE --key LookAndFeelPackage; echo SEP; "
    "test -f /usr/share/plasma/look-and-feel/org.sanora.light.desktop/metadata.json "
    "&& echo SANORA_THEME_PRESENT || echo SANORA_THEME_MISSING; echo SEP; "
    "loginctl list-sessions --no-legend; echo SEP; "
    "for s in $(loginctl list-sessions --no-legend | awk '{print $1}'); do "
    "loginctl show-session -p Type --value $s; done; echo SEP; "
    "systemd-analyze; echo SEP; free -m; echo SEP; "
    "ps -e --no-headers | wc -l; echo SEP; "
    "cat /etc/calamares/branding/sanora/branding.desc | head -5; echo SEP; "
    "uname -a"
)


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
            "-bios", combined_fd,
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
        "firmware": combined_fd, "accel": "kvm" if kvm else "tcg",
        "network": "qemu user-mode e1000", "uefi_vars_persisted": False,
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
            "QT_ACCESSIBILITY=1 QT_LINUX_ACCESSIBILITY_ALWAYS_ON=1 "
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
            f"sudo -n env DISPLAY=:0 XAUTHORITY={shlex.quote(xauth)} "
            f"python3 {driver_path} {encrypt_flag} "
            f"--timeout {args.timeout} --user {shlex.quote(args.user)} "
            f"--password {shlex.quote(args.password)} "
            f"--luks-passphrase {shlex.quote(args.luks_passphrase)} "
            "> /tmp/sanora-driver-stdout.log 2>&1; echo DRIVER_RC=$?"
        )
        child.sendline(driver)
        # Wait for the driver's final RESULT line (it also writes a JSON file).
        driver_deadline = time.time() + args.timeout
        driver_result = ""
        while time.time() < driver_deadline:
            try:
                idx = child.expect(
                    [r"RESULT: SUCCESS", r"RESULT: (FAILED|TIMEOUT)", pexpect.TIMEOUT, pexpect.EOF],
                    timeout=30,
                )
            except pexpect.TIMEOUT:
                idx = 2
            if idx in (0, 1):
                driver_result = "SUCCESS" if idx == 0 else "FAILED"
                capture(hmp, "install-02-finished")
                break
            if idx == 3:
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
    child2, hmp2, handle2 = run_phase(qemu_args(False), "installed", 900)
    if child2 is None:
        return finish(1)
    try:
        deadline = time.time() + 300
        logged_in = False
        while time.time() < deadline:
            try:
                idx = child2.expect(
                    [r"login:", r"Password:", r"\$ ", pexpect.TIMEOUT, pexpect.EOF],
                    timeout=min(60, max(5, deadline - time.time())),
                )
            except pexpect.TIMEOUT:
                idx = 3
            if idx == 0:
                child2.sendline(args.user)
            elif idx == 1:
                child2.sendline(args.password)
            elif idx == 2:
                logged_in = True
                break
            elif idx == 4:
                result["errors"].append("QEMU exited during installed boot")
                break
        result["phases"]["installed_serial_login"] = logged_in
        capture(hmp2, "installed-00-desktop")
        if not logged_in:
            result["errors"].append("could not log into installed system")
            return finish(1)

        child2.sendline("stty -echo")
        time.sleep(0.4)
        text = guest_cmd(child2, VALIDATE, "VALIDATE", timeout=180)
        (out / "installed-checks.txt").write_text(text, encoding="utf-8")
        secs = [s.strip() for s in text.split("SEP")]
        evidence = {
            "os_release": secs[0] if len(secs) > 0 else "",
            "sanora_info": secs[1] if len(secs) > 1 else "",
            "user_host": secs[2] if len(secs) > 2 else "",
            "locale": secs[3] if len(secs) > 3 else "",
            "lsblk": secs[4] if len(secs) > 4 else "",
            "root_mount": secs[5] if len(secs) > 5 else "",
            "efi_boot_files": secs[6] if len(secs) > 6 else "",
            "luks_dump": secs[7] if len(secs) > 7 else "",
            "efibootmgr": secs[8] if len(secs) > 8 else "",
            "look_and_feel": secs[9] if len(secs) > 9 else "",
            "theme_present": secs[10] if len(secs) > 10 else "",
            "sessions": secs[11] if len(secs) > 11 else "",
            "session_types": secs[12] if len(secs) > 12 else "",
            "systemd_analyze": secs[13] if len(secs) > 13 else "",
            "free": secs[14] if len(secs) > 14 else "",
            "process_count": secs[15] if len(secs) > 15 else "",
            "branding": secs[16] if len(secs) > 16 else "",
            "uname": secs[17] if len(secs) > 17 else "",
        }
        r = result.setdefault("installed", {})
        r.update(evidence)
        checks = {
            "os_release_sanora": 'NAME="SANORA OS"' in evidence["os_release"]
                                  and 'ID="sanora"' in evidence["os_release"],
            "sanora_info": "SANORA OS" in evidence["sanora_info"],
            "correct_user": args.user in evidence["user_host"],
            "english_locale": "en_US" in evidence["locale"],
            "root_filesystem": bool(re.search(r"ext4|btrfs", evidence["root_mount"])),
            "efi_system_partition": bool(re.search(r"EFI|BOOT", evidence["efi_boot_files"])),
            "grub_installed": "grub" in evidence["efi_boot_files"].lower()
                              or "SANORA" in evidence["efi_boot_files"],
            "luks2": "LUKS2" in evidence["luks_dump"].upper()
                     or "Version:       2" in evidence["luks_dump"],
            "sanora_theme": "SANORA_THEME_PRESENT" in evidence["theme_present"],
            "global_theme_selected": "org.sanora" in evidence["look_and_feel"],
            "wayland": "wayland" in evidence["session_types"].lower(),
        }
        result["installed"]["checks"] = checks
        result["status"] = "SUCCESS" if all(checks.values()) else "PARTIAL"
        if args.mode == "plain":
            # LUKS is not expected for the plain scenario.
            checks["luks2"] = True
            result["installed"]["checks"] = checks
            result["status"] = "SUCCESS" if all(checks.values()) else "PARTIAL"
        capture(hmp2, "installed-01-desktop")
    finally:
        kill(child2, hmp2, handle2)

    result["evidence"]["screenshots"] = screenshots_b64
    return finish(0 if result["status"] == "SUCCESS" else 1)


def _stream(path):
    """Yield file chunks (kept separate for the hash helper above)."""
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            yield block


if __name__ == "__main__":
    sys.exit(main())
