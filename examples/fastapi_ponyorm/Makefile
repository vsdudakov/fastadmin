all: install run

.PHONY: fastapi
run:
	poetry run fastapi dev --reload --port=8090 example.py

.PHONY: install
install:
	poetry install
