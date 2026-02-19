import pytest

from fastadmin import ModelAdmin, display, register


def test_display_sorter_string():
    """@display(sorter='expr') sets sorter to the given string."""

    @display(sorter="user__username")
    def author(self, obj):
        return str(obj)

    assert author.is_display is True
    assert author.sorter == "user__username"


def test_display_sorter_true():
    """@display(sorter=True) sets sorter to True."""

    @display(sorter=True)
    def user__username(self, obj):
        return str(obj)

    assert user__username.is_display is True
    assert user__username.sorter is True


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
