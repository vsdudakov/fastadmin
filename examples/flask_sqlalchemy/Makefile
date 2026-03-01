all: install run

.PHONY: run
run:
	poetry run python example.py

.PHONY: install
install:
	poetry install
	poetry run pip install -e ../..
