.PHONY: clean
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + > /dev/null 2>&1
	find . -type f -name "*.pyc" -exec rm -rf {} + > /dev/null 2>&1
	rm -rf htmlcov
	rm -rf .coverage

.PHONY: dev
dev:
	poetry run uvicorn main:admin_app --reload --host=0.0.0.0 --port=8090

.PHONY: fix
fix:
	poetry run black .
	poetry run isort .
	make -C frontend fix

.PHONY: lint
lint:
	poetry run flake8 --show-source .
	poetry run isort --check-only . --diff
	make -C frontend lint

.PHONY: test
test:
	poetry run pytest --cov=. --cov-report=term --cov-report=xml -s .

.PHONY: kill
kill:
	kill -9 $$(lsof -t -i:8090)
	kill -9 $$(lsof -t -i:3030)

.PHONY: build
build:
	make -C frontend build
