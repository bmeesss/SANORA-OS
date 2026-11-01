# ADR-0001 — Debian 13 "trixie" stable (amd64) as the base

- **Status:** Accepted 2026-11-01 (architecture ADR-0001; confirmed by user)
- **Decision:** SANORA OS is built from unmodified Debian 13 trixie stable
  packages for amd64, using archive areas `main contrib non-free-firmware`.
  No custom kernel from scratch, no Ubuntu/Fedora base.
- **Rationale:** five-year support window, Debian derivatives explicitly
  welcome, DFSG-compliant `main`, security fixes backported rather than version
  jumps, `live-build` reproducibility tooling, no vendor trademark restrictions
  like Canonical's IP policy, no six-month rebase cadence like Fedora.
- **Consequences:** Debian kernel 6.12 and Plasma 6.3.6 are older than some
  alternatives; newest hardware may need measured backports. Backports are
  disabled for now. All firmware redistribution requires a legal review.
- **Implementation:** `config/version.env`, `build/live-build/options.sh`
  (`--distribution trixie --architecture amd64 --archive-areas ...`),
  `config/packages/`.
- **Not reopened by:** the implementation kickoff.
