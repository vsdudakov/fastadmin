# api
import logging

try:
    from fastadmin.api.frameworks.django.app.urls import get_admin_urls as get_django_admin_urls
except ModuleNotFoundError:  # pragma: no cover
    logging.info("Django not installed")  # pragma: no cover

try:
    from fastadmin.api.frameworks.fastapi.app import app as fastapi_app
except ModuleNotFoundError:  # pragma: no cover
    logging.info("FastAPI not installed")  # pragma: no cover

try:
    from fastadmin.api.frameworks.flask.app import app as flask_app
except ModuleNotFoundError:  # pragma: no cover
    logging.info("Flask not installed")  # pragma: no cover

# models
from fastadmin.models.base import InlineModelAdmin, ModelAdmin
from fastadmin.models.decorators import action, display, register
from fastadmin.models.helpers import register_admin_model_class, unregister_admin_model_class
from fastadmin.models.orms.django import DjangoInlineModelAdmin, DjangoModelAdmin

# orms
from fastadmin.models.orms.ponyorm import PonyORMInlineModelAdmin, PonyORMModelAdmin
from fastadmin.models.orms.sqlalchemy import SqlAlchemyInlineModelAdmin, SqlAlchemyModelAdmin
from fastadmin.models.orms.tortoise import TortoiseInlineModelAdmin, TortoiseModelAdmin
