# live-build configuration

This directory holds the **canonical** Debian `live-build` configuration for
SANORA OS. It is not a custom ISO builder: `build.sh` calls the upstream `lb
config` and `lb build` commands.

| File | Purpose |
|---|---|
| `options.sh` | The exact `lb config` arguments (bash array sourced by `build.sh`) |
| `hooks/normal/*.hook.chroot` | Scripts executed inside the chroot at the end of the chroot stage |

## Why there is no `auto/config`

Upstream recommends an `auto/config` wrapper so that `lb config` options survive
re-runs. SANORA OS instead keeps the options in one bash array in `options.sh`
and regenerates the config tree from scratch on every build (`build.sh` removes
`build/work/live/config` first). This avoids two sources of truth. The trade-off
is that developers must use `./build.sh` rather than running `lb config`
directly inside the work directory; this is documented in
`docs/development/BUILDING.md`.

## What is generated, what is source

`lb config` writes `config/common`, `config/bootstrap`, `config/chroot`,
`config/binary` and `config/source` into `build/work/live/`. Those generated
files are **not** committed (see `.gitignore`). All committed SANORA inputs live
in `config/packages/`, `config/desktop/`, `config/system/`, `branding/`,
`installer/`, `packages/` and the hooks in this directory.
`build/scripts/assemble-config.sh` copies those inputs into the generated
`config/` tree as `config/package-lists/`, `config/packages.chroot/`,
`config/hooks/normal/`, `config/includes.chroot/` and `config/includes.binary/`.

## Option verification

The option names are validated offline by `tests/test_static.py` against a
snapshot of the trixie `lb_config(1)` synopsis in
`tests/data/lb_config_trixie_options.txt`. Adding an option that is not in that
list fails CI. The snapshot is documentation of the upstream man page, not a
list of guessed flags.

## Host-side caveat

`lb config` may read system-wide defaults from `/etc/live/build.conf` and
`/etc/live/build/`. On a shared build host, check those files before building;
they can change mirrors or archive areas. SANORA OS does not override them
silently.
