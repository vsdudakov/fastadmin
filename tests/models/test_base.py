import pytest

from fastadmin import ModelAdmin


async def test_not_implemented_methods():
    class Model:
        pass

    base = ModelAdmin(Model)
    with pytest.raises(NotImplementedError):
        await base.authenticate("username", "password")

    with pytest.raises(NotImplementedError):
        await base.orm_save_obj(None, {})

    with pytest.raises(NotImplementedError):
        await base.orm_delete_obj({})

    with pytest.raises(NotImplementedError):
        await base.orm_get_list()

    with pytest.raises(NotImplementedError):
        await base.orm_get_obj(0)

    with pytest.raises(NotImplementedError):
        await base.orm_get_m2m_ids({}, "test")

    with pytest.raises(NotImplementedError):
        await base.orm_save_m2m_ids({}, "test", [])

    with pytest.raises(NotImplementedError):
        await base.get_model_fields_with_widget_types()

    with pytest.raises(NotImplementedError):
        await base.get_model_pk_name(base.model_cls)


async def test_export_wrong_format(mocker):
    class Model:
        pass

    base = ModelAdmin(Model)

    mocker.patch.object(base, "orm_get_list", return_value=([], 0))
    mocker.patch.object(base, "get_model_fields_with_widget_types", return_value=[])
    await base.get_export("wrong_format") is None
