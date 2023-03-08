from typing import Any

from fastadmin.models.base import ModelAdmin, admin_model_classes


def register_admin_model_class(admin_model_class: type[ModelAdmin], orm_model_classes: list[Any]) -> None:
    """This method is used to register an admin model class.

    :params admin_model_class: a class of admin model.
    :params orm_model_classes: a list of orm model classes.
    :return: None.
    """
    for orm_model_class in orm_model_classes:
        admin_model_classes[orm_model_class] = admin_model_class
    return None


def unregister_admin_model_class(orm_model_classes: list[Any]) -> None:
    """This method is used to unregister an admin model class.

    :params admin_model_class: a class of admin model.
    :params orm_model_classes: a list of orm model classes.
    :return: None.
    """
    for orm_model_class in orm_model_classes:
        if orm_model_class in admin_model_classes:
            del admin_model_classes[orm_model_class]
    return None


def get_admin_model_classes() -> dict[Any, type[ModelAdmin]]:
    """This method is used to get a dict of admin model classes.

    :return: A dict of admin model classes.
    """
    return admin_model_classes


def get_admin_model(orm_model_class_name: str) -> ModelAdmin | None:
    """This method is used to get an admin model class by orm model class name.

    :params orm_model_class_name: a name of model.
    :return: An admin model class or None.
    """
    for orm_model_class, admin_model_class in admin_model_classes.items():
        if orm_model_class.__name__ == orm_model_class_name:
            return admin_model_class(orm_model_class)
    return None
