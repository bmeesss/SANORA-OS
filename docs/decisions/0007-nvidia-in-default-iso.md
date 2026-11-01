# ADR-0007 — NVIDIA support in the default ISO

- **Status:** **BLOCKED — awaiting explicit confirmation. Not implemented.**
- **Scope:** this is the only part of the implementation kickoff that was
  stopped. Everything else in the build foundation proceeded.

## Why it is blocked

Two facts conflict and the project rules require a decision, not a guess:

1. In the architecture review on 2026-11-01 the user chose
   `nvidia=in_iso` ("NVIDIA support in the default ISO"). `SANORA_OS_ARCHITECTURE.md`
   Bijlage A.1 records this as an **explicit deviation** from the technical
   advice (opt-in after installation).
2. The same document's §0.5 lists **ADR-0007 as `Ter bevestiging`**, and
   Bijlage A.2 contains an open question asking for confirmation of ADR-0007
   with six consequences, ending with: no ISO/package/installer configuration
   is created before that answer.

The implementation kickoff states: *"If the NVIDIA decision still requires
confirmation in the architecture document, stop that specific implementation
and flag it clearly instead of making the decision yourself."* It also says
*"do not silently bundle proprietary components without documenting the legal
and technical implications"* and lists legal/licensing issues among the stop
conditions.

Therefore NVIDIA bundling is **flagged and stopped**, not decided either way.
This is not a reversal of the user's earlier choice; it is the explicit gate in
the approved document being respected.

## What is actually in the repository

- **No** `nvidia-*` package in `config/packages/`.
- **No** NVIDIA driver, userspace, GSP firmware, CUDA or DKMS hook.
- **No** vendored `.deb` from NVIDIA.
- `tests/test_static.py` and `tests/test_assemble.py` fail if an NVIDIA package
  appears in the package lists, hooks or `sanora-base` payload.
- `out/build-metadata.json` records
  `gates.nvidia_in_iso = "BLOCKED - ADR-0007 awaiting confirmation"`.
- `THIRD_PARTY.md` lists NVIDIA components under "Explicitly NOT
  redistributed".
- Open in-kernel `nouveau`, `amdgpu`, `i915`/`xe` and Mesa are untouched; no
  hardware compatibility is claimed.

## What confirming ADR-0007 would require (from Bijlage A.2)

1. The full NVIDIA Driver License Agreement text must be present in the image
   **and** visible in the installer. The licence permits redistribution for
   OSI-licensed kernels only when binaries stay **unmodified** and the
   agreement is delivered to each recipient.
2. One exact pinned driver version per ISO, with kernel modules, GSP firmware
   and userspace from the same release, recorded in `THIRD_PARTY.md` and
   checked in CI.
3. Known limitations of the open kernel modules (slower GPU initialisation,
   longer S3/S4/RTD3 latency, marginally higher power draw) documented in
   release notes and measured against KPI-7/KPI-8.
4. MOK enrolment under Secure Boot, or a clear "disable Secure Boot" warning
   in the installer. SANORA OS has no own signed shim (R-01).
5. Legal review of the licence restrictions (reverse engineering, modified
   headers, datacenter use for GeForce/Titan) and of all firmware blobs.
6. `diffoscope` comparison per build, since firmware patterns were a known
   cause of non-reproducible trixie 13.2 live images.

## Decision requested

Confirm ADR-0007 with the six consequences above, **or** choose the opt-in
route from the original technical advice. Until the answer is given, no
NVIDIA component will be added. This ADR will be updated with the decision,
date and rationale — not silently edited.
