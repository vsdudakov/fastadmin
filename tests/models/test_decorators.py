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

    with pytest.raises(ValueError):
        register()(MyModelAdmin)

    with pytest.raises(ValueError):
        register(Model)(InvalidModelAdmin)
