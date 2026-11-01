# ADR-0008 — English default, international by design

- **Status:** Accepted by the implementation kickoff 2026-11-01.
- **Decision:** SANORA OS is an **international** Linux distribution. English
  is the primary system language, documentation language, UI terminology and
  default user experience. The project is not designed specifically for the
  Netherlands. Internationalisation is considered from the start so more
  languages can be added later.
- **Consequences for existing work:** the phase-1 architecture document is
  Dutch and is kept unchanged as a historical record. All **new**
  documentation, code, configuration, commit messages and UI text is English.
  Translating or superseding that document is a separate explicit task.
- **Implementation:** `config/version.env`
  (`SANORA_DEFAULT_LOCALE=en_US.UTF-8`, `SANORA_DEFAULT_KEYBOARD=us`),
  `--bootappend-live locales=... keyboard-layouts=...`, hook
  `0010-sanora-locale.hook.chroot`, `/etc/os-release DEFAULT_LANGUAGE="en"`,
  `gettext`/`qsTr()` usage in SANORA-authored code, broad Unicode font and
  input-method packages. See `docs/development/INTERNATIONALIZATION.md`.
- **Guardrails:** `tests/test_static.py` fails on a hardcoded `nl_NL` locale in
  `config/` or `build/`; `tests/test_assemble.py` checks the assembled tree.
- **Not yet done:** translation catalogues, per-locale font packs, a locale
  selector beyond upstream Calamares, translated documentation. No non-English
  locale is claimed to work.
