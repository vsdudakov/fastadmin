from fastadmin.models.orms.sqlalchemy import SqlAlchemyMixin
from fastadmin.models.schemas import WidgetType


def test_get_form_widget(mocker):
    mocker.patch.object(
        SqlAlchemyMixin,
        "get_model_fields",
        return_value={
            "tags": {
                "is_pk": False,
                "is_m2m": False,
                "is_fk": False,
                "is_o2o": False,
                "orm_class_name": "ArrayField",
                "parent_model": None,
                "parent_model_id": None,
                "parent_model_labels": None,
                "choices": None,
                "required": False,
                "form_hidden": False,
            }
        },
    )
    orm = SqlAlchemyMixin()
    orm.readonly_fields = []
    widget_type, widget_props = orm.get_form_widget("tags")
    assert widget_type == WidgetType.Select
    assert "tags" == widget_props["mode"]
