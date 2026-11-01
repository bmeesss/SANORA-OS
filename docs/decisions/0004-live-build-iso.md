# ADR-0004 — Debian live-build for ISO creation

- **Status:** Accepted by the implementation kickoff 2026-11-01 (architecture
  ADR-0004 was `Voorgesteld`).
- **Decision:** use upstream Debian `live-build` (`lb config` / `lb build`) to
  produce an `iso-hybrid` image. **No custom ISO builder.**
- **Rationale:** live-build is Debian's own tooling, is documented, supports
  chroot hooks/includes/package lists and has reproducibility support
  (`SOURCE_DATE_EPOCH`, checksums). Writing a builder would duplicate upstream
  work and violate the project principle.
- **Consequences:** host tools (syslinux, GRUB, xorriso, squashfs-tools) must
  match the target distribution; ~20 GB disk and root are needed; full ISO
  reproducibility is not yet verified (Debian trixie 13.2 images were reported
  not fully reproducible).
- **Implementation:** `build.sh`, `build/live-build/options.sh`,
  `build/scripts/*`, `.github/workflows/iso.yml`. Options were verified against
  trixie `lb_config(1)` 1:20250505+deb13u1 and enforced by `tests/test_static.py`.
- **Verification status:** `./build.sh --config-only` works offline; a full
  `lb build` has **not** completed (no live-build / no mirror in this sandbox).
