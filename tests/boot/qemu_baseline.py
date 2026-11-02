#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""Measure unmodified Debian 13 KDE in the same VM as SANORA OS.

Downloads/expects the official Debian live KDE ISO, boots it in QEMU with the
same VM configuration used for SANORA, and records the same baseline metrics
(systemd-analyze, free -m, load average, process count, boot-to-shell).

The Debian ISO has no serial console in its shipped boot parameters, so its
own kernel and initramfs are extracted from the ISO and booted directly with
`console=ttyS0`. This is a legitimate live-system boot of the same media, not
a modified image. No optimisation is performed; this is measurement only.
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import re
import shlex
import shutil
import signal
import subprocess
import time

try:
    import pexpect
except ImportError:
    pexpect = None

BASELINE_CMDS = (
    "echo BASELINE_BEGIN; systemd-analyze; echo SEP; "
    "free -m; echo SEP; cat /proc/loadavg; echo SEP; "
    "ps -e --no-headers | wc -l; echo SEP; "
    "cat /etc/os-release | head -5; echo BASELINE_DONE"
)


def guest_cmd(child, command, tag, timeout=180):
    b, e = f"SANORA_{tag}_BEGIN", f"SANORA_{tag}_END"
    child.sendline(f"echo SANORA\"\"_{tag}_BEGIN; {command}; echo SANORA\"\"_{tag}_END")
    child.expect_exact(b, timeout=60)
    child.expect_exact(e, timeout=timeout)
    return child.before or ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--debian-iso", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--sanora-boot", default="out/boot-uefi/boot-validation.json")
    ap.add_argument("--sanora-perf", default="out/boot-uefi/performance-baseline.txt")
    ap.add_argument("--timeout", type=int, default=600)
    args = ap.parse_args()

    out = pathlib.Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    result = {
        "schema": "sanora.baseline-comparison/1",
        "status": "SKIPPED",
        "errors": [],
        "vm": "4096 MiB RAM, 2 vCPU, KVM, QEMU std VGA, user-mode e1000, OVMF/SeaBIOS",
    }

    def finish(code):
        (out / "baseline-comparison.json").write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        print(json.dumps(result, indent=2, sort_keys=True))
        return code

    iso = pathlib.Path(args.debian_iso)
    if not iso.is_file():
        result["errors"].append("Debian KDE ISO missing; comparison SKIPPED")
        return finish(0)
    if pexpect is None:
        result["errors"].append("python3-pexpect missing; comparison SKIPPED")
        return finish(0)

    work = out / "baseline-vm"
    work.mkdir(parents=True, exist_ok=True)
    kernel, initrd = work / "vmlinuz", work / "initrd.img"
    try:
        subprocess.run(
            ["xorriso", "-osirrox", "on", "-indev", str(iso),
             "-extract", "/live/vmlinuz", str(kernel),
             "-extract", "/live/initrd.img", str(initrd)],
            check=True, capture_output=True, text=True, timeout=300,
        )
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        result["errors"].append(f"could not extract Debian kernel/initrd: {exc}")
        return finish(0)

    kvm = os.path.exists("/dev/kvm") and os.access("/dev/kvm", os.W_OK)
    argv = [
        "qemu-system-x86_64", "-no-reboot", "-m", "4096", "-smp", "2",
        "-kernel", str(kernel), "-initrd", str(initrd),
        "-append", "boot=live components console=tty0 console=ttyS0,115200 quiet",
        "-cdrom", str(iso.resolve()), "-vga", "std", "-display", "none",
        "-serial", "stdio", "-monitor", "none",
        "-netdev", "user,id=n0", "-device", "e1000,netdev=n0",
        "-rtc", "base=utc", "-pidfile", str(work / "qemu.pid"),
    ]
    argv += ["-enable-kvm", "-cpu", "host"] if kvm else ["-cpu", "max"]
    result["qemu_command"] = " ".join(shlex.quote(x) for x in argv)

    shell_cmd = " ".join(shlex.quote(x) for x in argv) \
        + " 2>" + shlex.quote(str(work / "qemu-stderr.log"))
    log = (out / "baseline-serial.log").open("w", encoding="utf-8", errors="replace")
    child = None
    start = time.time()
    try:
        child = pexpect.spawn(
            "/bin/bash", ["-c", shell_cmd], timeout=60,
            encoding="utf-8", codec_errors="replace", dimensions=(24, 140),
        )
        child.logfile_read = log
        deadline = time.time() + args.timeout
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
                break
        result["serial_shell"] = shell
        result["boot_to_shell_seconds"] = round(time.time() - start, 1) if shell else None
        if not shell:
            result["errors"].append("no serial shell in Debian baseline VM")
            return finish(1)
        child.sendline("stty -echo")
        time.sleep(0.4)
        text = guest_cmd(child, BASELINE_CMDS, "BASELINE", timeout=180)
        (out / "debian-baseline.txt").write_text(text, encoding="utf-8")
        secs = [s.strip() for s in text.split("SEP")]
        result["debian"] = {
            "systemd_analyze": secs[0] if len(secs) > 0 else "",
            "free": secs[1] if len(secs) > 1 else "",
            "loadavg": secs[2] if len(secs) > 2 else "",
            "process_count": secs[3] if len(secs) > 3 else "",
            "os_release": secs[4] if len(secs) > 4 else "",
        }
    except Exception as exc:  # noqa: BLE001
        result["errors"].append(f"baseline harness exception: {exc}")
        return finish(1)
    finally:
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
        log.close()

    # Parse SANORA numbers from the existing boot evidence.
    sanora = {}
    try:
        sanora_boot = json.loads(pathlib.Path(args.sanora_boot).read_text())
        sanora["boot_to_shell_seconds"] = sanora_boot.get("boot", {}).get(
            "boot_to_shell_seconds"
        )
        perf = pathlib.Path(args.sanora_perf).read_text(errors="replace")
        m = re.search(r"Startup finished in .*?= ([\d.]+)s", perf)
        if m:
            sanora["systemd_total_seconds"] = float(m.group(1))
        m = re.search(r"Mem:\s+(\d+)\s+(\d+)\s+(\d+)", perf)
        if m:
            sanora["mem_total_mb"] = int(m.group(1))
            sanora["mem_used_mb"] = int(m.group(2))
        m = re.search(r"^(\d+)$", perf, re.M)
        parts = [p.strip() for p in perf.split("SEP")]
        if len(parts) > 3:
            try:
                sanora["process_count"] = int(parts[3].splitlines()[-1])
            except (ValueError, IndexError):
                pass
        if len(parts) > 2:
            sanora["loadavg"] = parts[2].strip().splitlines()[0] if parts[2].strip() else ""
        if len(parts) > 1:
            m = re.search(r"Mem:\s+(\d+)\s+(\d+)\s+(\d+)", parts[1])
            if m:
                sanora["mem_total_mb"] = int(m.group(1))
                sanora["mem_used_mb"] = int(m.group(2))
        db = result["debian"]
        m = re.search(r"= ([\d.]+)s", db["systemd_analyze"])
        debian_total = float(m.group(1)) if m else None
        m = re.search(r"Mem:\s+(\d+)\s+(\d+)\s+(\d+)", db["free"])
        debian_used = int(m.group(2)) if m else None
        result["comparison"] = {
            "systemd_total_seconds": {
                "sanora": sanora.get("systemd_total_seconds"),
                "debian": debian_total,
                "delta_seconds": (
                    round(sanora["systemd_total_seconds"] - debian_total, 3)
                    if sanora.get("systemd_total_seconds") is not None and debian_total is not None
                    else None
                ),
            },
            "idle_ram_used_mb": {
                "sanora": sanora.get("mem_used_mb"),
                "debian": debian_used,
                "delta_mb": (
                    sanora["mem_used_mb"] - debian_used
                    if sanora.get("mem_used_mb") is not None and debian_used is not None
                    else None
                ),
            },
            "boot_to_shell_seconds": {
                "sanora": sanora.get("boot_to_shell_seconds"),
                "debian": result.get("boot_to_shell_seconds"),
            },
            "process_count": {
                "sanora": sanora.get("process_count"),
                "debian": db["process_count"],
            },
            "load_average": {
                "sanora": sanora.get("loadavg"),
                "debian": db["loadavg"],
            },
        }
        result["note"] = (
            "Baseline only. No optimisation was applied and no claim of superior "
            "performance is made. Live ISO RAM figures include the squashfs "
            "page cache on both systems."
        )
        result["status"] = "MEASURED"
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        result["errors"].append(f"could not parse SANORA evidence: {exc}")
        result["status"] = "PARTIAL"

    return finish(0)


if __name__ == "__main__":
    raise SystemExit(main())
