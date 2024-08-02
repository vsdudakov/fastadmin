from flask import Flask

from fastadmin import flask_app as admin_app

app = Flask(__name__)

app.register_blueprint(admin_app, url_prefix="/admin")
