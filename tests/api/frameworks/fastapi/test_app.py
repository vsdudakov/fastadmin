from fastadmin.api.frameworks.fastapi.app import exception_handler


async def test_exception_handler():
    assert await exception_handler(None, Exception("Test")) is not None
