from datetime import datetime, timezone


async def test_list(session_id, event, client):
    assert session_id

    r = await client.get(
        f"/api/list/{event.get_model_name()}?limit=1000",
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert data
    assert data["total"] > 0
    item = next((result for result in data["results"] if str(result["id"]) == str(event.id)), None)
    assert item
    assert item["id"] == event.id
    assert item["name"] == event.name
    assert item["tournament"] == event.tournament_id if hasattr(event, "tournament_id") else event.tournament
    created_at = datetime.fromisoformat(item["created_at"])
    updated_at = datetime.fromisoformat(item["updated_at"])
    assert created_at.replace(tzinfo=timezone.utc) == event.created_at.replace(tzinfo=timezone.utc)
    assert updated_at.replace(tzinfo=timezone.utc) == event.updated_at.replace(tzinfo=timezone.utc)
    assert "participants" not in item  # no m2m fields on list


async def test_list_filters(session_id, event, client):
    assert session_id

    r = await client.get(
        f"/api/list/{event.get_model_name()}?name__icontains={event.name[:2]}",
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert data
    assert data["total"] > 0
    item = next((result for result in data["results"] if str(result["id"]) == str(event.id)), None)
    assert item
    assert item["id"] == event.id

    r = await client.get(
        f"/api/list/{event.get_model_name()}?name__icontains=invalid",
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert data
    assert data["total"] == 0

    r = await client.get(
        f"/api/list/{event.get_model_name()}?invalid__icontains={event.name[:2]}",
    )
    assert r.status_code == 422, r.text

    r = await client.get(
        f"/api/list/{event.get_model_name()}?tournament=-1",
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert data
    assert data["total"] == 0

    r = await client.get(
        f"/api/list/{event.get_model_name()}?tournament={event.tournament_id if hasattr(event, 'tournament_id') else event.tournament.id}",
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert data
    assert data["total"] > 0


async def test_list_search(session_id, admin_models, event, client):
    assert session_id

    event_admin_model = admin_models[event.__class__]

    event_admin_model.search_fields = ["name"]
    r = await client.get(
        f"/api/list/{event.get_model_name()}?search={event.name[:2]}",
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert data
    assert data["total"] > 0
    item = next((result for result in data["results"] if str(result["id"]) == str(event.id)), None)
    assert item
    assert item["id"] == event.id

    r = await client.get(
        f"/api/list/{event.get_model_name()}?search=invalid",
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert data
    assert data["total"] == 0

    event_admin_model.search_fields = ["invalid"]
    r = await client.get(
        f"/api/list/{event.get_model_name()}?search={event.name[:2]}",
    )
    assert r.status_code == 422, r.text


async def test_list_sort_by(session_id, admin_models, event, client):
    assert session_id

    event_admin_model = admin_models[event.__class__]

    r = await client.get(
        f"/api/list/{event.get_model_name()}?sort_by=-name&limit=1000",
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert data
    assert data["total"] > 0
    item = next((result for result in data["results"] if str(result["id"]) == str(event.id)), None)
    assert item

    r = await client.get(
        f"/api/list/{event.get_model_name()}?sort_by=invalid",
    )
    assert r.status_code == 422, r.text

    event_admin_model.ordering = ["name"]
    r = await client.get(
        f"/api/list/{event.get_model_name()}",
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert data
    assert data["total"] > 0
    item = next((result for result in data["results"] if str(result["id"]) == str(event.id)), None)
    assert item

    event_admin_model.ordering = ["invalid"]
    r = await client.get(
        f"/api/list/{event.get_model_name()}",
    )
    assert r.status_code == 422, r.text


async def test_list_select_related(session_id, admin_models, event, client):
    assert session_id

    event_admin_model = admin_models[event.__class__]

    event_admin_model.list_select_related = ["tournament"]
    r = await client.get(
        f"/api/list/{event.get_model_name()}",
    )
    assert r.status_code == 200, r.text

    event_admin_model.list_select_related = ["invalid"]
    r = await client.get(
        f"/api/list/{event.get_model_name()}",
    )
    assert r.status_code == 422, r.text


async def test_list_display_fields(session_id, admin_models, event, client):
    assert session_id

    event_admin_model = admin_models[event.__class__]

    event_admin_model.list_display = ["started", "name_with_price"]
    r = await client.get(
        f"/api/list/{event.get_model_name()}",
    )
    assert r.status_code == 200, r.text

    event_admin_model.list_display = ["invalid"]
    r = await client.get(
        f"/api/list/{event.get_model_name()}",
    )
    assert r.status_code == 200, r.text


async def test_list_401(event, client):
    r = await client.get(
        f"/api/list/{event.get_model_name()}",
    )
    assert r.status_code == 401, r.text


async def test_list_404(session_id, admin_models, event, client):
    assert session_id
    del admin_models[event.__class__]
    r = await client.get(
        f"/api/list/{event.get_model_name()}",
    )
    assert r.status_code == 404, r.text


async def test_list_405(session_id, event, client):
    assert session_id
    r = await client.post(
        f"/api/list/{event.get_model_name()}",
    )
    assert r.status_code == 405, r.text
