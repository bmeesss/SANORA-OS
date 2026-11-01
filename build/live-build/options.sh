#!/usr/bin/env bash
# Canonical `lb config` options for the SANORA OS development ISO.
#
# Every option below was checked against the Debian trixie live-build
# 1:20250505+deb13u1 lb_config(1) synopsis:
#   https://manpages.debian.org/trixie/live-build/lb_config.1.en.html
#   (retrieved 2026-11-01)
# tests/test_static.py enforces that no unverified option is added here.
#
# This file is sourced by build.sh AFTER config/version.env. It is intentionally
# bash (an array) because build.sh is the single supported entrypoint; no
# live-build `auto/config` POSIX wrapper duplicates these values.

LB_OPTIONS=(
  # Base distribution and architecture (ADR-0001)
  "--mode" "debian"
  "--system" "live"
  "--distribution" "${DEBIAN_SUITE}"
  "--architecture" "${SANORA_ARCH}"
  "--archive-areas" "main contrib non-free-firmware"
  "--security" "true"
  "--updates" "true"
  "--backports" "false"

  # Verified package sources, host-independent mirrors
  "--apt" "apt"
  "--apt-secure" "true"
  "--apt-indices" "true"
  "--apt-recommends" "true"
  "--apt-source-archives" "false"
  "--mirror-bootstrap" "${SANORA_DEBIAN_MIRROR}"
  "--mirror-chroot" "${SANORA_DEBIAN_MIRROR}"
  "--mirror-chroot-security" "${SANORA_SECURITY_MIRROR}"
  "--mirror-binary" "${SANORA_DEBIAN_MIRROR}"
  "--mirror-binary-security" "${SANORA_SECURITY_MIRROR}"

  # Image type and boot chain. Debian's signed shim is reused; SANORA OS does
  # not ship its own Microsoft-signed shim (phase-1 risk R-01).
  "--binary-image" "iso-hybrid"
  "--bootloaders" "syslinux grub-efi"
  "--uefi-secure-boot" "auto"
  "--debian-installer" "none"
  "--debian-installer-gui" "false"
  "--bootappend-live" "boot=live components locales=${SANORA_DEFAULT_LOCALE} keyboard-layouts=${SANORA_DEFAULT_KEYBOARD} quiet splash"
  "--memtest" "none"

  # Firmware comes from Debian's non-free-firmware area. No SANORA-specific or
  # NVIDIA firmware is bundled. See THIRD_PARTY.md and ADR-0007.
  "--firmware-binary" "true"
  "--firmware-chroot" "true"

  # Filesystem, kernel and init (no custom kernel: ADR-0001)
  "--chroot-filesystem" "squashfs"
  "--chroot-squashfs-compression-type" "xz"
  "--linux-flavours" "amd64"
  "--linux-packages" "linux-image"
  "--initramfs" "live-boot"
  "--initsystem" "systemd"

  # Reproducibility / output metadata
  "--checksums" "sha256"
  "--zsync" "false"
  "--source" "false"
  "--utc-time" "true"
  "--image-name" "${SANORA_IMAGE_NAME}"
  "--iso-application" "SANORA OS development ISO"
  "--iso-publisher" "SANORA OS project - ${SANORA_HOMEPAGE}"
  "--iso-volume" "${SANORA_ISO_VOLUME}"
)
