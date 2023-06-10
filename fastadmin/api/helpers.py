import base64
import binascii
from uuid import UUID

from fastadmin.models.schemas import ModelFieldWidgetSchema


def sanitize_filter_value(value: str) -> bool | None | str:
    """Sanitize value

    :params value: a value.
    :return: A sanitized value.
    """
    match value:
        case "false":
            return False
        case "true":
            return True
        case "null":
            return None
        case _:
            return value


def sanitize_filter_key(key: str, fields: list[ModelFieldWidgetSchema]) -> tuple[str, str]:
    """Sanitize key.

    :param key: A key.
    :param fields: A list of fields.
    :return: A tuple of sanitized key and condition.
    """
    if "__" not in key:
        key = f"{key}__exact"
    field_name = key.split("__", 1)[0]
    condition = key.split("__", 1)[1]
    field: ModelFieldWidgetSchema | None = next((field for field in fields if field.name == field_name), None)
    if field and field.filter_widget_props.get("parentModel") and not field.is_m2m:
        field_name = f"{field_name}_id"
    return field_name, condition


def is_valid_uuid(uuid_to_test: str) -> bool:
    """Check if uuid_to_test is a valid uuid.

    :param uuid_to_test: A uuid to test.
    :return: True if uuid_to_test is a valid uuid, False otherwise.
    """
    try:
        uuid_obj = UUID(uuid_to_test)
    except ValueError:
        return False
    return str(uuid_obj) == uuid_to_test


def is_digit(digit_to_test: str) -> bool:
    """Check if digit_to_test is a digit.

    :param digit_to_test: A digit to test.
    :return: True if digit_to_test is a digit, False otherwise.
    """
    try:
        int(digit_to_test)
    except ValueError:
        return False
    return True


def is_valid_id(id: UUID | int) -> bool:
    """Check if id is a valid id.

    :param id: An id to test.
    :return: True if id is a valid id, False otherwise.
    """
    return is_digit(str(id)) or is_valid_uuid(str(id))


def is_valid_base64(value: str) -> bool:
    """Check if s is a valid base64.

    :param s: A string to test.
    :return: True if s is a valid base64, False otherwise.
    """
    try:
        base64.decodebytes(value.encode("ascii"))
        return True
    except binascii.Error:
        return False
