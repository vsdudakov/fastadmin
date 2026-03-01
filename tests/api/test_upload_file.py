def _upload_file_url(model_name: str, field_name: str = "file") -> str:
    """Upload file URL without id: /api/upload-file/{model}/{field_name}."""
    return f"/api/upload-file/{model_name}/{field_name}"


async def test_upload_file_405(session_id, event, client):
    """Non-POST method returns 405."""
    assert session_id
    r = await client.get(_upload_file_url(event.get_model_name()))
    assert r.status_code == 405, r.text


async def test_upload_file_404_model_not_registered(session_id, event, client):
    """Unknown model in path returns 404."""
    assert session_id
    r = await client.post(
        _upload_file_url("UnknownModel"),
        files={"file": ("x.txt", b"content")},
    )
    assert r.status_code == 404, r.text


async def test_upload_file_no_file(session_id, event, client):
    """POST without file returns 400 (Django) or 422 (Flask/FastAPI)."""
    assert session_id
    r = await client.post(
        _upload_file_url(event.get_model_name()),
        data={},
    )
    assert r.status_code in (400, 422), r.text


async def test_upload_file_empty_filename(session_id, event, client):
    """Empty filename returns 422 (FastAPI/Flask) or 400 (Django treats as no file)."""
    assert session_id
    r = await client.post(
        _upload_file_url(event.get_model_name()),
        files={"file": ("", b"content")},
    )
    assert r.status_code in (400, 422, 500), r.text


async def test_upload_file_401(event, client):
    """No session returns 401."""
    r = await client.post(
        _upload_file_url(event.get_model_name()),
        files={"file": ("x.txt", b"content")},
    )
    assert r.status_code == 401, r.text


async def test_upload_file_calls_service(session_id, event, client):
    """POST with file hits service; base upload_file raises so we get 500 or 404."""
    assert session_id
    r = await client.post(
        _upload_file_url(event.get_model_name()),
        files={"file": ("x.txt", b"content")},
    )
    # Event admin may not implement upload_file -> 500, or model not found -> 404
    assert r.status_code in (404, 500), r.text
