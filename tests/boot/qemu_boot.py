#!/usr/bin/env python3
"""Boot a SANORA OS ISO in QEMU and record *verifiable* evidence.

This is a test harness, not a claim of success. Every result written to
boot-validation.json is derived from something actually observed: serial
console output, a framebuffer screenshot, or QEMU's exit state.

Usage:
  qemu_boot.py --iso out/sanora-0.1.0-dev-amd64.iso \
               --mode uefi|bios --out out/boot-uefi --timeout 420

Requirements (Debian trixie): qemu-system-x86, ovmf, python3-pexpect,
netpbm (or the built-in PPM->PNG converter), coreutils.
"""

from __future__ import annotations

import argparse
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
except ImportError:  # pragma: no cover - reported as a skipped test, not a pass
    pexpect = None


# --------------------------------------------------------------------------
# Framebuffer screenshot conversion (P6 PPM -> PNG, stdlib only)
# --------------------------------------------------------------------------
def ppm_to_png(src: pathlib.Path, dst: pathlib.Path) -> tuple[int, int] | None:
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
    width, height = int(fields[1]), int(fields[2])
    i += 1  # single whitespace after maxval
    pixels = raw[i : i + width * height * 3]
    if len(pixels) < width * height * 3:
        return None
    rows = b"".join(
        b"\x00" + pixels[y * width * 3 : (y + 1) * width * 3]
        for y in range(height)
    )

    def chunk(kind: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + kind
            + data
            + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        )

    png = (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(rows, 6))
        + chunk(b"IEND", b"")
    )
    dst.write_bytes(png)
    return width, height


def screenshot_nonblank(path: pathlib.Path) -> bool:
    """A completely uniform framebuffer means nothing was rendered."""
    raw = path.read_bytes()
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
    if len(fields) < 4:
        return False
    width, height = int(fields[1]), int(fields[2])
    i += 1
    pixels = raw[i : i + width * height * 3]
    if len(pixels) < width * height * 3:
        return False
    # Sample a sparse grid; count distinct colours.
    colours = set()
    step = max(1, width // 40)
    for y in range(0, height, max(1, height // 30)):
        base = y * width * 3
        for x in range(0, width, step):
            off = base + x * 3
            colours.add(pixels[off : off + 3])
    return len(colours) > 3


# --------------------------------------------------------------------------
# QEMU human-monitor client over a UNIX socket
# --------------------------------------------------------------------------
class HMP:
    def __init__(self, path: str):
        self.path = path
        self.sock = None
        for _ in range(40):
            try:
                s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                s.settimeout(2)
                s.connect(path)
                self.sock = s
                break
            except OSError:
                time.sleep(0.25)
        if self.sock:
            self._drain()

    def _drain(self) -> None:
        try:
            self.sock.settimeout(0.4)
            self.sock.recv(65536)
        except OSError:
            pass

    def cmd(self, command: str) -> str:
        if not self.sock:
            return ""
        try:
            self.sock.settimeout(3)
            self.sock.sendall((command + "\n").encode())
            time.sleep(0.5)
            return self.sock.recv(65536).decode("utf-8", "replace")
        except OSError as exc:
            return f"<hmp error: {exc}>"

    def close(self) -> None:
        if self.sock:
            try:
                self.sock.close()
            except OSError:
                pass


# --------------------------------------------------------------------------
# Guest interaction
# --------------------------------------------------------------------------
def guest_command(child, command: str, tag: str, timeout: int) -> str:
    # The "" split prevents the typed command line (if echoed) from containing
    # the literal marker: only real command output can match it.
    begin, end = f"SANORA_{tag}_BEGIN", f"SANORA_{tag}_END"
    child.sendline(
        f"echo SANORA\"\"_{tag}_BEGIN; {command}; echo SANORA\"\"_{tag}_END"
    )
    child.expect_exact(begin, timeout=40)
    child.expect_exact(end, timeout=timeout)
    return child.before or ""


MAIN_CHECKS = (
    "cat /etc/os-release; echo SEP; "
    "sanora-info; echo SEP; "
    "cat /etc/default/locale; echo SEP; "
    "loginctl list-sessions --no-legend; echo SEP; "
    "for s in $(loginctl list-sessions --no-legend | awk '{print $1}'); do "
    "loginctl show-session -p Type -p Name --value $s; done; echo SEP; "
    "pgrep -a kwin_wayland; pgrep -a plasmashell; pgrep -a sddm; echo SEP; "
    "for p in $(pgrep -f kwin_wayland | head -2); do "
    "tr '\\000' '\\n' < /proc/$p/environ | "
    "grep -E '^(XDG_SESSION_TYPE|WAYLAND_DISPLAY|XDG_CURRENT_DESKTOP|XDG_SESSION_DESKTOP)='; "
    "done; echo SEP; "
    "systemctl is-active NetworkManager sddm; echo SEP; "
    "systemctl --user is-active pipewire pipewire-pulse wireplumber; echo SEP; "
    "for b in dolphin konsole plasma-discover fwupdmgr flatpak appstreamcli calamares cryptsetup; do "
    "command -v $b || echo MISSING:$b; done; "
    "test -x /usr/sbin/cryptsetup && echo CRYPTSETUP_PRESENT || echo CRYPTSETUP_ABSENT; echo SEP; "
    "fwupdmgr --version; echo SEP; "
    "ip -brief address; echo SEP; "
    "locale -a; echo SEP; "
    "ls -l /usr/share/sanora/branding /usr/share/sanora/wallpapers "
    "/etc/calamares/branding/sanora; echo SEP; "
    "grep -E 'componentName|productName' /etc/calamares/branding/sanora/branding.desc; echo SEP; "
    "grep -E '^[[:space:]]*branding:' /etc/calamares/settings.conf; echo SEP; "
    "lsblk -o NAME,SIZE,TYPE,FSTYPE; echo SEP; "
    "grep -niE 'luks|encrypt|cipher' /etc/calamares/modules/partition.conf; echo SEP; "
    "cat /etc/calamares/modules/partition.conf; echo SEP; "
    "echo XDG_SESSION_TYPE=$XDG_SESSION_TYPE; echo SEP; "
    "uname -a"
)

LOCALE_CHECKS = (
    "echo 'nl_NL.UTF-8 UTF-8' | sudo -n tee -a /etc/locale.gen; "
    "sudo -n locale-gen; locale -a | grep -i nl_nl || echo NO_NL_LOCALE; "
    "LC_ALL=nl_NL.UTF-8 LANG=nl_NL.UTF-8 sanora-info; "
    "echo LOCALE_DONE"
)

CALAMARES_CHECKS = (
    "ls -l /tmp/.X11-unix/ 2>/dev/null; "
    "XAUTH=$(ls /run/user/1000/xauth_* 2>/dev/null | head -1); "
    "echo XAUTHORITY=${XAUTH:-none}; "
    "sudo -n -b env DISPLAY=:0 XAUTHORITY=$XAUTH QT_QPA_PLATFORM=xcb calamares "
    "> /tmp/sanora-calamares.log 2>&1; "
    "sleep 10; pgrep -a calamares || echo CALAMARES_NOT_RUNNING; "
    "tail -30 /tmp/sanora-calamares.log 2>/dev/null; "
    "echo CALAMARES_DONE"
)

# Baseline measurements only -- explicitly NOT performance achievements.
PERF_CHECKS = (
    "systemd-analyze; echo SEP; "
    "free -m; echo SEP; "
    "cat /proc/loadavg; echo SEP; "
    "ps -e --no-headers | wc -l; echo SEP; "
    "grep -R 'sanora-wallpaper' $HOME/.config/plasma-org.kde.plasma.desktop-appletsrc "
    "2>/dev/null || echo NO_WALLPAPER_CONFIG; echo SEP; "
    "dpkg -l cryptsetup 2>/dev/null | tail -2; echo SEP; "
    "echo '--- /etc/calamares files ---'; "
    "find /etc/calamares -maxdepth 3 -type f 2>/dev/null | sort; echo SEP; "
    "echo '--- calamares-settings-debian configs ---'; "
    "dpkg -L calamares-settings-debian 2>/dev/null | grep -E '\\.conf$|partition' | head -40; echo SEP; "
    "echo '--- partition module configs anywhere ---'; "
    "find /usr/share/calamares /etc/calamares -iname '*partition*' 2>/dev/null | head -30; echo SEP; "
    "echo '--- calamares settings.conf ---'; "
    "cat /etc/calamares/settings.conf 2>/dev/null | head -80; echo SEP; "
    "ls -l /usr/sbin/cryptsetup /usr/bin/calamares 2>/dev/null; echo PERF_DONE"
)


def derive_checks(text: str, sections: list[str]) -> dict:
    def sec(n: int) -> str:
        return sections[n] if n < len(sections) else ""

    identity = 'NAME="SANORA OS"' in sec(0) and 'ID="sanora"' in sec(0)
    info = "SANORA OS" in sec(1) and "trixie" in sec(1) and "amd64" in sec(1)
    english = ("LANG=\"en_US.UTF-8\"" in sec(2) or "en_US.UTF-8" in sec(2)) and \
              ("DEFAULT_LANGUAGE=\"en\"" in sec(0))
    sessions = sec(4)
    wayland_env = sec(6)
    wayland = (
        "wayland" in sessions.lower()
        or "XDG_SESSION_TYPE=wayland" in wayland_env
        or "kwin_wayland" in sec(5)
        or "/usr/bin/kwin_wayland" in sec(5)
    )
    plasma = "plasmashell" in sec(5) or "kwin_wayland" in sec(5)
    network = "active" in sec(7) and bool(re.search(r"\d+\.\d+\.\d+\.\d+", sec(11)))
    audio = "active" in sec(8)
    apps = sec(9)
    discover = "plasma-discover" in apps and "MISSING:plasma-discover" not in apps
    fwupd = bool(re.search(r"client version|fwupd version|\d+\.\d+\.\d+", sec(10) + apps))
    branding = (
        "sanora-logo" in sec(13)
        and "sanora-wallpaper" in sec(13)
        and "branding.desc" in sec(13)
    )
    calamares_branding = "sanora" in sec(14).lower() and "sanora" in sec(15).lower()
    disks = bool(re.search(r"\b(sr0|cdrom|vd[a-z]|sd[a-z]|nvme)\b", sec(16)))
    cryptsetup = "CRYPTSETUP_PRESENT" in apps or (
        "cryptsetup" in apps and "MISSING:cryptsetup" not in apps
    )
    luks_conf = "luks" in sec(17).lower() or "luks" in sec(18).lower()
    return {
        "os_release_sanora": identity,
        "sanora_info": info,
        "english_default": english,
        "wayland": wayland,
        "plasma": plasma,
        "network": network,
        "audio_subsystem": audio,
        "discover": discover,
        "fwupd": fwupd,
        "file_manager": "dolphin" in apps and "MISSING:dolphin" not in apps,
        "terminal": "konsole" in apps and "MISSING:konsole" not in apps,
        "branding_files": branding,
        "calamares_branding_config": calamares_branding,
        "disk_detection": disks,
        "cryptsetup_available": cryptsetup,
        "luks_mentioned_in_partition_conf": luks_conf,
    }


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--iso", required=True)
    ap.add_argument("--mode", choices=["uefi", "bios"], required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--timeout", type=int, default=420)
    args = ap.parse_args()

    outdir = pathlib.Path(args.out)
    outdir.mkdir(parents=True, exist_ok=True)
    result: dict = {
        "schema": "sanora.boot-validation/1",
        "mode": args.mode,
        "iso": args.iso,
        "status": "SKIPPED",
        "errors": [],
        "checks": {},
        "evidence": {},
    }

    def finish(code: int) -> int:
        (outdir / "boot-validation.json").write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        print(json.dumps(result, indent=2, sort_keys=True))
        return code

    iso = pathlib.Path(args.iso) if args.iso and args.iso != "None" else None
    if not iso or not iso.is_file():
        result["errors"].append("No ISO found; boot test SKIPPED (not passed).")
        return finish(0)
    if pexpect is None:
        result["errors"].append("python3-pexpect missing; boot test SKIPPED.")
        return finish(0)

    # Stream the checksum: a live ISO is several GB and must not be slurped
    # into the QEMU host's RAM.
    digest = hashlib.sha256()
    with iso.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(block)
    result["iso_sha256"] = digest.hexdigest()
    result["iso_size_bytes"] = iso.stat().st_size

    kvm = os.path.exists("/dev/kvm") and os.access("/dev/kvm", os.W_OK)
    firmware = None
    if args.mode == "uefi":
        for candidate in ("/usr/share/qemu/OVMF.fd", "/usr/share/OVMF/OVMF_CODE_4M.fd"):
            if pathlib.Path(candidate).is_file():
                firmware = candidate
                break
        if not firmware:
            result["errors"].append("OVMF firmware not found; UEFI test SKIPPED.")
            return finish(0)

    mon_sock = f"/tmp/sanora-qemu-{args.mode}.sock"
    for p in (mon_sock,):
        try:
            os.unlink(p)
        except OSError:
            pass

    argv = [
        "qemu-system-x86_64",
        "-no-reboot", "-m", "4096", "-smp", "2",
        "-cdrom", str(iso.resolve()), "-boot", "d",
        "-vga", "std", "-display", "none",
        "-serial", "stdio",
        "-monitor", f"unix:{mon_sock},server=on,wait=off",
        "-netdev", "user,id=n0", "-device", "e1000,netdev=n0",
        "-device", "intel-hda", "-device", "hda-duplex",
        "-rtc", "base=utc",
        "-pidfile", str(outdir / "qemu.pid"),
    ]
    if kvm:
        argv += ["-enable-kvm", "-cpu", "host"]
    else:
        argv += ["-cpu", "max"]
    if args.mode == "uefi":
        argv += ["-machine", "q35", "-bios", firmware]

    result["qemu_command"] = " ".join(shlex.quote(a) for a in argv)
    result["kvm"] = kvm
    result["firmware"] = firmware
    result["status"] = "ATTEMPTED"

    serial_log = outdir / "serial.log"
    stderr_log = outdir / "qemu-stderr.log"
    cmd = " ".join(shlex.quote(a) for a in argv) + " 2>" + shlex.quote(str(stderr_log))
    log_handle = serial_log.open("w", encoding="utf-8", errors="replace")

    result["vm"] = {
        "ram_mb": 4096,
        "vcpus": 2,
        "vga": "std",
        "firmware": firmware or "SeaBIOS (QEMU default)",
        "accel": "kvm" if kvm else "tcg",
        "network": "qemu user-mode (e1000)",
        "audio_device": "intel-hda / hda-duplex",
        "display": "none (framebuffer captured via QMP screendump)",
    }

    boot_start = time.time()
    child = None
    hmp = None
    try:
        child = pexpect.spawn(
            "/bin/bash", ["-c", cmd], timeout=30,
            encoding="utf-8", codec_errors="replace", dimensions=(24, 120),
        )
        child.logfile_read = log_handle
        hmp = HMP(mon_sock)
        result["hmp_connected"] = bool(hmp.sock)

        # Boot menu screenshot, then press Enter to boot the default entry.
        time.sleep(8)
        menu_ppm = outdir / "boot-menu.ppm"
        hmp.cmd(f"screendump {menu_ppm}")
        if menu_ppm.is_file():
            menu_png = outdir / "boot-menu.png"
            dims = ppm_to_png(menu_ppm, menu_png)
            result["evidence"]["boot_menu_screenshot"] = str(menu_png)
            result["evidence"]["boot_menu_dimensions"] = list(dims) if dims else None
            result["evidence"]["boot_menu_nonblank"] = screenshot_nonblank(menu_ppm)
        hmp.cmd("sendkey ret")

        # Wait for a serial login prompt or an already-autologged shell.
        deadline = time.time() + args.timeout
        shell_ready = False
        while time.time() < deadline:
            remaining = max(5, min(30, deadline - time.time()))
            try:
                idx = child.expect(
                    [r"login:", r"Password:", r"\$ ", r"# ",
                     pexpect.TIMEOUT, pexpect.EOF],
                    timeout=remaining,
                )
            except pexpect.TIMEOUT:
                idx = 4
            if idx == 0:
                child.sendline("user")
            elif idx == 1:
                child.sendline("live")
            elif idx in (2, 3):
                shell_ready = True
                break
            elif idx == 5:
                result["errors"].append("QEMU exited before a shell appeared")
                break
        boot_info = result.setdefault("boot", {})
        boot_info["login_shell"] = shell_ready
        boot_info["boot_to_shell_seconds"] = (
            round(time.time() - boot_start, 1) if shell_ready else None
        )
        boot_info["serial_log"] = str(serial_log)

        if shell_ready:
            child.sendline("stty -echo")
            time.sleep(0.5)
            try:
                child.sendline("echo SANORA\"\"_SHELL_READY")
                child.expect_exact("SANORA_SHELL_READY", timeout=30)
            except (pexpect.TIMEOUT, pexpect.EOF) as exc:
                result["errors"].append(f"shell handshake failed: {exc}")

            try:
                text = guest_command(child, MAIN_CHECKS, "MAIN", timeout=150)
                (outdir / "guest-checks.txt").write_text(text, encoding="utf-8")
                sections = [s.strip() for s in text.split("SEP")]
                result["checks"] = derive_checks(text, sections)
                result["evidence"]["guest_checks"] = str(outdir / "guest-checks.txt")
                result["evidence"]["partition_conf"] = sections[18] if len(sections) > 18 else ""
                result["evidence"]["xdg_session_type_shell"] = (
                    sections[19] if len(sections) > 19 else ""
                )
                result["evidence"]["uname"] = sections[20] if len(sections) > 20 else ""
            except (pexpect.TIMEOUT, pexpect.EOF) as exc:
                result["errors"].append(f"main guest checks failed: {exc}")

            try:
                locale_text = guest_command(
                    child,
                    "echo LOCALE_BEGIN; " + LOCALE_CHECKS,
                    "LOCALE", timeout=120,
                )
                (outdir / "locale-checks.txt").write_text(locale_text, encoding="utf-8")
                result["checks"]["additional_locale_nl_NL"] = (
                    "nl_nl.utf8" in locale_text.lower()
                    and "NO_NL_LOCALE" not in locale_text
                    and "SANORA OS" in locale_text
                )
                result["evidence"]["locale_checks"] = str(outdir / "locale-checks.txt")
            except (pexpect.TIMEOUT, pexpect.EOF) as exc:
                result["checks"]["additional_locale_nl_NL"] = False
                result["errors"].append(f"locale checks failed: {exc}")

            try:
                cal_text = guest_command(
                    child,
                    "echo CALAMARES_BEGIN; " + CALAMARES_CHECKS,
                    "CAL", timeout=90,
                )
                (outdir / "calamares-checks.txt").write_text(cal_text, encoding="utf-8")
                result["checks"]["calamares_starts"] = (
                    "CALAMARES_NOT_RUNNING" not in cal_text
                    and "calamares" in cal_text.lower()
                )
                result["evidence"]["calamares_checks"] = str(outdir / "calamares-checks.txt")
            except (pexpect.TIMEOUT, pexpect.EOF) as exc:
                result["checks"]["calamares_starts"] = False
                result["errors"].append(f"Calamares checks failed: {exc}")

            try:
                perf_text = guest_command(
                    child,
                    "echo PERF_BEGIN; " + PERF_CHECKS,
                    "PERF", timeout=120,
                )
                (outdir / "performance-baseline.txt").write_text(
                    perf_text, encoding="utf-8"
                )
                result["evidence"]["performance_baseline"] = str(
                    outdir / "performance-baseline.txt"
                )
                result["checks"]["wallpaper_config_applied"] = (
                    "sanora-wallpaper" in perf_text
                    and "NO_WALLPAPER_CONFIG" not in perf_text
                )
                result["evidence"]["calamares_module_config_files"] = (
                    perf_text.split("SEP")[6] if len(perf_text.split("SEP")) > 6 else ""
                )
            except (pexpect.TIMEOUT, pexpect.EOF) as exc:
                result["errors"].append(f"performance baseline checks failed: {exc}")

        # Desktop screenshot (whatever is actually on the framebuffer).
        desktop_ppm = outdir / "desktop.ppm"
        hmp.cmd(f"screendump {desktop_ppm}")
        if desktop_ppm.is_file():
            desktop_png = outdir / "desktop.png"
            dims = ppm_to_png(desktop_ppm, desktop_png)
            result["evidence"]["desktop_screenshot"] = str(desktop_png)
            result["evidence"]["desktop_dimensions"] = list(dims) if dims else None
            result["evidence"]["desktop_nonblank"] = screenshot_nonblank(desktop_ppm)

        # Kernel evidence from the serial log.
        serial_text = serial_log.read_text(encoding="utf-8", errors="replace")
        boot_info["kernel_loaded"] = bool(
            re.search(r"Linux version|systemd\[1\]|Welcome to|login:", serial_text)
        )
        boot_info["serial_bytes"] = len(serial_text)
        result["status"] = "BOOTED" if boot_info["kernel_loaded"] else "NO_KERNEL_EVIDENCE"

    except Exception as exc:  # noqa: BLE001 - harness must always write evidence
        result["errors"].append(f"harness exception: {type(exc).__name__}: {exc}")
        result["status"] = "HARNESS_ERROR"
    finally:
        if hmp:
            hmp.close()
        if child:
            try:
                child.close(force=True)
            except Exception:
                pass
        # Stop QEMU by pid if it survived pexpect's process group.
        pidfile = outdir / "qemu.pid"
        if pidfile.is_file():
            try:
                pid = int(pidfile.read_text().strip())
                os.kill(pid, signal.SIGTERM)
            except (ValueError, OSError, ProcessLookupError):
                pass
        log_handle.close()
        try:
            os.unlink(mon_sock)
        except OSError:
            pass

    if stderr_log.is_file():
        result["evidence"]["qemu_stderr"] = str(stderr_log)
        err = stderr_log.read_text(errors="replace").strip()
        if err:
            result["evidence"]["qemu_stderr_tail"] = err[-2000:]

    # Exit 1 when the kernel never showed up: a red CI run is honest feedback.
    return finish(1 if result["status"] in ("NO_KERNEL_EVIDENCE", "HARNESS_ERROR") else 0)


if __name__ == "__main__":
    sys.exit(main())
