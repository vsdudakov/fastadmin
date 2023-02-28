.PHONY: clean
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + > /dev/null 2>&1
	find . -type f -name "*.pyc" -exec rm -rf {} + > /dev/null 2>&1
	rm -rf htmlcov
	rm -rf .coverage

.PHONY: dev
dev:
	poetry run uvicorn fastadmin.dev:app --reload --host=0.0.0.0 --port=8090

.PHONY: fix
fix:
	poetry run pyupgrade --exit-zero-even-if-changed --py39-plus fastadmin/**/*.py
	poetry run isort --settings-path pyproject.toml fastadmin
	poetry run black --config pyproject.toml fastadmin
	make -C frontend fix

.PHONY: lint
lint:
	poetry run isort --diff --check-only --settings-path pyproject.toml fastadmin
	poetry run black --diff --check --config pyproject.toml fastadmin
	poetry run flake8 --show-source --config .flake8 fastadmin
	poetry run mypy --show-error-code --install-types --non-interactive --namespace-packages --show-traceback --config-file pyproject.toml fastadmin
	make -C frontend lint

.PHONY: test
test:
	ADMIN_ENV_FILE=example.env poetry run pytest --cov=fastadmin --cov-report=term --cov-report=xml --cov-fail-under=40 -s tests
	make -C frontend test

.PHONY: kill
kill:
	kill -9 $$(lsof -t -i:8090)
	kill -9 $$(lsof -t -i:3030)

.PHONY: collectstatic
collectstatic:
	rm -rf ./fastadmin/static/js
	rm -rf ./fastadmin/static/css
	cp -rf ./frontend/build/static/js/ ./fastadmin/static/js/
	cp -rf ./frontend/build/static/css/ ./fastadmin/static/css/
	mv fastadmin/static/js/main*.js.map fastadmin/static/js/main.min.js.map
	mv fastadmin/static/js/main*.js fastadmin/static/js/main.min.js
	mv fastadmin/static/css/main*.css.map fastadmin/static/css/main.min.css.map
	mv fastadmin/static/css/main*.css fastadmin/static/css/main.min.css
	rm fastadmin/static/js/*.txt

.PHONY: install
install:
	poetry install
	make -C frontend install

.PHONY: build
build:
	make -C frontend build
	make collectstatic

.PHONY: pre-commit-install
pre-commit-install:
	pip install pre-commit
	pre-commit install

.PHONY: pre-commit
pre-commit:
	pre-commit run --all-files
