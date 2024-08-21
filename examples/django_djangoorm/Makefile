all: install run

.PHONY: fastapi
run:
	poetry run python manage.py migrate
	poetry run python manage.py runserver

.PHONY: install
install:
	poetry install
