from pathlib import Path
from uuid import UUID

from fastadmin.models.schemas import ModelFieldWidgetSchema, WidgetType

# Text-like filter widgets whose values are free-form strings. For these the
# literals "true"/"false"/"null" are legitimate content and must NOT be coerced
# to bool/None (otherwise a Char column can never be filtered for those words).
TEXT_FILTER_WIDGET_TYPES = frozenset(
    {
        WidgetType.Input,
        WidgetType.TextArea,
        WidgetType.RichTextArea,
        WidgetType.JsonTextArea,
        WidgetType.SlugInput,
        WidgetType.EmailInput,
        WidgetType.PhoneInput,
        WidgetType.UrlInput,
        WidgetType.PasswordInput,
    }
)


def sanitize_filter_value(
    value: str | list,
    field: ModelFieldWidgetSchema | None = None,
) -> bool | None | str | list:
    """Sanitize value (string or list for __in filters).

    :params value: a value (str or list of str for __in).
    :params field: the field being filtered, used to decide whether the
        "true"/"false"/"null" literals should be coerced (skipped for text fields).
    :return: A sanitized value.
    """
    if isinstance(value, list):
        return [sanitize_filter_value(v, field) for v in value]
    if field is not None and field.filter_widget_type in TEXT_FILTER_WIDGET_TYPES:
        return value
    match value:
        case "false":
            return False
        case "true":
            return True
        case "null":
            return None
        case _:
            return value


def parse_list_filters_from_query_params(keys_fn, getlist_fn, exclude: set[str]) -> dict[str, str | list[str]]:
    """Build filters dict from query params, supporting __in as list (comma-separated or repeated keys).

    :param keys_fn: Callable that returns param keys (e.g. request.query_params.keys).
    :param getlist_fn: Callable(key) that returns list of values (e.g. request.query_params.getlist).
    :param exclude: Keys to skip (e.g. search, sort_by, offset, limit).
    :return: Dict mapping param key to str or list[str] for __in params.
    """
    result: dict[str, str | list[str]] = {}
    for key in keys_fn():
        if key in exclude:
            continue
        values = getlist_fn(key)
        if not values:
            continue
        if key.endswith("__in"):
            if len(values) == 1 and "," in values[0]:
                result[key] = [x.strip() for x in values[0].split(",") if x.strip()]
            else:
                result[key] = values
        else:
            result[key] = values[0]
    return result


def sanitize_filter_key(key: str, fields: list[ModelFieldWidgetSchema]) -> tuple[str, str]:
    """Sanitize key.

    :param key: A key.
    :param fields: A list of fields.
    :return: A tuple of sanitized key and condition.
    """
    if "__" not in key:
        key += "__exact"
    field_name, _, condition = key.partition("__")
    field: ModelFieldWidgetSchema | None = next((field for field in fields if field.name == field_name), None)
    if field and field.filter_widget_props.get("parentModel") and not field.is_m2m:
        field_name += "_id"
    return field_name, condition


def build_query_filters(
    filters: dict,
    fields: list[ModelFieldWidgetSchema],
    exclude: tuple[str, ...],
) -> dict[tuple[str, str], bool | None | str | list]:
    """Build the sanitized ``{(field_name, condition): value}`` filter dict.

    Resolves each key's field so value coercion (true/false/null) can be applied
    in a type-aware way (see :func:`sanitize_filter_value`).

    :param filters: raw filters mapping ``key -> value``.
    :param fields: model fields with widget types.
    :param exclude: keys to skip (search, sort_by, offset, limit).
    :return: sanitized filters dict.
    """
    result: dict[tuple[str, str], bool | None | str | list] = {}
    for key, value in filters.items():
        if key in exclude:
            continue
        field_name = key.partition("__")[0]
        field = next((f for f in fields if f.name == field_name), None)
        result[sanitize_filter_key(key, fields)] = sanitize_filter_value(value, field)
    return result


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


def is_valid_id(id: UUID | int | str) -> bool:
    """Check if id is a valid id.

    :param id: An id to test (UUID, int, or string PK).
    :return: True if id is a valid id, False otherwise.
    """
    if isinstance(id, str):
        # Any non-empty string is a valid PK (UUID, numeric, or opaque string PK).
        return bool(id)
    if is_valid_uuid(str(id)):
        return True
    try:
        int(id)
        return True
    except (ValueError, TypeError):
        pass
    return False


def get_template(template: Path, context: dict) -> str:
    with template.open("r") as file:
        content = file.read()
        for key, value in context.items():
            content = content.replace(f"{{{{{key}}}}}", str(value))
        return content
