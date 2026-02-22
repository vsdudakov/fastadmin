all: install run

.PHONY: fastapi
run:
	poetry run uvicorn example:app --reload --host=0.0.0.0 --port=8090

.PHONY: install
install:
	poetry install
	poetry run pip install -e ../../
