"""User-registerable custom encoders for admin API serialization.

Model field values are converted to JSON-serializable representations during
serialization (see :meth:`fastadmin.models.base.BaseModelAdmin.serialize_obj_attributes`).
Register a custom encoder to control how instances of a given type are represented
in every admin API response — e.g. a custom datetime format, an ``Enum``'s label,
or a domain value object.

Example:

.. code-block:: python

    import datetime

    from fastadmin import register_encoder

    # Render every datetime as "2024-01-31 14:05" instead of ISO 8601.
    register_encoder(datetime.datetime, lambda dt: dt.strftime("%Y-%m-%d %H:%M"))

Encoders are matched via ``isinstance`` in registration order, so register more
specific types before their base types.
"""

from collections.abc import Callable
from typing import Any

# Maps a type to a function converting an instance of that type to a JSON-serializable value.
CUSTOM_ENCODERS: dict[type, Callable[[Any], Any]] = {}


def register_encoder(type_: type, encoder: Callable[[Any], Any]) -> None:
    """Register a custom encoder for a type used across all admin API responses.

    :params type_: the type to encode (matched via ``isinstance``).
    :params encoder: a callable converting an instance to a JSON-serializable value.
    :return: None.
    """
    CUSTOM_ENCODERS[type_] = encoder


def unregister_encoder(type_: type) -> None:
    """Remove a previously registered encoder for a type (no-op if absent).

    :params type_: the type whose encoder should be removed.
    :return: None.
    """
    CUSTOM_ENCODERS.pop(type_, None)


def clear_encoders() -> None:
    """Remove all registered custom encoders.

    :return: None.
    """
    CUSTOM_ENCODERS.clear()


def apply_custom_encoders(value: Any) -> Any:
    """Return ``value`` encoded by the first matching custom encoder, else unchanged.

    Types are matched via ``isinstance`` in registration order, so a more specific
    type registered before its base type wins.

    :params value: the value to encode.
    :return: the encoded value, or the original value if no encoder matches.
    """
    for type_, encoder in CUSTOM_ENCODERS.items():
        if isinstance(value, type_):
            return encoder(value)
    return value
