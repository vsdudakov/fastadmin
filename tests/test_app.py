from fastadmin.api.fastapi.app import admin_model_exception_handler, exception_handler
from fastadmin.models.exceptions import AdminModelException


async def test_exception_handler():
    assert await exception_handler(None, Exception("Test")) is not None


async def test_admin_model_exception_handler():
    assert await admin_model_exception_handler(None, AdminModelException("Test")) is not None
