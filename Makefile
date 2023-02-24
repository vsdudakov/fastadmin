.PHONY: clean
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + > /dev/null 2>&1
	find . -type f -name "*.pyc" -exec rm -rf {} + > /dev/null 2>&1
	rm -rf htmlcov
	rm -rf .coverage

.PHONY: dev
dev:
	poetry run uvicorn fastapi_admin.main:admin_app --reload --host=0.0.0.0 --port=8090

.PHONY: fix
fix:
	poetry run black fastapi_admin
	poetry run isort fastapi_admin
	make -C frontend fix

.PHONY: lint
lint:
	poetry run flake8 --show-source fastapi_admin
	poetry run isort --check-only fastapi_admin --diff
	make -C frontend lint

.PHONY: test
test:
	poetry run pytest --cov=fastapi_admin --cov-report=term --cov-report=xml -s fastapi_admin/tests

.PHONY: kill
kill:
	kill -9 $$(lsof -t -i:8090)
	kill -9 $$(lsof -t -i:3030)

.PHONY: collectstatic
collectstatic:
	rm -rf ./fastapi_admin/static/js
	rm -rf ./fastapi_admin/static/css
	cp -rf ./frontend/build/static/js/ ./fastapi_admin/static/js/
	cp -rf ./frontend/build/static/css/ ./fastapi_admin/static/css/
	mv fastapi_admin/static/js/main*.js.map fastapi_admin/static/js/main.min.js.map
	mv fastapi_admin/static/js/main*.js fastapi_admin/static/js/main.min.js
	mv fastapi_admin/static/css/main*.css.map fastapi_admin/static/css/main.min.css.map
	mv fastapi_admin/static/css/main*.css fastapi_admin/static/css/main.min.css

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
