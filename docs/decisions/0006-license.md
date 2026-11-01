# ADR-0006 — Licensing

- **Status:** Accepted for SANORA-authored **code**; open for documentation
  and branding assets (Q-01 in the phase-1 document).
- **Decision:** SANORA-authored source code is `GPL-2.0-or-later`.
  `LICENSE` contains the SPDX `GPL-2.0-or-later` text (retrieved from
  `spdx/license-list-data` on 2026-11-01). Scripts carry SPDX headers or
  `THIRD_PARTY.md` entries.
- **Rationale:** the user chose GPL for own code in the architecture review;
  GPLv2-or-later is compatible with the Linux kernel module ecosystem and with
  Debian's licensing expectations.
- **Open:** a licence for documentation and branding assets has **not** been
  decided. Until then, original artwork ships with `sanora-base` under
  `GPL-2.0-or-later` and this is recorded in
  `packages/sanora-base/DEBIAN/copyright` and `THIRD_PARTY.md`. Do not assume
  CC-BY-SA-4.0; it was only a proposal.
- **Upstream:** all Debian/KDE/etc. packages keep their own licences, visible
  at `/usr/share/doc/<package>/copyright`. Nothing is forked.
- **Gate:** legal review of firmware blobs, fonts/codecs and (if ADR-0007 is
  confirmed) the NVIDIA licence is required before any public ISO.
