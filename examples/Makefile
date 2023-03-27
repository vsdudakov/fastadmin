.PHONY: fastapi
fastapi:
	cd .. && poetry run uvicorn examples.fastapi.dev:app --reload --host=0.0.0.0 --port=8090

.PHONY: flask
flask:
	cd .. && poetry run flask --app examples.flask.dev run --debug --host 0.0.0.0 --port 8090

.PHONY: django
django:
	cd .. && poetry run python examples/django/dev/manage.py runserver 0.0.0.0:8090


.PHONY: install
install:
	cd .. && poetry install --all-extras
