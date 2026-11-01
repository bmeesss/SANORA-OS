SANORA OS @SANORA_VERSION@ - development ISO
=============================================

This is a DEVELOPMENT milestone, not a release. It is intended for building
and testing the SANORA OS foundation only. Do not use it as a daily driver and
do not redistribute it as a finished product.

Base:        Debian 13 "trixie" (amd64)
Desktop:     KDE Plasma on Wayland
Build tool:  Debian live-build
Language:    English (en_US.UTF-8) by default; international by design

Source code: https://github.com/bmeesss/SANORA-OS
Licence:     SANORA-authored code is GPL-2.0-or-later. Upstream components
             keep their own licences; see /usr/share/doc/*/copyright inside
             the running system and THIRD_PARTY.md in the source repository.

Known limitations of this image:
 - It has NOT been boot-tested unless docs/architecture/STATUS.md says so.
 - NVIDIA proprietary components are NOT included (ADR-0007 is blocked).
 - There is no signed SANORA package repository and no own Secure Boot shim.
 - Firmware redistribution has not yet had its required legal review.

For build and test instructions see docs/development/BUILDING.md in the
repository. Never assume a build works until you have verified it.
