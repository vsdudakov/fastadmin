from uuid import UUID

from fastadmin.api.service import convert_id


def test_convert_id():
    assert convert_id("1") == 1
    assert convert_id("1000") == 1000
    assert convert_id(1000) == 1000
    assert convert_id("123e4567-e89b-12d3-a456-426614174000") == UUID("123e4567-e89b-12d3-a456-426614174000")
    assert convert_id(UUID("123e4567-e89b-12d3-a456-426614174000")) == UUID("123e4567-e89b-12d3-a456-426614174000")
    assert convert_id("invalid") is None
