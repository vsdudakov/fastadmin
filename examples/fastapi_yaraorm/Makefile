all: install run

.PHONY: fastapi
run:
	uv run uvicorn example:app --reload --host=0.0.0.0 --port=8090

.PHONY: install
install:
	uv pip install fastadmin[fastapi] yara-orm uvicorn
	uv pip install -e ../../
