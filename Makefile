.PHONY: clean
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + > /dev/null 2>&1
	find . -type f -name "*.pyc" -exec rm -rf {} + > /dev/null 2>&1
	rm -rf htmlcov
	rm -rf .coverage

.PHONY: dev_fastapi
dev_fastapi:
	poetry run uvicorn tests.dev.fastapi.dev:app --reload --host=0.0.0.0 --port=8090

.PHONY: dev_flask
dev_flask:
	poetry run flask --app tests.dev.flask.dev run --debug

.PHONY: dev_django
dev_django:
	poetry run python tests/dev/django/dev/manage.py migrate
	poetry run python tests/dev/django/dev/manage.py runserver

.PHONY: fix
fix:
	poetry run pyupgrade --exit-zero-even-if-changed --py39-plus fastadmin/**/*.py tests/**/*.py
	poetry run isort --settings-path pyproject.toml fastadmin tests
	poetry run black --config pyproject.toml fastadmin tests
	make -C frontend fix

.PHONY: lint
lint:
	poetry run isort --diff --check-only --settings-path pyproject.toml fastadmin tests
	poetry run black --diff --check --config pyproject.toml fastadmin tests
	poetry run flake8 --show-source --config .flake8 fastadmin tests
	poetry run mypy --show-error-code --install-types --non-interactive --namespace-packages --show-traceback --config-file pyproject.toml fastadmin
	make -C frontend lint

.PHONY: test
test:
	ADMIN_ENV_FILE=example.env poetry run pytest --cov=fastadmin --cov-report=term-missing --cov-report=xml --cov-fail-under=100 -s tests
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
	poetry install --all-extras
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


.PHONY: push
push:
	make fix
	make lint
	make test
	make build
	make pre-commit
	git stash
	git checkout main
	git pull origin main
	git stash pop
	git add .
	git commit -am "$(message)"
	git push origin main
