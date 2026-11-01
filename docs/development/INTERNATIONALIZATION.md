# Internationalisation

SANORA OS is an **international** distribution. English is the default system
language, documentation language, UI terminology and default user experience.
The project is not designed for the Netherlands or any single country.

## Defaults (single source of truth)

`config/version.env`:

```
SANORA_DEFAULT_LOCALE=en_US.UTF-8
SANORA_DEFAULT_KEYBOARD=us
```

These values are used in:

- `build/live-build/options.sh` → `--bootappend-live "boot=live components
  locales=${SANORA_DEFAULT_LOCALE} keyboard-layouts=${SANORA_DEFAULT_KEYBOARD}
  ..."` (live-config at boot).
- `0010-sanora-locale.hook.chroot` → `/etc/locale.gen`, `locale-gen`,
  `/etc/default/locale` with `LANG="en_US.UTF-8"`, `LANGUAGE="en_US:en"` for
  the installed system.
- `/etc/os-release` → `DEFAULT_LANGUAGE="en"` (SANORA extension field).
- `config/system/sanora.conf` → `SANORA_DEFAULT_LANGUAGE=en`,
  `SANORA_INTERNATIONAL=true`.
- `out/build-metadata.json` → `defaults.ui_language`, `defaults.international`.

`tests/test_static.py` asserts these defaults and fails if `nl_NL` or another
country-specific hardcoded locale appears in `config/` or `build/`.

## Font and input coverage

`config/packages/60-i18n-a11y.list.chroot` deliberately installs broad Unicode
font coverage (`fonts-noto-core`, `fonts-noto-color-emoji`,
`fonts-dejavu-core`, `fonts-liberation2`) and the IBus input-method framework,
plus AT-SPI and Orca for accessibility. This is preparation, not a claim that
all languages are fully supported: additional fonts, input-method engines and
language packs are added per locale later.

## SANORA-authored code: gettext conventions

`sanora-info` follows normal Linux gettext conventions:

```sh
TEXTDOMAIN=sanora-base
TEXTDOMAINDIR=/usr/share/locale
msg() { gettext "$1"; }        # falls back to the literal if gettext is absent
```

- UI labels are message strings, not embedded in logic.
- Product names (`SANORA OS`) and identifiers are deliberately **not**
  translated.
- Adding a language later means shipping
  `/usr/share/locale/<lang>/LC_MESSAGES/sanora-base.mo`. No code change is
  needed. There is no `.po` catalogue yet (`Planned`).
- Calamares slideshow sentences use `qsTr()`; `branding.desc` uses
  `${NAME}`/`${VERSION_ID}` substitution from `/etc/os-release` instead of
  hardcoded English product strings.
- KDE/Qt, GTK and AppStream metadata bring their own upstream translations.

## How to add a locale (future, not yet implemented)

1. Append the locale to `/etc/locale.gen` in hook 0010 and regenerate.
2. Add the corresponding font/input-method packages to
   `config/packages/60-i18n-a11y.list.chroot`.
3. Ship a compiled gettext catalogue for `sanora-base`.
4. Add a boot smoke test that selects the locale via the kernel command line
   (`locales=...`, `keyboard-layouts=...`).
5. Update `docs/architecture/STATUS.md` only after that test actually ran.

## Explicitly not done

- No translation infrastructure server, no `.po` files, no translated docs,
  no locale selector in the installer beyond upstream Calamares' locale module,
  no country-specific defaults, no Dutch UI text in new files.
- No claim that any non-English locale is verified working.
