.PHONY: clean
clean:
	@exec find . -type d -name "__pycache__" -exec rm -rf {} + > /dev/null 2>&1
	@exec find . -type f -name "*.pyc" -exec rm -rf {} + > /dev/null 2>&1
	@exec rm -rf htmlcov
	@exec rm -rf .coverage

.PHONY: fix
fix:
	@echo "Run ruff"
	@exec poetry run ruff check --fix fastadmin tests docs examples
	@echo "Run isort"
	@exec poetry run isort fastadmin tests docs examples
	@echo "Run black"
	@exec poetry run black fastadmin tests docs examples
	@echo "Run mypy"
	@exec poetry run mypy -p fastadmin -p docs
	@echo "Run frontend linters"
	@exec make -C frontend fix

.PHONY: lint
lint:
	@echo "Run ruff"
	@exec poetry run ruff check fastadmin tests docs examples
	@echo "Run isort"
	@exec poetry run isort --check-only fastadmin tests docs examples
	@echo "Run black"
	@exec poetry run black --check --diff fastadmin tests docs examples
	@echo "Run mypy"
	@exec poetry run mypy -p fastadmin -p docs
	@echo "Run frontend linters"
	@exec make -C frontend lint

# -n auto : fix django
.PHONY: test
test:
	@exec poetry run pytest -n 1 --cov=fastadmin --cov-report=term-missing --cov-report=xml --cov-fail-under=80 -s tests
	@exec make -C frontend test

.PHONY: kill
kill:
	@exec kill -9 $$(lsof -t -i:8090)
	@exec kill -9 $$(lsof -t -i:3030)

.PHONY: install
install:
	@exec pip install poetry
	@exec poetry install --all-extras
	@exec make -C frontend install

.PHONY: docs
docs:
	@exec make -C docs build

.PHONY: build
build:
	@exec make docs
	@exec make -C frontend build

.PHONY: push
pre-push:
	@exec make fix
	@exec make lint
	@exec make docs
	@exec make build
