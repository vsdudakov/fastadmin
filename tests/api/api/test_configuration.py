from fastadmin import ModelAdmin
from fastadmin.models.helpers import get_admin_model, register_admin_model, unregister_admin_model
from fastadmin.settings import settings
from tests.api.helpers import sign_in, sign_out

LIST_EVENT_FIELDS = [
    "name",
    "tournament_id",
    "participants",
    "rating",
    "description",
    "event_type",
    "tags",
    "is_active",
    "created_at",
    "start_time",
    "date",
    "json",
]


def validate_configuration_response_data(response_data, is_auth=True):
    assert response_data
    assert response_data["site_name"] == settings.ADMIN_SITE_NAME
    assert response_data["site_sign_in_logo"] == settings.ADMIN_SITE_SIGN_IN_LOGO
    assert response_data["site_header_logo"] == settings.ADMIN_SITE_HEADER_LOGO
    assert response_data["site_favicon"] == settings.ADMIN_SITE_FAVICON
    assert response_data["primary_color"] == settings.ADMIN_PRIMARY_COLOR
    assert response_data["username_field"] == settings.ADMIN_USER_MODEL_USERNAME_FIELD
    assert response_data["date_format"] == settings.ADMIN_DATE_FORMAT
    assert response_data["datetime_format"] == settings.ADMIN_DATETIME_FORMAT

    if not is_auth:
        assert response_data["models"] == []
        return

    for model in response_data["models"]:
        model_name = model["name"]
        assert model_name
        admin_model = get_admin_model(model_name)
        assert admin_model
        assert model["name"] == admin_model.model_cls.__name__
        permissions = []
        if admin_model.has_add_permission():
            permissions.append("Add")
        if admin_model.has_change_permission():
            permissions.append("Change")
        if admin_model.has_delete_permission():
            permissions.append("Delete")
        if admin_model.has_export_permission():
            permissions.append("Export")
        assert set(model["permissions"]) == set(permissions)
        assert model["list_per_page"] == admin_model.list_per_page
        assert model["save_on_top"] == admin_model.save_on_top
        assert model["save_as"] == admin_model.save_as
        assert model["save_as_continue"] == admin_model.save_as_continue
        assert model["view_on_site"] == admin_model.view_on_site
        assert model["search_help_text"] == admin_model.search_help_text
        assert set(model["search_fields"]) == set(admin_model.search_fields)
        assert model["preserve_filters"] == admin_model.preserve_filters
        assert model["list_max_show_all"] == admin_model.list_max_show_all
        assert model["show_full_result_count"] == admin_model.show_full_result_count

        list_fields = [f for f in model["fields"] if f["list_configuration"] is not None]
        add_fields = [f for f in model["fields"] if f["add_configuration"] is not None]
        change_fields = [f for f in model["fields"] if f["change_configuration"] is not None]

        list_display = admin_model.list_display or ["id"]

        model_fields = admin_model.get_model_fields()

        for list_display_field in list_display:
            list_field = next((f for f in list_fields if f["name"] == list_display_field), None)
            if model_fields.get(list_display_field, {}).get("is_m2m"):
                assert not list_field
                continue
            assert list_field and list_field["list_configuration"]
            assert list_field["list_configuration"]["index"] == list_display.index(list_display_field)
            sorter = not admin_model.sortable_by or list_display_field in admin_model.sortable_by
            if hasattr(admin_model, list_display_field):
                sorter = False
            assert list_field["list_configuration"]["sorter"] == sorter
            assert list_field["list_configuration"]["width"] is None
            assert list_field["list_configuration"]["is_link"] == (list_display_field in admin_model.list_display_links)
            assert list_field["list_configuration"]["empty_value_display"] == admin_model.empty_value_display
            assert bool(list_field["list_configuration"]["filter_widget_type"]) == (
                list_display_field in admin_model.list_filter
            )
            assert "filter_widget_props" in list_field["list_configuration"]


async def test_configuration(objects, client):
    superuser = objects["superuser"]
    event = objects["event"]
    admin_user_cls: ModelAdmin = objects["admin_user_cls"]
    admin_event_cls: ModelAdmin = objects["admin_event_cls"]

    await sign_in(client, superuser, admin_user_cls)

    register_admin_model(admin_event_cls, [event.__class__])
    r = await client.get(
        f"/api/configuration",
    )
    assert r.status_code == 200, r.text
    response_data = r.json()
    validate_configuration_response_data(response_data)

    unregister_admin_model([event.__class__])
    await sign_out(client, superuser)


async def test_configuration_not_auth(objects, client):
    event = objects["event"]
    admin_event_cls = objects["admin_event_cls"]

    register_admin_model(admin_event_cls, [event.__class__])
    r = await client.get(
        f"/api/configuration",
    )
    assert r.status_code == 200, r.text
    response_data = r.json()
    validate_configuration_response_data(response_data, is_auth=False)

    unregister_admin_model([event.__class__])


async def test_configuration_list_display(objects, client):
    superuser = objects["superuser"]
    event = objects["event"]
    admin_user_cls = objects["admin_user_cls"]
    admin_event_cls = objects["admin_event_cls"]

    await sign_in(client, superuser, admin_user_cls)

    register_admin_model(admin_event_cls, [event.__class__])
    admin_event_cls.list_display = LIST_EVENT_FIELDS
    r = await client.get(
        f"/api/configuration",
    )
    assert r.status_code == 200, r.text
    response_data = r.json()
    assert response_data
    validate_configuration_response_data(response_data)

    admin_event_cls.list_display = ()
    unregister_admin_model([event.__class__])
    await sign_out(client, superuser)


async def test_configuration_list_display_display_fields(objects, client):
    superuser = objects["superuser"]
    event = objects["event"]
    admin_user_cls = objects["admin_user_cls"]
    admin_event_cls = objects["admin_event_cls"]

    await sign_in(client, superuser, admin_user_cls)

    register_admin_model(admin_event_cls, [event.__class__])
    admin_event_cls.list_display = ("started", "name_with_price")  # see EventAdmin display methods
    r = await client.get(
        f"/api/configuration",
    )
    assert r.status_code == 200, r.text
    response_data = r.json()
    assert response_data
    validate_configuration_response_data(response_data)

    admin_event_cls.list_display = ()
    unregister_admin_model([event.__class__])
    await sign_out(client, superuser)


async def test_configuration_list_filter(objects, client):
    superuser = objects["superuser"]
    event = objects["event"]
    admin_user_cls = objects["admin_user_cls"]
    admin_event_cls = objects["admin_event_cls"]

    await sign_in(client, superuser, admin_user_cls)

    register_admin_model(admin_event_cls, [event.__class__])
    admin_event_cls.list_display = LIST_EVENT_FIELDS
    admin_event_cls.list_filter = LIST_EVENT_FIELDS
    r = await client.get(
        f"/api/configuration",
    )
    assert r.status_code == 200, r.text
    response_data = r.json()
    assert response_data
    validate_configuration_response_data(response_data)

    admin_event_cls.list_display = ()
    admin_event_cls.list_filter = ()
    unregister_admin_model([event.__class__])
    await sign_out(client, superuser)


async def test_configuration_sortable_by(objects, client):
    superuser = objects["superuser"]
    event = objects["event"]
    admin_user_cls = objects["admin_user_cls"]
    admin_event_cls = objects["admin_event_cls"]

    await sign_in(client, superuser, admin_user_cls)

    register_admin_model(admin_event_cls, [event.__class__])
    admin_event_cls.list_display = LIST_EVENT_FIELDS
    admin_event_cls.list_filter = LIST_EVENT_FIELDS
    admin_event_cls.sortable_by = ("name",)
    r = await client.get(
        f"/api/configuration",
    )
    assert r.status_code == 200, r.text
    response_data = r.json()
    assert response_data
    validate_configuration_response_data(response_data)

    admin_event_cls.list_display = ()
    admin_event_cls.list_filter = ()
    admin_event_cls.sortable_by = ()
    unregister_admin_model([event.__class__])
    await sign_out(client, superuser)


async def test_configuration_radio_fields(objects, client):
    superuser = objects["superuser"]
    event = objects["event"]
    admin_user_cls = objects["admin_user_cls"]
    admin_event_cls = objects["admin_event_cls"]

    await sign_in(client, superuser, admin_user_cls)

    register_admin_model(admin_event_cls, [event.__class__])
    admin_event_cls.list_display = LIST_EVENT_FIELDS
    admin_event_cls.list_filter = LIST_EVENT_FIELDS
    admin_event_cls.radio_fields = ("event_type",)
    r = await client.get(
        f"/api/configuration",
    )
    assert r.status_code == 200, r.text
    response_data = r.json()
    assert response_data
    validate_configuration_response_data(response_data)

    admin_event_cls.list_display = ()
    admin_event_cls.list_filter = ()
    admin_event_cls.radio_fields = ()
    unregister_admin_model([event.__class__])
    await sign_out(client, superuser)


async def test_configuration_filter_horizontal_vertical(objects, client):
    superuser = objects["superuser"]
    event = objects["event"]
    admin_user_cls = objects["admin_user_cls"]
    admin_event_cls = objects["admin_event_cls"]

    await sign_in(client, superuser, admin_user_cls)

    register_admin_model(admin_event_cls, [event.__class__])
    admin_event_cls.list_display = LIST_EVENT_FIELDS
    admin_event_cls.list_filter = LIST_EVENT_FIELDS
    admin_event_cls.filter_horizontal = ("participants",)
    r = await client.get(
        f"/api/configuration",
    )
    assert r.status_code == 200, r.text
    response_data = r.json()
    assert response_data
    validate_configuration_response_data(response_data)

    admin_event_cls.filter_vertical = ["participants"]
    r = await client.get(
        f"/api/configuration",
    )
    assert r.status_code == 200, r.text
    response_data = r.json()
    assert response_data
    validate_configuration_response_data(response_data)

    admin_event_cls.list_display = ()
    admin_event_cls.list_filter = ()
    admin_event_cls.filter_horizontal = ()
    unregister_admin_model([event.__class__])
    await sign_out(client, superuser)


async def test_configuration_raw_id_fields(objects, client):
    superuser = objects["superuser"]
    event = objects["event"]
    admin_user_cls = objects["admin_user_cls"]
    admin_event_cls = objects["admin_event_cls"]

    await sign_in(client, superuser, admin_user_cls)

    register_admin_model(admin_event_cls, [event.__class__])
    admin_event_cls.list_display = LIST_EVENT_FIELDS
    admin_event_cls.list_filter = LIST_EVENT_FIELDS
    admin_event_cls.raw_id_fields = ("participants", "tournament_id", "base_id")
    r = await client.get(
        f"/api/configuration",
    )
    assert r.status_code == 200, r.text
    response_data = r.json()
    assert response_data
    validate_configuration_response_data(response_data)

    admin_event_cls.list_display = ()
    admin_event_cls.list_filter = ()
    admin_event_cls.raw_id_fields = ()
    unregister_admin_model([event.__class__])
    await sign_out(client, superuser)


async def test_configuration_fields(objects, client):
    superuser = objects["superuser"]
    event = objects["event"]
    admin_user_cls = objects["admin_user_cls"]
    admin_event_cls = objects["admin_event_cls"]

    await sign_in(client, superuser, admin_user_cls)

    register_admin_model(admin_event_cls, [event.__class__])
    admin_event_cls.fields = LIST_EVENT_FIELDS
    r = await client.get(
        f"/api/configuration",
    )
    assert r.status_code == 200, r.text
    response_data = r.json()
    assert response_data
    validate_configuration_response_data(response_data)

    admin_event_cls.fields = ()
    unregister_admin_model([event.__class__])
    await sign_out(client, superuser)


async def test_configuration_actions(objects, client):
    superuser = objects["superuser"]
    event = objects["event"]
    admin_user_cls = objects["admin_user_cls"]
    admin_event_cls = objects["admin_event_cls"]

    await sign_in(client, superuser, admin_user_cls)

    register_admin_model(admin_event_cls, [event.__class__])
    admin_event_cls.actions = ("make_is_active",)
    r = await client.get(
        f"/api/configuration",
    )
    assert r.status_code == 200, r.text
    response_data = r.json()
    assert response_data
    validate_configuration_response_data(response_data)

    admin_event_cls.actions = ()
    unregister_admin_model([event.__class__])
    await sign_out(client, superuser)


async def test_configuration_fieldsets(objects, client):
    superuser = objects["superuser"]
    event = objects["event"]
    admin_user_cls = objects["admin_user_cls"]
    admin_event_cls = objects["admin_event_cls"]

    await sign_in(client, superuser, admin_user_cls)

    register_admin_model(admin_event_cls, [event.__class__])
    admin_event_cls.fieldsets = [
        (None, {"fields": ("base_id", "name", "tournament_id", "participants")}),
        (
            "Types",
            {
                "classes": ("collapse",),
                "fields": ("is_active",),
            },
        ),
        (
            "Geo",
            {
                "classes": ("collapse",),
                "fields": ("latitude", "longitude"),
            },
        ),
    ]
    r = await client.get(
        f"/api/configuration",
    )
    assert r.status_code == 200, r.text
    response_data = r.json()
    assert response_data
    validate_configuration_response_data(response_data)

    admin_event_cls.fieldsets = ()
    unregister_admin_model([event.__class__])
    await sign_out(client, superuser)


async def test_configuration_inlines(objects, client):
    superuser = objects["superuser"]
    tournament = objects["tournament"]
    admin_user_cls = objects["admin_user_cls"]
    admin_tournament_cls = objects["admin_tournament_cls"]

    await sign_in(client, superuser, admin_user_cls)

    register_admin_model(admin_tournament_cls, [tournament.__class__])
    r = await client.get(
        f"/api/configuration",
    )
    assert r.status_code == 200, r.text
    response_data = r.json()
    assert response_data
    validate_configuration_response_data(response_data)

    unregister_admin_model([tournament.__class__])
    await sign_out(client, superuser)
