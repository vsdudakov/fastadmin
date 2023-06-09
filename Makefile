.PHONY: clean
clean:
	@exec find . -type d -name "__pycache__" -exec rm -rf {} + > /dev/null 2>&1
	@exec find . -type f -name "*.pyc" -exec rm -rf {} + > /dev/null 2>&1
	@exec rm -rf htmlcov
	@exec rm -rf .coverage

.PHONY: fix
fix:
	@echo "Run ruff"
	@exec ruff --fix fastadmin tests
	@echo "Run isort"
	@exec isort fastadmin tests
	@echo "Run black"
	@exec black fastadmin tests
	@echo "Run mypy"
	@exec mypy -p fastadmin -p tests
	@echo "Run frontend linters"
	@exec cd frontend && make fix

.PHONY: lint
lint:
	@echo "Run ruff"
	@exec ruff fastadmin tests
	@echo "Run isort"
	@exec isort --check-only fastadmin tests
	@echo "Run black"
	@exec black --check --diff fastadmin tests
	@echo "Run mypy"
	@exec mypy -p fastadmin -p tests
	@echo "Run frontend linters"
	@exec cd frontend && make lint

.PHONY: test
test:
	poetry run python generate_db.py
	ADMIN_ENV_FILE=example.env poetry run pytest --cov=fastadmin --cov-report=term-missing --cov-report=xml --cov-fail-under=90 -s tests
	@exec cd frontend && make test

.PHONY: kill
kill:
	@exec kill -9 $$(lsof -t -i:8090)
	@exec kill -9 $$(lsof -t -i:3030)

.PHONY: collectstatic
collectstatic:
	@exec rm -rf ./fastadmin/static/js
	@exec rm -rf ./fastadmin/static/css
	@exec cp -rf ./frontend/build/static/js/ ./fastadmin/static/js/
	@exec cp -rf ./frontend/build/static/css/ ./fastadmin/static/css/
	@exec mv fastadmin/static/js/main*.js fastadmin/static/js/main.min.js
	@exec mv fastadmin/static/css/main*.css fastadmin/static/css/main.min.css
	@exec rm fastadmin/static/js/*.txt

.PHONY: install
install:
	@exec poetry install --all-extras
	@exec make -C frontend install


.PHONY: docs
docs:
	@exec make -C docs build
	@exec cp ./docs/README.md ./README.md


.PHONY: build
build:
	@exec make docs
	@exec make -C frontend build
	@exec make collectstatic

.PHONY: pre-commit-install
pre-commit-install:
	@exec poetry run pip install pre-commit
	@exec poetry run pre-commit install

.PHONY: pre-commit
pre-commit:
	@exec poetry run pre-commit run --all-files

.PHONY: push
push:
	@exec make fix
	@exec make lint
	@exec make test
	@exec make build
	@exec make pre-commit
	@exec git stash
	@exec git checkout main
	@exec git pull origin main
	@exec git stash pop
	@exec git add .
	@exec git commit -am "$(message)"
	@exec git push origin main
