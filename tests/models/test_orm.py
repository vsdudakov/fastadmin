from fastadmin.models.helpers import get_admin_model
from fastadmin.models.schemas import ModelFieldWidgetSchema, WidgetType


def test_get_form_widget_user(user):
    admin_model_obj = get_admin_model(user.__class__)
    fields: list[ModelFieldWidgetSchema] = admin_model_obj.get_model_fields_with_widget_types()
    for field in (
        "id",
        "created_at",
        "updated_at",
        "username",
        "password",
        "is_superuser",
    ):
        assert field in [f.name for f in fields]
    for field in fields:
        match field.name:
            case "id":
                assert field.column_name == "id"
                assert not field.is_m2m
                assert field.is_pk
                assert field.is_immutable
                assert field.filter_widget_type == WidgetType.InputNumber
                assert field.filter_widget_props
                assert field.form_widget_type == WidgetType.InputNumber
                assert field.form_widget_props
            case "created_at":
                assert field.column_name == "created_at"
                assert not field.is_m2m
                assert not field.is_pk
                assert field.is_immutable
                assert field.filter_widget_type == WidgetType.RangePicker
                assert field.filter_widget_props
                assert field.form_widget_type == WidgetType.DateTimePicker
                assert field.form_widget_props
            case "updated_at":
                assert field.column_name == "updated_at"
                assert not field.is_m2m
                assert not field.is_pk
                assert field.is_immutable
                assert field.filter_widget_type == WidgetType.RangePicker
                assert field.filter_widget_props
                assert field.form_widget_type == WidgetType.DateTimePicker
                assert field.form_widget_props
            case "username":
                assert field.column_name == "username"
                assert not field.is_m2m
                assert not field.is_pk
                assert not field.is_immutable
                assert field.filter_widget_type == WidgetType.Input
                assert field.filter_widget_props
                assert field.form_widget_type == WidgetType.Input
                assert field.form_widget_props
            case "password":
                assert field.column_name == "password"
                assert not field.is_m2m
                assert not field.is_pk
                assert not field.is_immutable
                assert field.filter_widget_type == WidgetType.Input
                assert field.filter_widget_props
                assert field.form_widget_type == WidgetType.Input
                assert field.form_widget_props
            case "is_superuser":
                assert field.column_name == "is_superuser"
                assert not field.is_m2m
                assert not field.is_pk
                assert not field.is_immutable
                assert field.filter_widget_type == WidgetType.RadioGroup
                assert field.filter_widget_props["options"]
                assert field.form_widget_type == WidgetType.Switch
                assert field.form_widget_props
            case "events":
                assert field.column_name == "events"
                assert field.is_m2m
                assert not field.is_pk
                assert not field.is_immutable
                assert field.filter_widget_type == WidgetType.AsyncSelect
                assert field.filter_widget_props["mode"] == "multiple"
                assert field.form_widget_type == WidgetType.AsyncSelect
                assert field.form_widget_props["mode"] == "multiple"
            case _:
                raise ValueError(f"Unexpected field: {field.name}")


def test_get_form_widget_tournament(tournament):
    admin_model_obj = get_admin_model(tournament.__class__)
    fields: list[ModelFieldWidgetSchema] = admin_model_obj.get_model_fields_with_widget_types()
    for field in (
        "id",
        "created_at",
        "updated_at",
        "name",
    ):
        assert field in [f.name for f in fields]
    for field in fields:
        match field.name:
            case "id":
                assert field.column_name == "id"
                assert not field.is_m2m
                assert field.is_pk
                assert field.is_immutable
                assert field.filter_widget_type == WidgetType.InputNumber
                assert field.filter_widget_props
                assert field.form_widget_type == WidgetType.InputNumber
                assert field.form_widget_props
            case "created_at":
                assert field.column_name == "created_at"
                assert not field.is_m2m
                assert not field.is_pk
                assert field.is_immutable
                assert field.filter_widget_type == WidgetType.RangePicker
                assert field.filter_widget_props
                assert field.form_widget_type == WidgetType.DateTimePicker
                assert field.form_widget_props
            case "updated_at":
                assert field.column_name == "updated_at"
                assert not field.is_m2m
                assert not field.is_pk
                assert field.is_immutable
                assert field.filter_widget_type == WidgetType.RangePicker
                assert field.filter_widget_props
                assert field.form_widget_type == WidgetType.DateTimePicker
                assert field.form_widget_props
            case "name":
                assert field.column_name == "name"
                assert not field.is_m2m
                assert not field.is_pk
                assert not field.is_immutable
                assert field.filter_widget_type == WidgetType.Input
                assert field.filter_widget_props
                assert field.form_widget_type == WidgetType.Input
                assert field.form_widget_props
            case "events":
                assert field.column_name == "events"
                assert field.is_m2m
                assert not field.is_pk
                assert not field.is_immutable
                assert field.filter_widget_type == WidgetType.AsyncSelect
                assert field.filter_widget_props["mode"] == "multiple"
                assert field.form_widget_type == WidgetType.AsyncSelect
                assert field.form_widget_props["mode"] == "multiple"
            case _:
                raise ValueError(f"Unexpected field: {field.name}")


def test_get_form_widget_event(event):
    admin_model_obj = get_admin_model(event.__class__)
    fields: list[ModelFieldWidgetSchema] = admin_model_obj.get_model_fields_with_widget_types()
    for field in (
        "id",
        "created_at",
        "updated_at",
        "base",
        "name",
        "tournament",
        "participants",
        "is_active",
        "start_time",
        "date",
        "latitude",
        "longitude",
        "price",
        "json",
    ):
        assert field in [f.name for f in fields]
    for field in fields:
        match field.name:
            case "id":
                assert field.column_name == "id"
                assert not field.is_m2m
                assert field.is_pk
                assert field.is_immutable
                assert field.filter_widget_type == WidgetType.InputNumber
                assert field.filter_widget_props
                assert field.form_widget_type == WidgetType.InputNumber
                assert field.form_widget_props
            case "created_at":
                assert field.column_name == "created_at"
                assert not field.is_m2m
                assert not field.is_pk
                assert field.is_immutable
                assert field.filter_widget_type == WidgetType.RangePicker
                assert field.filter_widget_props
                assert field.form_widget_type == WidgetType.DateTimePicker
                assert field.form_widget_props
            case "updated_at":
                assert field.column_name == "updated_at"
                assert not field.is_m2m
                assert not field.is_pk
                assert field.is_immutable
                assert field.filter_widget_type == WidgetType.RangePicker
                assert field.filter_widget_props
                assert field.form_widget_type == WidgetType.DateTimePicker
                assert field.form_widget_props
            case "base":
                assert field.column_name in ("base_id", "base")
                assert not field.is_m2m
                assert not field.is_pk
                assert not field.is_immutable
                assert field.filter_widget_type == WidgetType.AsyncSelect
                assert field.filter_widget_props["mode"] == "multiple"
                assert field.form_widget_type == WidgetType.AsyncSelect
                assert field.form_widget_props
            case "name":
                assert field.column_name == "name"
                assert not field.is_m2m
                assert not field.is_pk
                assert not field.is_immutable
                assert field.filter_widget_type == WidgetType.Input
                assert field.filter_widget_props
                assert field.form_widget_type == WidgetType.Input
                assert field.form_widget_props
            case "tournament":
                assert field.column_name in ("tournament_id", "tournament")
                assert not field.is_m2m
                assert not field.is_pk
                assert not field.is_immutable
                assert field.filter_widget_type == WidgetType.AsyncSelect
                assert field.filter_widget_props["mode"] == "multiple"
                assert field.form_widget_type == WidgetType.AsyncSelect
                assert field.form_widget_props
            case "participants":
                assert field.column_name == "participants"
                assert field.is_m2m
                assert not field.is_pk
                assert not field.is_immutable
                assert field.filter_widget_type == WidgetType.AsyncSelect
                assert field.filter_widget_props["mode"] == "multiple"
                assert field.form_widget_type == WidgetType.AsyncSelect
                assert field.form_widget_props["mode"] == "multiple"
            case "rating":
                assert field.column_name == "rating"
                assert not field.is_m2m
                assert not field.is_pk
                assert not field.is_immutable
                assert field.filter_widget_type == WidgetType.InputNumber
                assert field.filter_widget_props
                assert field.form_widget_type == WidgetType.InputNumber
                assert field.form_widget_props
            case "description":
                assert field.column_name == "description"
                assert not field.is_m2m
                assert not field.is_pk
                assert not field.is_immutable
                assert field.filter_widget_type == WidgetType.TextArea
                assert field.filter_widget_props
                assert field.form_widget_type == WidgetType.TextArea
                assert field.form_widget_props
            case "event_type":
                assert field.column_name == "event_type"
                assert not field.is_m2m
                assert not field.is_pk
                assert not field.is_immutable
                assert field.filter_widget_type == WidgetType.Select
                assert field.filter_widget_props["options"]
                assert field.filter_widget_props["mode"] == "multiple"
                assert field.form_widget_type == WidgetType.Select
                assert field.form_widget_props["options"]
            case "is_active":
                assert field.column_name == "is_active"
                assert not field.is_m2m
                assert not field.is_pk
                assert not field.is_immutable
                assert field.filter_widget_type == WidgetType.RadioGroup
                assert field.filter_widget_props["options"]
                assert field.form_widget_type == WidgetType.Switch
                assert field.form_widget_props
            case "start_time":
                assert field.column_name == "start_time"
                assert not field.is_m2m
                assert not field.is_pk
                assert not field.is_immutable
                assert field.filter_widget_type == WidgetType.RangePicker
                assert field.filter_widget_props
                assert field.form_widget_type == WidgetType.TimePicker
                assert field.form_widget_props
            case "date":
                assert field.column_name == "date"
                assert not field.is_m2m
                assert not field.is_pk
                assert not field.is_immutable
                assert field.filter_widget_type == WidgetType.RangePicker
                assert field.filter_widget_props
                assert field.form_widget_type == WidgetType.DatePicker
                assert field.form_widget_props
            case "latitude":
                assert field.column_name == "latitude"
                assert not field.is_m2m
                assert not field.is_pk
                assert not field.is_immutable
                assert field.filter_widget_type == WidgetType.InputNumber
                assert field.filter_widget_props
                assert field.form_widget_type == WidgetType.InputNumber
                assert field.form_widget_props
            case "longitude":
                assert field.column_name == "longitude"
                assert not field.is_m2m
                assert not field.is_pk
                assert not field.is_immutable
                assert field.filter_widget_type == WidgetType.InputNumber
                assert field.filter_widget_props
                assert field.form_widget_type == WidgetType.InputNumber
                assert field.form_widget_props
            case "price":
                assert field.column_name == "price"
                assert not field.is_m2m
                assert not field.is_pk
                assert not field.is_immutable
                assert field.filter_widget_type == WidgetType.InputNumber
                assert field.filter_widget_props
                assert field.form_widget_type == WidgetType.InputNumber
                assert field.form_widget_props
            case "json":
                assert field.column_name == "json"
                assert not field.is_m2m
                assert not field.is_pk
                assert not field.is_immutable
                assert field.filter_widget_type == WidgetType.Input
                assert field.filter_widget_props
                assert field.form_widget_type in (WidgetType.Input, WidgetType.JsonTextArea)
                assert field.form_widget_props
            case _:
                raise ValueError(f"Unexpected field: {field.name}")


def test_nullable_foreign_key_form_required(event):
    """Nullable FK (base) must have required=False; non-nullable FK (tournament) required=True.

    Suitable for all ORMs: Django/Tortoise use field.null, Pony uses is_required,
    SQLAlchemy uses the underlying FK column's nullable.
    """
    admin_model = get_admin_model(event.__class__)
    fields = admin_model.get_model_fields_with_widget_types()
    by_name = {f.name: f for f in fields}
    assert "base" in by_name, "Event should have base (nullable FK) field"
    assert "tournament" in by_name, "Event should have tournament (required FK) field"
    assert (
        by_name["base"].form_widget_props["required"] is False
    ), "nullable FK base_id should be optional in admin form"
    assert (
        by_name["tournament"].form_widget_props["required"] is True
    ), "non-nullable FK tournament_id should be required in admin form"


def test_sqlalchemy_field_mapping_special_cases(monkeypatch):
    from types import SimpleNamespace

    from fastadmin.models.orms import sqlalchemy as sqlalchemy_orm
    from fastadmin.models.orms.sqlalchemy import SqlAlchemyModelAdmin

    class DummyModel:
        pass

    class RelModel:
        __table__ = SimpleNamespace(
            primary_key=SimpleNamespace(
                _autoincrement_column=SimpleNamespace(name="id"),
            )
        )

    class ARRAY:
        pass

    # First mapper: MANYTOONE without matching *_id FK column -> skip by continue at line 55.
    mapper_missing_fk = SimpleNamespace(
        c=[],
        relationships=[
            SimpleNamespace(
                key="owner",
                direction=SimpleNamespace(name="MANYTOONE"),
            )
        ],
    )
    monkeypatch.setattr(sqlalchemy_orm, "inspect", lambda _model_cls: mapper_missing_fk)
    admin_missing_fk = SqlAlchemyModelAdmin(DummyModel)
    assert admin_missing_fk.get_model_fields_with_widget_types() == []

    # Second mapper: ARRAY and ONETOONE relation branch coverage.
    mapper_full = SimpleNamespace(
        c=[
            SimpleNamespace(key="tags", foreign_keys=[], type=ARRAY()),
            SimpleNamespace(key="profile_id", foreign_keys=[1], nullable=False),
        ],
        relationships=[
            SimpleNamespace(
                key="profile",
                direction=SimpleNamespace(name="ONETOONE"),
                entity=SimpleNamespace(class_=RelModel),
            )
        ],
    )
    monkeypatch.setattr(sqlalchemy_orm, "inspect", lambda _model_cls: mapper_full)
    admin_full = SqlAlchemyModelAdmin(DummyModel)
    fields = admin_full.get_model_fields_with_widget_types()
    by_name = {f.name: f for f in fields}

    assert by_name["tags"].form_widget_type == WidgetType.Select
    assert by_name["tags"].form_widget_props["mode"] == "tags"
    assert by_name["tags"].filter_widget_props["mode"] == "tags"
    assert by_name["profile"].form_widget_type == WidgetType.AsyncSelect
    assert by_name["profile"].form_widget_props["parentModel"] == "RelModel"
    assert by_name["profile"].filter_widget_type == WidgetType.AsyncSelect
    assert by_name["profile"].filter_widget_props["mode"] == "multiple"

    # ONETOONE raw_id_fields branch -> Input widgets.
    admin_full.raw_id_fields = ("profile",)
    fields_raw = admin_full.get_model_fields_with_widget_types()
    by_name_raw = {f.name: f for f in fields_raw}
    assert by_name_raw["profile"].form_widget_type == WidgetType.Input
    assert by_name_raw["profile"].filter_widget_type == WidgetType.Input


def test_sqlalchemy_with_upload_false_skips_upload(user, session_with_type):
    _, session_type = session_with_type
    if session_type != "sqlalchemy":
        return

    admin_model = get_admin_model(user.__class__)
    admin_model.formfield_overrides["username"] = (WidgetType.Upload, {})
    fields = admin_model.get_model_fields_with_widget_types(with_upload=False)
    assert "username" not in [f.name for f in fields]


async def test_sqlalchemy_orm_get_list_filter_operators(event, session_with_type):
    _, session_type = session_with_type
    if session_type != "sqlalchemy":
        return

    admin_model = get_admin_model(event.__class__)
    objs, total = await admin_model.orm_get_list(
        filters={
            ("rating", "lte"): "10",
            ("rating", "gte"): "0",
            ("rating", "lt"): "100",
            ("rating", "gt"): "-1",
            ("rating", "in"): ["0", "1"],
            ("name", "contains"): "event",
        }
    )
    assert isinstance(total, int)
    assert isinstance(objs, list)


async def test_sqlalchemy_orm_get_list_search_nested_relation(event, session_with_type):
    _, session_type = session_with_type
    if session_type != "sqlalchemy":
        return

    admin_model = get_admin_model(event.__class__)
    admin_model.search_fields = ["name", "tournament__name"]

    objs, total = await admin_model.orm_get_list(search="Test Tournament")
    assert isinstance(total, int)
    assert total > 0
    assert any(getattr(obj, "id", None) == event.id for obj in objs)


def test_sqlalchemy_resolve_ordering_field_for_relation(monkeypatch):
    from types import SimpleNamespace

    from fastadmin.models.orms import sqlalchemy as sqlalchemy_orm
    from fastadmin.models.orms.sqlalchemy import SqlAlchemyModelAdmin

    relation = SimpleNamespace(
        key="tournament",
        direction=SimpleNamespace(name="MANYTOONE"),
        local_columns=[SimpleNamespace(key="tournament_id")],
    )
    fake_mapper = SimpleNamespace(c=[], relationships=[relation])
    monkeypatch.setattr(sqlalchemy_orm, "inspect", lambda _model_cls: fake_mapper)

    class FakeModel:
        pass

    admin = SqlAlchemyModelAdmin(FakeModel)
    assert admin._resolve_ordering_field("tournament") == "tournament_id"
    assert admin._resolve_ordering_field("-tournament") == "-tournament_id"
    assert admin._resolve_ordering_field("tournament__name") == "tournament__name"


def test_sqlalchemy_build_search_condition_edge_cases(session_with_type):
    from types import SimpleNamespace

    from fastadmin.models.orms.sqlalchemy import SqlAlchemyModelAdmin

    _, session_type = session_with_type
    if session_type != "sqlalchemy":
        return

    class LeafAttr:
        @staticmethod
        def ilike(_value):
            return "leaf-ilike"

    class RelatedLeafModel:
        name = LeafAttr()

    class RelationRoot:
        child = SimpleNamespace(
            property=SimpleNamespace(mapper=SimpleNamespace(class_=RelatedLeafModel), uselist=True),
            any=lambda _condition: "any-condition",
            has=lambda _condition: "has-condition",
        )

    class NoRelationPropertyRoot:
        child = SimpleNamespace()

    class NoRelatedModelRoot:
        child = SimpleNamespace(property=SimpleNamespace(mapper=SimpleNamespace(), uselist=False))

    class MissingNestedFieldRoot:
        child = SimpleNamespace(
            property=SimpleNamespace(mapper=SimpleNamespace(class_=SimpleNamespace()), uselist=False)
        )

    admin = SqlAlchemyModelAdmin(RelationRoot)
    assert admin._build_search_condition("missing", "a") is None

    admin.model_cls = NoRelationPropertyRoot
    assert admin._build_search_condition("child__name", "a") is None

    admin.model_cls = NoRelatedModelRoot
    assert admin._build_search_condition("child__name", "a") is None

    admin.model_cls = MissingNestedFieldRoot
    assert admin._build_search_condition("child__name", "a") is None

    admin.model_cls = RelationRoot
    assert admin._build_search_condition("child__name", "a") == "any-condition"


def test_sqlalchemy_resolve_ordering_field_edge_cases(monkeypatch):
    from types import SimpleNamespace

    from fastadmin.models.orms import sqlalchemy as sqlalchemy_orm
    from fastadmin.models.orms.sqlalchemy import SqlAlchemyModelAdmin

    relation = SimpleNamespace(
        key="tournament",
        direction=SimpleNamespace(name="MANYTOONE"),
        local_columns=[],
    )
    fake_mapper = SimpleNamespace(c=[], relationships=[relation])
    monkeypatch.setattr(sqlalchemy_orm, "inspect", lambda _model_cls: fake_mapper)

    class FakeModel:
        pass

    admin = SqlAlchemyModelAdmin(FakeModel)
    assert admin._resolve_ordering_field("") == ""
    assert admin._resolve_ordering_field("tournament") == "tournament_id"


async def test_sqlalchemy_orm_serialize_obj_by_id(event, session_with_type):
    _, session_type = session_with_type
    if session_type != "sqlalchemy":
        return

    admin_model = get_admin_model(event.__class__)
    assert await admin_model.orm_serialize_obj_by_id(-1) is None
    obj = await admin_model.orm_serialize_obj_by_id(event.id)
    assert obj is not None
    assert str(obj["id"]) == str(event.id)


async def test_sqlalchemy_orm_get_list_search_without_valid_fields_returns_empty(event, session_with_type):
    _, session_type = session_with_type
    if session_type != "sqlalchemy":
        return

    admin_model = get_admin_model(event.__class__)
    admin_model.search_fields = ["does_not_exist"]
    objs, total = await admin_model.orm_get_list(search="irrelevant")
    assert objs == []
    assert total == 0


async def test_sqlalchemy_orm_save_obj_fk_string_conversion(tournament, session_with_type):
    _, session_type = session_with_type
    if session_type != "sqlalchemy":
        return

    from tests.environment.sqlalchemy_env.models import Event

    admin_model = get_admin_model(Event)
    obj = await admin_model.orm_save_obj(
        None,
        {
            "name": "created-by-test",
            "tournament_id": str(tournament.id),
            "rating": 0,
            "is_active": True,
        },
    )
    assert obj is not None
    assert obj.tournament_id == tournament.id
    await admin_model.orm_delete_obj(obj.id)


async def test_sqlalchemy_m2m_edge_cases(event, session_with_type):
    from types import SimpleNamespace

    import pytest

    _, session_type = session_with_type
    if session_type != "sqlalchemy":
        return

    admin_model = get_admin_model(event.__class__)
    assert await admin_model.orm_get_m2m_ids(SimpleNamespace(id=-1), "participants") == []

    with pytest.raises(ValueError, match="Field unknown_field is not a relationship field."):
        await admin_model.orm_save_m2m_ids(event, "unknown_field", [1])

    # id=0 hits early-return branch before writing m2m rows.
    await admin_model.orm_save_m2m_ids(SimpleNamespace(id=0), "participants", [1])


def test_ponyorm_field_mapping_special_cases():
    from types import SimpleNamespace

    from fastadmin.models.orms.ponyorm import PonyORMModelAdmin

    O2ORelation = type("o2o", (), {"_pk_": SimpleNamespace(name="id")})

    fake_array_field = SimpleNamespace(
        py_type=type("IntArray", (), {}),
        name="tags",
        is_relation=False,
        is_collection=False,
        is_pk=False,
        hidden=False,
        is_required=False,
    )
    fake_o2o_field = SimpleNamespace(
        py_type=O2ORelation,
        name="profile",
        is_relation=False,
        is_collection=False,
        is_pk=False,
        hidden=False,
        is_required=False,
    )

    class FakeModel:
        tags = fake_array_field
        profile = fake_o2o_field

    admin = PonyORMModelAdmin(FakeModel)
    fields = admin.get_model_fields_with_widget_types()
    by_name = {f.name: f for f in fields}

    assert by_name["tags"].form_widget_type == WidgetType.Select
    assert by_name["tags"].form_widget_props["mode"] == "tags"
    assert by_name["tags"].filter_widget_type == WidgetType.Select
    assert by_name["tags"].filter_widget_props["mode"] == "tags"

    assert by_name["profile"].form_widget_type == WidgetType.AsyncSelect
    assert by_name["profile"].form_widget_props["parentModel"] == "o2o"
    assert by_name["profile"].form_widget_props["idField"] == "id"
    assert by_name["profile"].filter_widget_type == WidgetType.AsyncSelect
    assert by_name["profile"].filter_widget_props["mode"] == "multiple"

    admin.raw_id_fields = ("profile",)
    mapped_raw = admin.get_model_fields_with_widget_types()
    by_name_raw = {f.name: f for f in mapped_raw}
    assert by_name_raw["profile"].form_widget_type == WidgetType.Input
    assert by_name_raw["profile"].filter_widget_type == WidgetType.Input


def test_ponyorm_with_upload_false_skips_upload(user, session_with_type):
    _, session_type = session_with_type
    if session_type != "ponyorm":
        return

    admin_model = get_admin_model(user.__class__)
    admin_model.formfield_overrides["username"] = (WidgetType.Upload, {})
    fields = admin_model.get_model_fields_with_widget_types(with_upload=False)
    assert "username" not in [f.name for f in fields]


async def test_ponyorm_orm_get_list_filter_operators():
    from types import SimpleNamespace

    from fastadmin.models.orms.ponyorm import PonyORMModelAdmin

    class FakeQuery:
        def __init__(self):
            self.filters = []

        def filter(self, expression):
            self.filters.append(expression)
            return self

        def order_by(self, *args):
            return self

        def prefetch(self, *args):
            return self

        def limit(self, _limit, offset=0):
            return self

        def count(self):
            return 0

        def __iter__(self):
            return iter([])

    fake_query = FakeQuery()

    class FakeModel:
        _pk_ = SimpleNamespace(name="id")
        id = "id"
        name = "name"

        @staticmethod
        def select(*args, **kwargs):
            return fake_query

    admin_model = PonyORMModelAdmin(FakeModel)
    objs, total = await admin_model.orm_get_list(
        filters={
            ("id", "in"): [1, 2],
            ("name", "lte"): "zzzz",
            ("name", "gte"): "",
            ("name", "lt"): "zzzz",
            ("name", "gt"): "",
            ("name", "contains"): "eve",
        }
    )
    assert total == 0
    assert objs == []
    assert fake_query.filters


async def test_ponyorm_orm_get_list_search_nested_relation(event, session_with_type):
    _, session_type = session_with_type
    if session_type != "ponyorm":
        return

    admin_model = get_admin_model(event.__class__)
    admin_model.search_fields = ["name", "tournament__name"]
    objs, total = await admin_model.orm_get_list(search="Test Tournament")
    assert isinstance(total, int)
    assert total > 0
    assert any(getattr(obj, "id", None) == event.id for obj in objs)


async def test_ponyorm_edge_cases(event, session_with_type):
    from types import SimpleNamespace

    _, session_type = session_with_type
    if session_type != "ponyorm":
        return

    admin_model = get_admin_model(event.__class__)

    # delete missing object should return without raising
    await admin_model.orm_delete_obj(-1)

    # m2m/get serialize paths when object is missing
    assert await admin_model.orm_get_m2m_ids(SimpleNamespace(id=-1), "participants") == []
    await admin_model.orm_save_m2m_ids(SimpleNamespace(id=-1), "participants", [1])

    attrs = [
        ModelFieldWidgetSchema(
            name="id",
            column_name="id",
            is_m2m=False,
            is_pk=True,
            is_immutable=False,
            form_widget_type=WidgetType.Input,
            form_widget_props={},
            filter_widget_type=WidgetType.Input,
            filter_widget_props={},
        )
    ]
    assert await admin_model.serialize_obj_attributes(SimpleNamespace(id=-1), attrs) == {}


async def test_ponyorm_serialize_obj_by_id_relation_values_are_primitives(event, session_with_type):
    _, session_type = session_with_type
    if session_type != "ponyorm":
        return

    admin_model = get_admin_model(event.__class__)
    obj = await admin_model.orm_serialize_obj_by_id(event.id)
    assert obj is not None
    assert isinstance(obj.get("tournament"), int)
    assert obj.get("base") is None or isinstance(obj.get("base"), int)


async def test_ponyorm_serialize_obj_by_id_none_when_missing(event, session_with_type):
    _, session_type = session_with_type
    if session_type != "ponyorm":
        return

    admin_model = get_admin_model(event.__class__)
    assert await admin_model.orm_serialize_obj_by_id(-1) is None


async def test_ponyorm_serialize_obj_by_id_display_and_relation_edge_cases(session_with_type):
    from types import SimpleNamespace

    _, session_type = session_with_type
    if session_type != "ponyorm":
        return

    from fastadmin.models.orms.ponyorm import PonyORMModelAdmin

    class FakeRelatedModel:
        _pk_ = SimpleNamespace(name="id")

    relation_attr = SimpleNamespace(is_relation=True, py_type=FakeRelatedModel)

    class FakeEntity:
        relation = None
        skip = "skip-value"

        def __str__(self):
            return "entity"

    class FakeQuery:
        @staticmethod
        def first():
            return FakeEntity()

    class FakeModel:
        _pk_ = SimpleNamespace(name="id")
        relation = relation_attr

        @staticmethod
        def select(**_kwargs):
            return FakeQuery()

    admin_model = PonyORMModelAdmin(FakeModel)
    admin_model.get_model_fields_with_widget_types = lambda: [  # type: ignore[method-assign]
        ModelFieldWidgetSchema(
            name="skip",
            column_name="skip",
            is_m2m=False,
            is_pk=False,
            is_immutable=False,
            form_widget_type=WidgetType.Input,
            form_widget_props={},
            filter_widget_type=WidgetType.Input,
            filter_widget_props={},
        ),
        ModelFieldWidgetSchema(
            name="relation",
            column_name="relation",
            is_m2m=False,
            is_pk=False,
            is_immutable=False,
            form_widget_type=WidgetType.Input,
            form_widget_props={},
            filter_widget_type=WidgetType.Input,
            filter_widget_props={},
        ),
    ]
    admin_model.get_fields_for_serialize = lambda: {"relation", "async_display", "sync_display"}  # type: ignore[method-assign]

    async def async_display(_obj):
        return "async-skipped"

    async_display.is_display = True  # type: ignore[attr-defined]

    def sync_display(obj):
        if isinstance(obj, SimpleNamespace):
            raise AttributeError("force fallback from proxy")
        return "fallback-ok"

    sync_display.is_display = True  # type: ignore[attr-defined]

    admin_model.async_display = async_display  # type: ignore[method-assign]
    admin_model.sync_display = sync_display  # type: ignore[method-assign]

    obj = await admin_model.orm_serialize_obj_by_id(1)
    assert obj is not None
    assert obj["relation"] is None
    assert obj["sync_display"] == "fallback-ok"
    assert "async_display" not in obj


def test_tortoise_field_mapping_special_cases():
    from types import SimpleNamespace

    from fastadmin.models.orms.tortoise import TortoiseModelAdmin

    class RelatedModel:
        _meta = SimpleNamespace(pk_attr="id")

    fake_array = type("ArrayField", (), {})()
    fake_array.name = "tags"
    fake_array.pk = False
    fake_array.auto_now = False
    fake_array.auto_now_add = False
    fake_array.null = True
    fake_array.default = False
    fake_array._generated = False
    fake_array.reference = False

    fake_fk = type("ForeignKeyFieldInstance", (), {})()
    fake_fk.name = "profile"
    fake_fk.pk = False
    fake_fk.auto_now = False
    fake_fk.auto_now_add = False
    fake_fk.null = True
    fake_fk.default = False
    fake_fk._generated = False
    fake_fk.reference = False
    fake_fk.related_model = RelatedModel

    fake_model = type(
        "FakeTortoiseModel",
        (),
        {"_meta": SimpleNamespace(pk_attr="id", fields_map={"tags": fake_array, "profile": fake_fk})},
    )

    admin = TortoiseModelAdmin(fake_model)
    admin.formfield_overrides = {}
    fields = admin.get_model_fields_with_widget_types()
    by_name = {f.name: f for f in fields}
    assert by_name["tags"].form_widget_type == WidgetType.Select
    assert by_name["tags"].form_widget_props["mode"] == "tags"
    assert by_name["tags"].filter_widget_props["mode"] == "tags"

    admin.formfield_overrides = {"tags": (WidgetType.Upload, {})}
    mapped_no_upload = admin.get_model_fields_with_widget_types(with_upload=False)
    assert "tags" not in [f.name for f in mapped_no_upload]


def test_tortoise_resolve_ordering_field_for_relation():
    from types import SimpleNamespace

    from fastadmin.models.orms.tortoise import TortoiseModelAdmin

    fake_fk = type("ForeignKeyFieldInstance", (), {})()
    fake_fk.name = "tournament"

    fake_model = type(
        "FakeTortoiseModelForOrdering",
        (),
        {"_meta": SimpleNamespace(pk_attr="id", fields_map={"tournament": fake_fk})},
    )
    admin = TortoiseModelAdmin(fake_model)

    assert admin._resolve_ordering_field("tournament") == "tournament_id"
    assert admin._resolve_ordering_field("-tournament") == "-tournament_id"
    assert admin._resolve_ordering_field("tournament__name") == "tournament__name"


def test_tortoise_resolve_ordering_field_edge_cases():
    from types import SimpleNamespace

    from fastadmin.models.orms.tortoise import TortoiseModelAdmin

    fake_model = type("FakeTortoiseModelForOrderingEdges", (), {"_meta": SimpleNamespace(pk_attr="id", fields_map={})})
    admin = TortoiseModelAdmin(fake_model)

    assert admin._resolve_ordering_field("") == ""
    assert admin._resolve_ordering_field("unknown") == "unknown"


def test_django_field_mapping_special_cases():
    from types import SimpleNamespace

    from fastadmin.models.orms.django import DjangoModelAdmin

    def make_field(class_name, name, *, null=True):
        cls = type(class_name, (), {})
        field = cls()
        field.name = name
        field.primary_key = False
        field.auto_now = False
        field.auto_now_add = False
        field.null = null
        field.default = False
        field.choices = None
        return field

    fields = [
        make_field("ArrayField", "tags"),
        make_field("FileField", "file"),
        make_field("URLField", "website"),
        make_field("EmailField", "email"),
        make_field("SlugField", "slug"),
    ]

    class FakeModel:
        _meta = SimpleNamespace(get_fields=lambda: fields)

    admin = DjangoModelAdmin(FakeModel)
    admin.formfield_overrides = {}
    mapped = admin.get_model_fields_with_widget_types()
    by_name = {f.name: f for f in mapped}

    assert by_name["tags"].form_widget_type == WidgetType.Select
    assert by_name["tags"].form_widget_props["mode"] == "tags"
    assert by_name["tags"].filter_widget_props["mode"] == "tags"
    assert by_name["file"].form_widget_type == WidgetType.Upload
    assert by_name["website"].form_widget_type == WidgetType.UrlInput
    assert by_name["email"].form_widget_type == WidgetType.EmailInput
    assert by_name["slug"].form_widget_type == WidgetType.SlugInput


def test_django_with_upload_false_skips_upload_via_override():
    from types import SimpleNamespace

    from fastadmin.models.orms.django import DjangoModelAdmin

    char_field = type("CharField", (), {})()
    char_field.name = "username"
    char_field.primary_key = False
    char_field.auto_now = False
    char_field.auto_now_add = False
    char_field.null = False
    char_field.default = False
    char_field.choices = None

    class FakeModel:
        _meta = SimpleNamespace(get_fields=lambda: [char_field])

    admin = DjangoModelAdmin(FakeModel)
    admin.formfield_overrides = {"username": (WidgetType.Upload, {})}
    mapped = admin.get_model_fields_with_widget_types(with_upload=False)
    assert mapped == []


async def test_django_orm_save_upload_field():
    from types import SimpleNamespace

    from fastadmin.models.orms.django import DjangoModelAdmin

    class FakeModel:
        _meta = SimpleNamespace(pk=SimpleNamespace(name="id"), get_fields=list)

    class CaptureFile:
        def __init__(self):
            self.called = False
            self.name = None
            self.data = None
            self.save_flag = None

        def save(self, name, data, save=True):
            self.called = True
            self.name = name
            self.data = data.read()
            self.save_flag = save

    obj = SimpleNamespace(avatar=CaptureFile())
    admin = DjangoModelAdmin(FakeModel)
    await admin.orm_save_upload_field(obj, "avatar", "data:image/png;base64,aGVsbG8=")

    assert obj.avatar.called is True
    assert obj.avatar.name == "image.png"
    assert obj.avatar.data == b"hello"
    assert obj.avatar.save_flag is True
