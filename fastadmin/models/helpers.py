from typing import Any

from fastadmin.models.base import BaseModelAdmin


def register_admin_model(admin_model_class: type[BaseModelAdmin], model_classes: list[Any]):
    from fastadmin.app import admin_models

    for model_class in model_classes:
        admin_models[model_class] = admin_model_class


def get_admin_models() -> dict[Any, type[BaseModelAdmin]]:
    from fastadmin.app import admin_models

    return admin_models


def get_admin_model(model_name: str) -> BaseModelAdmin | None:
    from fastadmin.app import admin_models

    for model, admin_model in admin_models.items():
        if model.__name__ == model_name:
            return admin_model(model)
    return None
