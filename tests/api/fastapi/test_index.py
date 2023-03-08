async def test_index(fastapi_client):
    r = await fastapi_client.get("/")
    assert r.status_code == 200
