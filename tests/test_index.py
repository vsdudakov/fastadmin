async def test_index(client):
    r = await client.get("/")
    assert r.status_code == 200
