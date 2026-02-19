import uuid
from datetime import datetime, timedelta, timezone

import jwt

from fastadmin.api.helpers import (
    get_template,
    is_valid_id,
    is_valid_uuid,
    parse_list_filters_from_query_params,
    sanitize_filter_key,
    sanitize_filter_value,
)
from fastadmin.api.service import get_user_id_from_session_id
from fastadmin.models.schemas import ModelFieldWidgetSchema, WidgetType
from fastadmin.settings import settings


async def test_sanitize_filter_value():
    assert sanitize_filter_value("true") is True
    assert sanitize_filter_value("false") is False
    assert sanitize_filter_value("null") is None
    assert sanitize_filter_value("foo") == "foo"
    assert sanitize_filter_value(["true", "false"]) == [True, False]
    assert sanitize_filter_value(["null", "foo"]) == [None, "foo"]


async def test_parse_list_filters_from_query_params():
    def keys():
        return ["search", "name", "id__in", "other", "skip"]

    def getlist(k):
        if k == "search":
            return ["x"]
        if k == "name":
            return ["Test"]
        if k == "id__in":
            return ["1", "2", "3"]
        if k == "other":
            return ["a"]
        if k == "skip":
            return []
        return []

    result = parse_list_filters_from_query_params(
        keys, getlist, exclude={"search", "sort_by", "offset", "limit", "skip"}
    )
    assert result["name"] == "Test"
    assert result["id__in"] == ["1", "2", "3"]
    assert result["other"] == "a"
    assert "search" not in result
    assert "skip" not in result

    # Key not in exclude but getlist returns [] -> continue (line 39-40)
    def keys2():
        return ["empty_key"]

    def getlist2(k):
        return [] if k == "empty_key" else ["x"]

    result_empty = parse_list_filters_from_query_params(keys2, getlist2, exclude=set())
    assert result_empty == {}

    # __in with comma-separated single value
    result2 = parse_list_filters_from_query_params(
        lambda: ["tags__in"],
        lambda k: ["a, b , c"] if k == "tags__in" else [],
        exclude=set(),
    )
    assert result2["tags__in"] == ["a", "b", "c"]


def _make_field(name, filter_widget_props=None, is_m2m=False):
    return ModelFieldWidgetSchema(
        name=name,
        column_name=name,
        is_m2m=is_m2m,
        is_pk=False,
        is_immutable=False,
        form_widget_type=WidgetType.Input,
        form_widget_props={},
        filter_widget_type=WidgetType.Input,
        filter_widget_props=filter_widget_props or {},
    )


async def test_sanitize_filter_key():
    fields = [
        _make_field("tournament", filter_widget_props={"parentModel": "Tournament"}),
        _make_field("name"),
    ]
    field_name, condition = sanitize_filter_key("name", fields)
    assert field_name == "name"
    assert condition == "exact"
    field_name2, condition2 = sanitize_filter_key("tournament", fields)
    assert field_name2 == "tournament_id"
    assert condition2 == "exact"
    fn, cond = sanitize_filter_key("name__icontains", fields)
    assert fn == "name"
    assert cond == "icontains"


async def test_is_valid_uuid():
    assert is_valid_uuid(str(uuid.uuid1())) is True
    assert is_valid_uuid(str(uuid.uuid3(uuid.uuid4(), "test"))) is True
    assert is_valid_uuid(str(uuid.uuid4())) is True
    assert is_valid_uuid(str(uuid.uuid5(uuid.uuid4(), "test"))) is True
    assert is_valid_uuid("invalid") is False


async def test_is_valid_id():
    assert is_valid_id(1) is True
    assert is_valid_id(uuid.uuid4()) is True
    assert is_valid_id("1") is True
    assert is_valid_id(str(uuid.uuid4())) is True
    assert is_valid_id("MANUAL") is True  # string PK
    assert is_valid_id("") is False
    assert is_valid_id(None) is False  # TypeError in int(None)
    assert is_valid_id(object()) is False  # non-str, int() raises TypeError


async def test_get_user_id_from_session_id(session_id):
    assert await get_user_id_from_session_id(None) is None
    assert await get_user_id_from_session_id("invalid") is None
    user_id = await get_user_id_from_session_id(session_id)
    assert user_id is not None

    now = datetime.now(timezone.utc)
    session_expired_at = now + timedelta(seconds=settings.ADMIN_SESSION_EXPIRED_AT)
    without_expired_session_id = jwt.encode(
        {
            "user_id": str(user_id),
        },
        settings.ADMIN_SECRET_KEY,
        algorithm="HS256",
    )
    assert await get_user_id_from_session_id(without_expired_session_id) is None

    session_expired_at = now - timedelta(seconds=settings.ADMIN_SESSION_EXPIRED_AT)
    expired_session_id = jwt.encode(
        {
            "user_id": str(user_id),
            "session_expired_at": session_expired_at.isoformat(),
        },
        settings.ADMIN_SECRET_KEY,
        algorithm="HS256",
    )
    assert await get_user_id_from_session_id(expired_session_id) is None

    session_expired_at = now + timedelta(seconds=settings.ADMIN_SESSION_EXPIRED_AT)
    invalid_user_session_id = jwt.encode(
        {
            "user_id": str(-1),
            "session_expired_at": session_expired_at.isoformat(),
        },
        settings.ADMIN_SECRET_KEY,
        algorithm="HS256",
    )
    assert await get_user_id_from_session_id(invalid_user_session_id) is None


async def test_get_template(tmp_path):
    template = tmp_path / "tpl.txt"
    template.write_text("Hello {{name}}, count={{count}}")
    out = get_template(template, {"name": "World", "count": 42})
    assert out == "Hello World, count=42"
