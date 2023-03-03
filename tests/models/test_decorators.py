import pytest

from fastadmin import register, ModelAdmin

async def test_register():
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
