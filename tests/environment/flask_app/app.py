from flask import Flask

from fastadmin import flask_app as admin_app
from fastadmin.api.frameworks.flask.app import JSONProvider
from fastadmin.settings import settings

app = Flask(__name__)
# TODO: works only here not on blueprint
app.json = JSONProvider(app)
app.register_blueprint(admin_app, url_prefix=f"/{settings.ADMIN_PREFIX}")
