---
title: Contributing
description: How to set up a development environment, run the linters and tests, and submit changes to FastAdmin.
---

# Contributing

Bug reports, fixes and features are welcome — open an
[issue](https://github.com/vsdudakov/fastadmin/issues) or a pull request.

## Project layout

```
fastadmin/           # the Python package (api, models, settings, bundled static frontend)
frontend/            # React (Vite + antd) frontend sources, built into fastadmin/static
tests/               # backend test suite (pytest, 100% coverage gate)
examples/            # runnable example apps for each framework/ORM combination
docs/                # MkDocs Material documentation (this site)
```

## Development setup

You need Python 3.12+, [uv](https://docs.astral.sh/uv/) and Node.js with
yarn (for the frontend).

```bash
git clone https://github.com/vsdudakov/fastadmin.git
cd fastadmin
make dev        # uv sync --all-extras + frontend yarn install
```

## Day-to-day commands

| Command | What it does |
| --- | --- |
| `make lint` | ruff check + ruff format --check + ty, then the frontend linters. |
| `make format` | Auto-fix lint issues and reformat (Python + frontend). |
| `make test` | Backend tests with a **100% coverage gate**, then frontend tests. |
| `make build` | Build the frontend into `fastadmin/static` and the wheel/sdist via `uv build`. |
| `make docs` | Build this documentation site into `./site` (strict mode). |
| `make docs-serve` | Live-preview the docs at `http://127.0.0.1:8000`. |

The backend tests need the required admin settings:

```bash
export ADMIN_USER_MODEL=User
export ADMIN_USER_MODEL_USERNAME_FIELD=username
export ADMIN_SECRET_KEY=secret_key
make test
```

## Pull requests

- Run `make format`, `make lint` and `make test` before pushing — CI enforces
  all three.
- Keep the 100% backend coverage gate green: new code needs tests.
- Update the relevant docs page and `CHANGELOG.md` when behavior changes.
- Releases are cut by tagging `v*` on `main`; the release workflow builds and
  publishes to PyPI, and the docs workflow deploys this site to GitHub Pages.
