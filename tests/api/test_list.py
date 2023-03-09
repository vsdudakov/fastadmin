from fastadmin import register_admin_model_class, unregister_admin_model_class
from tests.api.helpers import sign_in, sign_out
from tests.models.orms.tortoise.admins import EventModelAdmin


async def test_list(superuser, event, client):
    await sign_in(client, superuser)
    register_admin_model_class(EventModelAdmin, [event.__class__])
    r = await client.get(
        f"/api/list/{event.__class__.__name__}",
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert data
    assert data["total"] == 1
    item = data["results"][0]
    assert item["id"] == event.id
    assert item["name"] == event.name
    assert item["tournament_id"] == event.tournament_id
    assert item["created_at"] == event.created_at.isoformat()
    assert item["updated_at"] == event.updated_at.isoformat()
    assert "participants" not in item  # no m2m2 fields on list

    unregister_admin_model_class([event.__class__])
    await sign_out(client, superuser)


async def test_list_filters(superuser, event, client):
    await sign_in(client, superuser)
    register_admin_model_class(EventModelAdmin, [event.__class__])
    r = await client.get(
        f"/api/list/{event.__class__.__name__}?name__icontains={event.name[:2]}",
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert data
    assert data["total"] == 1
    item = data["results"][0]
    assert item["id"] == event.id

    r = await client.get(
        f"/api/list/{event.__class__.__name__}?name__icontains=invalid",
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert data
    assert data["total"] == 0

    r = await client.get(
        f"/api/list/{event.__class__.__name__}?invalid__icontains={event.name[:2]}",
    )
    assert r.status_code == 422, r.text

    unregister_admin_model_class([event.__class__])
    await sign_out(client, superuser)


async def test_list_search(superuser, event, client):
    await sign_in(client, superuser)
    register_admin_model_class(EventModelAdmin, [event.__class__])

    EventModelAdmin.search_fields = ["name"]
    r = await client.get(
        f"/api/list/{event.__class__.__name__}?search={event.name[:2]}",
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert data
    assert data["total"] == 1
    item = data["results"][0]
    assert item["id"] == event.id

    r = await client.get(
        f"/api/list/{event.__class__.__name__}?search=invalid",
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert data
    assert data["total"] == 0

    EventModelAdmin.search_fields = ["invalid"]
    r = await client.get(
        f"/api/list/{event.__class__.__name__}?search={event.name[:2]}",
    )
    assert r.status_code == 422, r.text

    EventModelAdmin.search_fields = ()
    unregister_admin_model_class([event.__class__])
    await sign_out(client, superuser)


async def test_list_sort_by(superuser, event, client):
    await sign_in(client, superuser)
    register_admin_model_class(EventModelAdmin, [event.__class__])

    r = await client.get(
        f"/api/list/{event.__class__.__name__}?sort_by=-name",
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert data
    assert data["total"] == 1

    r = await client.get(
        f"/api/list/{event.__class__.__name__}?sort_by=invalid",
    )
    assert r.status_code == 422, r.text

    EventModelAdmin.ordering = ["name"]
    r = await client.get(
        f"/api/list/{event.__class__.__name__}",
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert data
    assert data["total"] == 1

    EventModelAdmin.ordering = ["invalid"]
    r = await client.get(
        f"/api/list/{event.__class__.__name__}",
    )
    assert r.status_code == 422, r.text

    EventModelAdmin.ordering = ()
    unregister_admin_model_class([event.__class__])
    await sign_out(client, superuser)


async def test_list_select_related(superuser, event, client):
    await sign_in(client, superuser)
    register_admin_model_class(EventModelAdmin, [event.__class__])

    EventModelAdmin.list_select_related = ["tournament_id"]
    r = await client.get(
        f"/api/list/{event.__class__.__name__}",
    )
    assert r.status_code == 200, r.text

    EventModelAdmin.list_select_related = ["invalid"]
    r = await client.get(
        f"/api/list/{event.__class__.__name__}",
    )
    assert r.status_code == 422, r.text

    EventModelAdmin.list_select_related = ()
    unregister_admin_model_class([event.__class__])
    await sign_out(client, superuser)


async def test_list_display_fields(superuser, event, client):
    await sign_in(client, superuser)
    register_admin_model_class(EventModelAdmin, [event.__class__])

    EventModelAdmin.list_display = ["started", "name_with_price"]
    r = await client.get(
        f"/api/list/{event.__class__.__name__}",
    )
    assert r.status_code == 200, r.text

    EventModelAdmin.list_display = ["invalid"]
    r = await client.get(
        f"/api/list/{event.__class__.__name__}",
    )
    assert r.status_code == 200, r.text

    EventModelAdmin.list_display = ()
    unregister_admin_model_class([event.__class__])
    await sign_out(client, superuser)


async def test_list_401(superuser, event, client):
    event = event
    r = await client.get(
        f"/api/list/{event.__class__.__name__}",
    )
    assert r.status_code == 401, r.text


async def test_list_404(superuser, event, client):
    unregister_admin_model_class([event.__class__])
    await sign_in(client, superuser)
    r = await client.get(
        f"/api/list/{event.__class__.__name__}",
    )
    assert r.status_code == 404, r.text
    await sign_out(client, superuser)
