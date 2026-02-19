# FastAdmin documentation

This folder contains the source and build script for the [FastAdmin documentation](https://vsdudakov.github.io/fastadmin) site.

## Building the docs

From the **project root**:

```bash
cd docs
make build
```

Or:

```bash
cd docs && poetry run python build.py
```

This will:

1. Generate **`index.html`** — the full documentation site (Introduction, Getting Started, Settings, Dashboard Widgets, Model Admins, Inline Admins, Changelog).
2. Generate **`../README.md`** — the project README (Introduction and Getting Started sections only).

## Structure

| Path | Purpose |
|------|---------|
| `build.py` | Build script: loads content, renders Jinja templates, writes output. |
| `templates/` | Jinja templates for the HTML site and README. |
| `templates/index.html` | Main HTML layout and navigation. |
| `templates/readme.md` | README template (badges, screenshots, then generated sections). |
| `code/` | Example code snippets included in the docs (quick tutorial, models, dashboard, inlines). |
| `assets/` | CSS, JS, and images for the HTML site. |

Content for each section is defined in `build.py` in `get_page_context()` and `get_sections()`.
