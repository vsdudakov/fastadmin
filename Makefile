.PHONY: clean
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + > /dev/null 2>&1
	find . -type f -name "*.pyc" -exec rm -rf {} + > /dev/null 2>&1
	rm -rf htmlcov
	rm -rf .coverage

.PHONY: fix
fix:
	ruff --fix fastadmin tests examples docs
	isort fastadmin tests examples docs
	black fastadmin tests examples docs
	mypy -p fastadmin -p tests -p examples -p docs
	cd frontend && make fix

.PHONY: lint
lint:
	ruff fastadmin tests examples docs
	isort --check-only fastadmin tests examples docs
	black --check --diff fastadmin tests examples docs
	mypy -p fastadmin -p tests -p examples -p docs
	cd frontend && make lint

.PHONY: test
test:
	poetry run python generate_db.py
	ADMIN_ENV_FILE=example.env poetry run pytest --cov=fastadmin --cov-report=term-missing --cov-report=xml --cov-fail-under=90 -s tests
	cd frontend && make test

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
	mv fastadmin/static/js/main*.js fastadmin/static/js/main.min.js
	mv fastadmin/static/css/main*.css fastadmin/static/css/main.min.css
	rm fastadmin/static/js/*.txt

.PHONY: install
install:
	poetry install --all-extras
	make -C frontend install


.PHONY: docs
docs:
	make -C docs build


.PHONY: build
build:
	make docs
	make -C frontend build
	make collectstatic

.PHONY: pre-commit-install
pre-commit-install:
	poetry run pip install pre-commit
	poetry run pre-commit install

.PHONY: pre-commit
pre-commit:
	poetry run pre-commit run --all-files

.PHONY: push
pre-push:
	make fix
	make lint
	make pre-commit-install
	make pre-commit
	make docs
	make build
