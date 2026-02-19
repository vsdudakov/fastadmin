.PHONY: fastapi
fastapi:
	poetry run uvicorn fastapi_app.dev:app --reload --host=0.0.0.0 --port=8090

.PHONY: flask
flask:
	poetry run flask --app flask_app.dev run --debug --host 0.0.0.0 --port 8090

.PHONY: django
django:
	poetry run python django/dev/manage.py runserver 0.0.0.0:8090


.PHONY: install
install:
	poetry install --all-extras
