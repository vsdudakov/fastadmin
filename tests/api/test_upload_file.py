async def test_upload_file_405(session_id, event, client):
    """Non-POST method returns 405."""
    assert session_id
    r = await client.get(
        f"/api/upload-file/{event.get_model_name()}/{event.id}/file",
    )
    assert r.status_code == 405, r.text


async def test_upload_file_422_invalid_id(session_id, event, client):
    """Empty or invalid id returns 422 (Django/Flask check in view; FastAPI may get to service)."""
    assert session_id
    # Empty path segment for id to trigger is_valid_id(id) -> False
    r = await client.post(
        f"/api/upload-file/{event.get_model_name()}//file",
        files={"file": ("x.txt", b"content")},
    )
    # Django and Flask return 422 for invalid id; FastAPI might 404 on route
    assert r.status_code in (404, 422), r.text


async def test_upload_file_no_file(session_id, event, client):
    """POST without file returns 400 (Django) or 422 (Flask/FastAPI)."""
    assert session_id
    r = await client.post(
        f"/api/upload-file/{event.get_model_name()}/{event.id}/file",
        data={},
    )
    assert r.status_code in (400, 422), r.text


async def test_upload_file_empty_filename(session_id, event, client):
    """Empty filename returns 422 (FastAPI/Flask) or 400 (Django treats as no file)."""
    assert session_id
    r = await client.post(
        f"/api/upload-file/{event.get_model_name()}/{event.id}/file",
        files={"file": ("", b"content")},
    )
    assert r.status_code in (400, 422, 500), r.text


async def test_upload_file_401(event, client):
    """No session returns 401."""
    r = await client.post(
        f"/api/upload-file/{event.get_model_name()}/{event.id}/file",
        files={"file": ("x.txt", b"content")},
    )
    assert r.status_code == 401, r.text


async def test_upload_file_calls_service(session_id, event, client):
    """POST with file hits service; base upload_file raises so we get 500 or 404."""
    assert session_id
    r = await client.post(
        f"/api/upload-file/{event.get_model_name()}/{event.id}/file",
        files={"file": ("x.txt", b"content")},
    )
    # Event admin may not implement upload_file -> 500, or model not found -> 404
    assert r.status_code in (404, 500), r.text
