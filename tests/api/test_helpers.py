from fastadmin.api.helpers import sanitize


async def test_sanitize():
    assert sanitize("true") is True
    assert sanitize("false") is False
    assert sanitize("null") is None
    assert sanitize("foo") == "foo"
