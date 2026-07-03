.PHONY: dev build lint format test cov docs docs-serve example clean kill

LINT_PATHS := fastadmin tests examples

# Create the local environment: Python deps via uv (all ORM/framework extras
# plus the dev group) and the frontend via yarn.
dev:
	uv sync --all-extras
	make -C frontend install

# Build the frontend into fastadmin/static and package the wheel + sdist.
build:
	make -C frontend build
	uv build

# Blocking gate: ruff check + format + ty, then the frontend linters.
lint:
	uv run ruff check $(LINT_PATHS)
	uv run ruff format --check $(LINT_PATHS)
	uv run ty check fastadmin
	make -C frontend lint

format:
	uv run ruff check --fix $(LINT_PATHS)
	uv run ruff format $(LINT_PATHS)
	make -C frontend fix

# -n auto runs the suite in parallel via pytest-xdist. Each worker gets its own
# SQLite file (Django/Pony) with a busy timeout, so there are no "database is
# locked" failures.
test:
	uv run pytest -n auto --cov=fastadmin --cov-report=term-missing --cov-report=xml tests
	make -C frontend test

cov: test

# --- Documentation (MkDocs Material) -----------------------------------------
# Build the static site into ./site. Social cards are generated only in CI
# (the docs workflow installs the Cairo system libraries they need).
docs:
	uv run --group docs mkdocs build --strict

# Live-preview at http://127.0.0.1:8000 (social cards off for speed).
docs-serve:
	uv run --group docs mkdocs serve

kill:
	kill -9 $$(lsof -t -i:8090)
	kill -9 $$(lsof -t -i:3030)

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + > /dev/null 2>&1 || true
	find . -type f -name "*.pyc" -delete > /dev/null 2>&1 || true
	rm -rf htmlcov .coverage coverage.xml dist site .cache
