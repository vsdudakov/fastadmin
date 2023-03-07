from fastadmin.fastapi import unicorn_exception_handler


async def test_unicorn_exception_handler():
    assert await unicorn_exception_handler(None, Exception("Test")) is not None
