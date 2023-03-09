from flask import Flask

from fastadmin import flask_app as admin_app
from fastadmin.settings import settings

app = Flask(__name__)
app.register_blueprint(admin_app, url_prefix=f"/{settings.ADMIN_PREFIX}")
