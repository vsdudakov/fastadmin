import pytest

from fastadmin import register_admin_model_class, unregister_admin_model_class
from fastadmin.models.helpers import get_admin_model
from tests.models.orms.tortoise.admins import UserModelAdmin


async def test_get_form_widget(tortoise_superuser):
    register_admin_model_class(UserModelAdmin, [tortoise_superuser.__class__])

    admin_model = get_admin_model(tortoise_superuser.__class__.__name__)
    with pytest.raises(Exception):
        admin_model.get_form_widget("invalid")

    unregister_admin_model_class([tortoise_superuser.__class__])
