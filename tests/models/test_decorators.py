import pytest

from fastadmin import ModelAdmin, register


async def test_register():
    class Model:
        pass

    class MyModelAdmin(ModelAdmin):
        pass

    assert register(Model)(MyModelAdmin)


async def test_register_error():
    class Model:
        pass

    class InvalidModelAdmin:
        pass

    class MyModelAdmin(ModelAdmin):
        pass

    with pytest.raises(ValueError, match="At least one model must be passed to register."):
        register()(MyModelAdmin)

    with pytest.raises(ValueError, match="Wrapped class must subclass ModelAdmin."):
        register(Model)(InvalidModelAdmin)
