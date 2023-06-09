# api
import logging

try:
    from fastadmin.api.frameworks.django.app.urls import get_admin_urls as get_django_admin_urls  # noqa: F401
    from fastadmin.models.orms.django import DjangoInlineModelAdmin, DjangoModelAdmin  # noqa: F401
except ModuleNotFoundError:  # pragma: no cover
    logging.info("Django is not installed")  # pragma: no cover

try:
    from fastadmin.api.frameworks.fastapi.app import app as fastapi_app  # noqa: F401
except ModuleNotFoundError:  # pragma: no cover
    logging.info("FastAPI is not installed")  # pragma: no cover

try:
    from fastadmin.api.frameworks.flask.app import app as flask_app  # noqa: F401
except ModuleNotFoundError:  # pragma: no cover
    logging.info("Flask is not installed")  # pragma: no cover

try:
    from fastadmin.models.orms.ponyorm import PonyORMInlineModelAdmin, PonyORMModelAdmin  # noqa: F401
except ModuleNotFoundError:  # pragma: no cover
    logging.info("PonyORM is not installed")  # pragma: no cover

try:
    from fastadmin.models.orms.sqlalchemy import SqlAlchemyInlineModelAdmin, SqlAlchemyModelAdmin  # noqa: F401
except ModuleNotFoundError:  # pragma: no cover
    logging.info("SQLAlchemy is not installed")  # pragma: no cover

try:
    from fastadmin.models.orms.tortoise import TortoiseInlineModelAdmin, TortoiseModelAdmin  # noqa: F401
except ModuleNotFoundError:  # pragma: no cover
    logging.info("TortoiseORM is not installed")  # pragma: no cover

# models
from fastadmin.models.base import DashboardWidgetAdmin, InlineModelAdmin, ModelAdmin  # noqa: F401
from fastadmin.models.decorators import action, display, register, register_widget  # noqa: F401
from fastadmin.models.helpers import register_admin_model_class, unregister_admin_model_class  # noqa: F401
from fastadmin.models.schemas import DashboardWidgetType, WidgetType  # noqa: F401
