def sanitize(value: str) -> bool | None | str:
    """Sanitize value

    :params value: a value.
    :return: A sanitized value.
    """
    if value == "false":
        return False
    elif value == "true":
        return True
    elif value == "null":
        return None
    return value
