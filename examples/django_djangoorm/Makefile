all: install run

.PHONY: fastapi
run:
	poetry run python manage.py migrate
	poetry run python manage.py runserver 8090

.PHONY: install
install:
	poetry install
	poetry run pip install -e ../../
