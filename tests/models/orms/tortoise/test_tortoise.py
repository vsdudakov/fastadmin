import pytest

from fastadmin import register_admin_model_class, unregister_admin_model_class
from fastadmin.models.helpers import get_admin_model


async def test_get_form_widget(tortoise_superuser):
    admin_model = get_admin_model(tortoise_superuser.__class__.__name__)
    with pytest.raises(Exception):
        admin_model.get_form_widget("invalid")
