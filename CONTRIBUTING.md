# Contributing to SANORA OS

SANORA OS is an international open-source project. English is the working
language for issues, pull requests, code comments, commit messages and
documentation. The project is in the **development foundation** phase: the
priority is a working, reproducible build rather than visual polish.

## Before you start

1. Read the [README](README.md) and
   [docs/development/BUILDING.md](docs/development/BUILDING.md).
2. Read [docs/architecture/STATUS.md](docs/architecture/STATUS.md) to see what
   is implemented, tested and blocked.
3. Read [docs/decisions/README.md](docs/decisions/README.md). Approved
   architecture decisions are not changed silently; propose a new ADR.

## Development rules

- Inspect the repository before changing it. Do not overwrite existing work
  unnecessarily; `README.md` and `SANORA_OS_ARCHITECTURE.md` are existing files.
- Prefer configuration, packages, `/etc` files, systemd drop-ins, KDE defaults
  and integration layers over forks of upstream projects.
- Keep changes small and verifiable. One logical change per commit.
- Separate facts, assumptions and recommendations in documents and discussions.
- Never invent commands, package names, APIs, benchmark results or hardware
  support claims. Verify against official documentation.
- Never report a test as passed unless it actually ran and you inspected the
  result. State `Implemented`, `Tested`, `Partially tested`, `Planned`,
  `Blocked` or `Unknown` explicitly.
- Do not add dependencies or background services without a documented reason.
- Do not copy Apple assets, branding or interface designs.
- Do not hardcode English UI strings in SANORA-authored code that should later
  be translatable. Use gettext conventions; see
  [docs/development/INTERNATIONALIZATION.md](docs/development/INTERNATIONALIZATION.md).
- Do not build or publish a release ISO before the architecture gates are
  satisfied.

## Workflow

```sh
git clone https://github.com/bmeesss/SANORA-OS.git
cd SANORA-OS
./build.sh --check          # must pass before opening a PR
# make one small change
./build.sh --config-only    # offline assembly of the build configuration
./tests/run.sh              # full offline test suite
git add <files>
git commit -m "area: short imperative description"
```

Meaningful commit prefixes: `build:`, `config:`, `system:`, `branding:`,
`installer:`, `tests:`, `ci:`, `docs:`, `fix:`.

Pull requests must include:

- what changed and why,
- which tests were executed and their exact results,
- any new dependency, license or upstream patch and its justification,
- an update to `docs/architecture/STATUS.md` when a status changes.

## Reviewing

Reviewers check technical correctness against upstream documentation,
licensing, internationalization, reproducibility impact and whether the change
respects the approved architecture. NVIDIA redistribution, Secure Boot signing,
own APT repositories and release publication are gated decisions and must not
be introduced by an unrelated pull request.

## Code of conduct

All participation is governed by [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
Security issues follow [SECURITY.md](SECURITY.md).
