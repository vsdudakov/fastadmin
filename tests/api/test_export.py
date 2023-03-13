async def test_export(session_id, event, client):
    assert session_id
    async with client.stream(
        "POST",
        f"/api/export/{event.get_model_name()}",
        json={},
    ) as r:
        assert r.status_code == 200, r.text
        rows = []
        async for line in r.aiter_lines():
            rows.append(line)
    assert rows


async def test_export_405(session_id, event, client):
    assert session_id
    r = await client.get(
        f"/api/export/{event.get_model_name()}",
    )
    assert r.status_code == 405, r.text


async def test_export_401(event, client):
    async with client.stream(
        "POST",
        f"/api/export/{event.get_model_name()}",
        json={},
    ) as r:
        assert r.status_code == 401, r.text


async def test_export_404(session_id, admin_models, event, client):
    assert session_id
    del admin_models[event.__class__]
    async with client.stream(
        "POST",
        f"/api/export/{event.get_model_name()}",
        json={},
    ) as r:
        assert r.status_code == 404, r.text
