from fastadmin import ModelAdmin, display
from fastadmin.models.helpers import (
    generate_models_schema,
    get_admin_model,
    get_admin_models,
    register_admin_model_class,
    unregister_admin_model_class,
)


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


async def test_admin_model_list_configuration_ordering(tournament, base_model_admin):
    Tournament = tournament.__class__

    class TournamentModelAdmin(base_model_admin):
        list_display = ("pseudo_name", "name", "another_calculated_field")

        @display
        def pseudo_name(self, obj: Tournament) -> str:
            return "Pseudo name"

        @display
        def another_calculated_field(self, obj: Tournament) -> int:
            return 0

    model_schema = generate_models_schema({Tournament: TournamentModelAdmin(Tournament)})

    assert model_schema
    assert len(model_schema) == 1

    list_display = [
        (field.list_configuration.index, field.name) for field in model_schema[0].fields if field.list_configuration
    ]
    list_display.sort()
    list_display = tuple(name for index, name in list_display)

    assert list_display == TournamentModelAdmin.list_display
