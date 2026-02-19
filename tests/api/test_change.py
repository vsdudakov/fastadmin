import datetime

from fastadmin.models.base import ModelAdmin
from fastadmin.models.helpers import get_admin_model
from fastadmin.models.schemas import ModelFieldWidgetSchema


async def test_change(session_id, admin_models, event, client):
    assert session_id
    event_admin_model: ModelAdmin = admin_models[event.__class__]
    fields = event_admin_model.get_model_fields_with_widget_types()

    participants_field: ModelFieldWidgetSchema = next((f for f in fields if f.name == "participants"), None)
    assert participants_field

    participants_model_cls_name = participants_field.form_widget_props["parentModel"]
    participants_model = f"{event_admin_model.model_name_prefix}.{participants_model_cls_name}"
    participants_admin_model = get_admin_model(participants_model)
    participant = await participants_admin_model.save_model(None, {"username": "participant", "password": "test"})

    r = await client.patch(
        f"/api/change/{event.get_model_name()}/{event.id}",
        json={
            "name": "new name",
            "participants": [participant["id"]],
            "rating": 10,
            "description": "test",
            "event_type": "PRIVATE",
            "is_active": True,
            # start_time omitted: test DBs use SQLite which has limited datetime.time support
            "date": datetime.datetime.now(tz=datetime.UTC).isoformat(),
            "latitude": 0.2,
            "longitude": 0.4,
            "price": "20.3",
            "json": {"test": "test"},
        },
    )

    assert r.status_code == 200, r.text

    updated_event = await event_admin_model.get_obj(event.id)
    item = r.json()
    assert item["id"] == updated_event["id"]
    assert item["name"] == updated_event["name"]
    assert item["tournament"] == updated_event["tournament"]
    assert datetime.datetime.fromisoformat(item["created_at"]) == updated_event["created_at"]
    assert datetime.datetime.fromisoformat(item["updated_at"]) == updated_event["updated_at"]
    assert item["participants"] == [participant["id"]]

    r = await client.delete(f"/api/delete/{participants_model}/{participant['id']}")
    assert r.status_code == 200, r.text


async def test_change_empty_m2m(session_id, admin_models, event, client):
    assert session_id
    event_admin_model: ModelAdmin = admin_models[event.__class__]

    r = await client.patch(
        f"/api/change/{event.get_model_name()}/{event.id}",
        json={
            "name": "new name",
            "participants": [],
            "rating": 10,
            "description": "test",
            "event_type": "PRIVATE",
            "is_active": True,
            # start_time omitted: test DBs use SQLite which has limited datetime.time support
            "date": datetime.datetime.now(tz=datetime.UTC).isoformat(),
            "latitude": 0.2,
            "longitude": 0.4,
            "price": "20.3",
            "json": {"test": "test"},
        },
    )

    assert r.status_code == 200, r.text

    updated_event = await event_admin_model.get_obj(event.id)
    item = r.json()
    assert item["id"] == updated_event["id"]
    assert item["name"] == updated_event["name"]
    assert item["tournament"] == updated_event["tournament"]
    assert datetime.datetime.fromisoformat(item["created_at"]) == updated_event["created_at"]
    assert datetime.datetime.fromisoformat(item["updated_at"]) == updated_event["updated_at"]
    assert item["participants"] == []


async def test_change_405(session_id, event, client):
    assert session_id
    r = await client.get(
        f"/api/change/{event.get_model_name()}/{event.id}",
    )
    assert r.status_code == 405, r.text


async def test_change_401(superuser, event, client):
    r = await client.patch(
        f"/api/change/{event.get_model_name()}/{event.id}",
        json={
            "name": "new name",
            "participants": [superuser.id],
        },
    )
    assert r.status_code == 401, r.text


async def test_change_404_admin_class_found(session_id, admin_models, superuser, event, client):
    assert session_id
    del admin_models[event.__class__]
    r = await client.patch(
        f"/api/change/{event.get_model_name()}/{event.id}",
        json={
            "name": "new name",
            "participants": [superuser.id],
        },
    )
    assert r.status_code == 404, r.text


async def test_change_404_obj_not_found(session_id, superuser, event, client):
    assert session_id
    # "invalid" is valid as string PK; lookup fails → 404
    r = await client.patch(
        f"/api/change/{event.get_model_name()}/invalid",
        json={
            "name": "new name",
            "participants": [superuser.id],
        },
    )
    assert r.status_code == 404, r.text

    r = await client.patch(
        f"/api/change/{event.get_model_name()}/-1",
        json={
            "name": "new name",
            "participants": [superuser.id],
        },
    )
    assert r.status_code == 404, r.text
