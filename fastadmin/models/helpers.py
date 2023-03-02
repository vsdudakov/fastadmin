from typing import Any

from fastadmin.models.base import BaseModelAdmin


def register_admin_model(admin_model_class: type[BaseModelAdmin], model_classes: list[Any]):
    """This method is used to register an admin model.

    :params admin_model_class: a class of admin model.
    :params model_classes: a list of model classes.
    :return: None.
    """
    from fastadmin.app import admin_models

    for model_class in model_classes:
        admin_models[model_class] = admin_model_class


def get_admin_models() -> dict[Any, type[BaseModelAdmin]]:
    """This method is used to get a dict of admin models.

    :return: A dict of admin models.
    """
    from fastadmin.app import admin_models

    return admin_models


def get_admin_model(model_name: str) -> BaseModelAdmin | None:
    """This method is used to get an admin model by model name.

    :params model_name: a name of model.
    :return: An admin model or None.
    """
    from fastadmin.app import admin_models

    for model, admin_model in admin_models.items():
        if model.__name__ == model_name:
            return admin_model(model)
    return None
