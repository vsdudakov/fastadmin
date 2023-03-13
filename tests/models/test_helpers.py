from fastadmin import ModelAdmin
from fastadmin.models.helpers import get_admin_model, register_admin_model_class, unregister_admin_model_class


async def test_uregister_admin_model_class():
    class AdminModelClass(ModelAdmin):
        pass

    class OrmModelClass:
        pass

    register_admin_model_class(AdminModelClass, [OrmModelClass])
    assert get_admin_model(OrmModelClass.__name__)
    assert get_admin_model(OrmModelClass)
    unregister_admin_model_class([OrmModelClass])
    assert not get_admin_model(OrmModelClass.__name__)
    assert not get_admin_model(OrmModelClass)
