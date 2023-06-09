from fastadmin.models.helpers import get_admin_model
from fastadmin.settings import settings

LIST_EVENT_FIELDS = [
    "name",
    "tournament",
    "participants",
    "rating",
    "description",
    "event_type",
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
        assert model["name"] == admin_model.model_cls.get_model_name()
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
        # add_fields = [f for f in model["fields"] if f["add_configuration"] is not None]
        # change_fields = [f for f in model["fields"] if f["change_configuration"] is not None]

        list_display = admin_model.list_display or ["id"]

        model_fields = admin_model.get_model_fields_with_widget_types()
        fields_for_serialize = admin_model.get_fields_for_serialize()

        # check list_configuration
        for model_field in model_fields:
            list_field = next((f for f in list_fields if f["name"] == model_field.name), None)
            if model_field.is_m2m:
                assert not list_field
                continue
            if model_field.name not in fields_for_serialize:
                assert not list_field
                continue
            if model_field.name not in list_display:
                assert not list_field
                continue
            assert list_field, model_field.name
            assert list_field["list_configuration"], model_field.name
            assert list_field["list_configuration"]["index"] == list_display.index(model_field.name)
            sorter = not admin_model.sortable_by or model_field.name in admin_model.sortable_by
            if hasattr(admin_model, model_field.name):
                sorter = False
            assert list_field["list_configuration"]["sorter"] == sorter
            assert list_field["list_configuration"]["width"] is None
            assert list_field["list_configuration"]["is_link"] == (model_field.name in admin_model.list_display_links)
            assert list_field["list_configuration"]["empty_value_display"] == admin_model.empty_value_display
            assert bool(list_field["list_configuration"]["filter_widget_type"]) == (
                model_field.name in admin_model.list_filter
            )
            assert "filter_widget_props" in list_field["list_configuration"]


async def test_configuration(session_id, event, client):
    assert session_id

    r = await client.get(
        "/api/configuration",
    )
    assert r.status_code == 200, r.text
    response_data = r.json()
    validate_configuration_response_data(response_data)


async def test_configuration_405(session_id, client):
    assert session_id
    r = await client.post(
        "/api/configuration",
    )
    assert r.status_code == 405, r.text


async def test_configuration_not_auth(client):
    r = await client.get(
        "/api/configuration",
    )
    assert r.status_code == 200, r.text
    response_data = r.json()
    validate_configuration_response_data(response_data, is_auth=False)


async def test_configuration_list_display(session_id, admin_models, event, client):
    assert session_id
    event_admin_model = admin_models[event.__class__]

    event_admin_model.list_display = LIST_EVENT_FIELDS
    r = await client.get(
        "/api/configuration",
    )
    assert r.status_code == 200, r.text
    response_data = r.json()
    assert response_data
    validate_configuration_response_data(response_data)


async def test_configuration_list_display_display_fields(session_id, admin_models, event, client):
    assert session_id
    event_admin_model = admin_models[event.__class__]

    event_admin_model.list_display = ("started", "name_with_price")  # see EventAdmin display methods
    r = await client.get(
        "/api/configuration",
    )
    assert r.status_code == 200, r.text
    response_data = r.json()
    assert response_data
    validate_configuration_response_data(response_data)


async def test_configuration_list_filter(session_id, admin_models, event, client):
    assert session_id
    event_admin_model = admin_models[event.__class__]

    event_admin_model.list_display = LIST_EVENT_FIELDS
    event_admin_model.list_filter = LIST_EVENT_FIELDS
    r = await client.get(
        "/api/configuration",
    )
    assert r.status_code == 200, r.text
    response_data = r.json()
    assert response_data
    validate_configuration_response_data(response_data)


async def test_configuration_sortable_by(session_id, admin_models, event, client):
    assert session_id
    event_admin_model = admin_models[event.__class__]

    event_admin_model.list_display = LIST_EVENT_FIELDS
    event_admin_model.list_filter = LIST_EVENT_FIELDS
    event_admin_model.sortable_by = ("name",)
    r = await client.get(
        "/api/configuration",
    )
    assert r.status_code == 200, r.text
    response_data = r.json()
    assert response_data
    validate_configuration_response_data(response_data)


async def test_configuration_radio_fields(session_id, admin_models, event, client):
    assert session_id
    event_admin_model = admin_models[event.__class__]

    event_admin_model.list_display = LIST_EVENT_FIELDS
    event_admin_model.list_filter = LIST_EVENT_FIELDS
    event_admin_model.radio_fields = ("event_type",)
    r = await client.get(
        "/api/configuration",
    )
    assert r.status_code == 200, r.text
    response_data = r.json()
    assert response_data
    validate_configuration_response_data(response_data)


async def test_configuration_filter_horizontal_vertical(session_id, admin_models, event, client):
    assert session_id
    event_admin_model = admin_models[event.__class__]

    event_admin_model.list_display = LIST_EVENT_FIELDS
    event_admin_model.list_filter = LIST_EVENT_FIELDS
    event_admin_model.filter_horizontal = ("participants",)
    r = await client.get(
        "/api/configuration",
    )
    assert r.status_code == 200, r.text
    response_data = r.json()
    assert response_data
    validate_configuration_response_data(response_data)

    event_admin_model.filter_vertical = ["participants"]
    r = await client.get(
        "/api/configuration",
    )
    assert r.status_code == 200, r.text
    response_data = r.json()
    assert response_data
    validate_configuration_response_data(response_data)


async def test_configuration_raw_id_fields(session_id, admin_models, event, client):
    assert session_id
    event_admin_model = admin_models[event.__class__]

    event_admin_model.list_display = LIST_EVENT_FIELDS
    event_admin_model.list_filter = LIST_EVENT_FIELDS
    event_admin_model.raw_id_fields = ("participants", "tournament", "base")
    r = await client.get(
        "/api/configuration",
    )
    assert r.status_code == 200, r.text
    response_data = r.json()
    assert response_data
    validate_configuration_response_data(response_data)


async def test_configuration_fields(session_id, admin_models, event, client):
    assert session_id
    event_admin_model = admin_models[event.__class__]

    event_admin_model.fields = LIST_EVENT_FIELDS
    r = await client.get(
        "/api/configuration",
    )
    assert r.status_code == 200, r.text
    response_data = r.json()
    assert response_data
    validate_configuration_response_data(response_data)


async def test_configuration_actions(session_id, admin_models, event, client):
    assert session_id
    event_admin_model = admin_models[event.__class__]

    event_admin_model.actions = ("make_is_active",)
    r = await client.get(
        "/api/configuration",
    )
    assert r.status_code == 200, r.text
    response_data = r.json()
    assert response_data
    validate_configuration_response_data(response_data)

    event_admin_model.actions = ("test_action",)
    r = await client.get(
        "/api/configuration",
    )
    assert r.status_code == 200, r.text
    response_data = r.json()
    assert response_data
    validate_configuration_response_data(response_data)


async def test_configuration_fieldsets(session_id, admin_models, event, client):
    assert session_id
    event_admin_model = admin_models[event.__class__]

    event_admin_model.fieldsets = [
        (None, {"fields": ("base", "name", "tournament", "participants")}),
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
        "/api/configuration",
    )
    assert r.status_code == 200, r.text
    response_data = r.json()
    assert response_data
    validate_configuration_response_data(response_data)


async def test_configuration_inlines(session_id, client):
    assert session_id

    r = await client.get(
        "/api/configuration",
    )
    assert r.status_code == 200, r.text
    response_data = r.json()
    assert response_data
    validate_configuration_response_data(response_data)
