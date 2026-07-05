import datetime
from decimal import Decimal

import pytest

from fastadmin.api.encoders import (
    CUSTOM_ENCODERS,
    apply_custom_encoders,
    clear_encoders,
    register_encoder,
    unregister_encoder,
)


@pytest.fixture(autouse=True)
def _clear_encoders():
    """Keep the global registry isolated between tests."""
    clear_encoders()
    yield
    clear_encoders()


def test_apply_custom_encoders_no_match_returns_unchanged():
    value = object()
    assert apply_custom_encoders(value) is value


def test_register_and_apply_encoder():
    register_encoder(datetime.datetime, lambda dt: dt.strftime("%Y-%m-%d %H:%M"))
    result = apply_custom_encoders(datetime.datetime(2024, 1, 31, 14, 5, 9, tzinfo=datetime.UTC))
    assert result == "2024-01-31 14:05"


def test_encoder_matches_by_isinstance_registration_order():
    class Base:
        pass

    class Child(Base):
        pass

    register_encoder(Child, lambda _: "child")
    register_encoder(Base, lambda _: "base")
    # Child is registered first, so it wins for a Child instance.
    assert apply_custom_encoders(Child()) == "child"
    assert apply_custom_encoders(Base()) == "base"


def test_register_encoder_overrides_previous():
    register_encoder(Decimal, lambda _: "first")
    register_encoder(Decimal, lambda _: "second")
    assert apply_custom_encoders(Decimal("1")) == "second"


def test_unregister_encoder():
    register_encoder(Decimal, lambda _: "x")
    unregister_encoder(Decimal)
    assert apply_custom_encoders(Decimal("1")) == Decimal("1")
    # unregistering an absent type is a no-op
    unregister_encoder(Decimal)


def test_clear_encoders():
    register_encoder(Decimal, lambda _: "x")
    register_encoder(datetime.date, lambda _: "y")
    clear_encoders()
    assert CUSTOM_ENCODERS == {}
