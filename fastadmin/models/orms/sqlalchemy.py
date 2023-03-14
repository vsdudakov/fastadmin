import asyncio
import inspect
from collections import OrderedDict
from operator import attrgetter
from typing import Any
from uuid import UUID

from fastadmin.models.base import InlineModelAdmin, ModelAdmin
from fastadmin.models.helpers import get_admin_model
from fastadmin.models.schemas import WidgetType
from fastadmin.settings import settings


def get_attrs(obj: Any, keys: str) -> Any | None:
    try:
        return attrgetter(keys)(obj)
    except (TypeError, AttributeError):
        return None


def convert_sort_by(sort_by: str) -> str:
    if sort_by.startswith("-"):
        return sort_by[1:] + " desc"
    return sort_by

class SqlAlchemyMixin:
    sqlalchemy_session = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.sqlalchemy_session:
            raise ValueError("%s: sqlalchemy_session is not defined.", self.__class__.__name__)

    async def _obj_to_dict(self, obj: Any, with_m2m: bool = True, with_display_fields: bool = False) -> dict:
        """Converts orm model obj to dict.

        :params obj: an object.
        :params with_m2m: a flag to include m2m fields.
        :params with_display_fields: a flag to include display fields.
        :return: A dict.
        """
        obj_dict = {k: v for k, v in obj.__dict__.items() if not k.startswith("_")}
        # if with_m2m:
        #     fields = self.get_model_fields()
        #     m2m_fields = [f for f, v in fields.items() if v.get("is_m2m", False)]
        #     for field in m2m_fields:
        #         m2m_results = await getattr(obj, field)
        #         m2m_result_ids = [m2m_result.id for m2m_result in m2m_results]
        #         await self.sqlalchemy_session.refresh(obj)
        #         obj_dict[field] = m2m_result_ids
        if with_display_fields:
            if admin_model := get_admin_model(obj.__class__):
                for field in admin_model.list_display:
                    display_field_function = getattr(admin_model, field, None)
                    if (
                        not display_field_function
                        or not inspect.ismethod(display_field_function)
                        or not hasattr(display_field_function, "is_display")
                    ):
                        continue
                    obj_dict[field] = await display_field_function(obj)
        return obj_dict

    def get_model_fields(self) -> OrderedDict[str, dict]:
        """This method is used to get all orm/db model fields
        with saving ordering (non relations, fk, o2o, m2m).

        :return: An OrderedDict of model fields.
        """
        if hasattr(self, "_model_fields"):
            return self._model_fields

        from sqlalchemy import inspect

        mapper = inspect(self.model_cls)

        # TODO remove backward relations, identify o2o correctly
        all_fields = {f for f in mapper.c if not f.foreign_keys} | {f for f in mapper.relationships}
        fk_fields = [f.key for f in mapper.relationships if f.direction.name == "MANYTOONE"]
        o2o_fields = [f.key for f in mapper.relationships if f.direction.name == "MANYTOONE"]
        m2m_fields = [f.key for f in mapper.relationships if f.direction.name == "MANYTOMANY"]
        protection_fields = [f.key for f in all_fields if f.key not in m2m_fields]

        fields = OrderedDict()
        for field in all_fields:
            field_name = field.key
            if field_name not in protection_fields and field_name not in m2m_fields:
                continue

            parent_model_id = None
            parent_model_labels = ()
            parent_model = get_attrs(field, "entity.class_")
            if parent_model:
                parent_admin_model = get_admin_model(parent_model)
                parent_model_id = "id"
                parent_model_labels = ("id",)
                if parent_admin_model:
                    parent_model_id = (
                        get_attrs(parent_admin_model.model_cls, "__table__.primary_key._autoincrement_column.name")
                        or "id"
                    )
                    parent_model_labels = parent_admin_model.label_fields or (parent_model_id,)

            form_hidden = getattr(field, "primary_key", False)

            orm_class_name = get_attrs(field, "type.__class__.__name__")
            if field_name in o2o_fields:
                orm_class_name = "OneToOneField"
            if field_name in fk_fields:
                orm_class_name = "ForeignKeyField"
            if field_name in m2m_fields:
                orm_class_name = "ManyToManyField"

            fields[field_name] = {
                "is_pk": getattr(field, "primary_key", False),
                "is_m2m": field_name in m2m_fields,
                "is_fk": field_name in fk_fields,
                "is_o2o": field_name in o2o_fields,
                "orm_class_name": orm_class_name,
                "parent_model": parent_model.__name__ if parent_model else None,
                "parent_model_id": parent_model_id,
                "parent_model_labels": parent_model_labels,
                "choices": getattr(field, "enum_type", None),
                "required": not getattr(field, "nullable", False)
                and not getattr(field, "default", False)
                and field_name not in m2m_fields,
                "form_hidden": form_hidden,
            }

        setattr(self, "_model_fields", fields)
        return fields

    async def save_model(self, id: UUID | int | None, payload: dict) -> dict | None:
        """This method is used to save orm/db model object.

        :params id: an id of object.
        :params payload: a payload from request.
        :return: A saved object or None.
        """
        async with self.sqlalchemy_session() as session:  # type: ignore
            fields = self.get_model_fields()
            m2m_fields = [f for f, v in fields.items() if v.get("is_m2m", False)]

            if id:
                obj = await session.get(self.model_cls, id)
                if not obj:
                    return None
            else:
                obj = self.model_cls()

            update_fields = []
            for key, value in payload.items():
                if key not in m2m_fields:
                    setattr(obj, key, value)
                    update_fields.append(key)

            if id is None:
                session.add(obj)
            await session.commit()
            await session.refresh(obj)

            # for key, values in payload.items():
            #     if key in m2m_fields:
            #         m2m_rel = getattr(obj, key)
            #         remote_model = m2m_rel.remote_model
            #         await m2m_rel.clear()
            #         remote_model_objs = []
            #         for id in values:
            #             remote_model_obj = remote_model()
            #             setattr(remote_model_obj, remote_model._meta.pk_attr, id)
            #             setattr(remote_model_obj, "_saved_in_db", True)
            #             remote_model_objs.append(remote_model_obj)
            #         if remote_model_objs:
            #             await m2m_rel.add(*remote_model_objs)
            return await self._obj_to_dict(obj)

    async def delete_model(self, id: UUID | int) -> None:
        """This method is used to delete orm/db model object.

        :params id: an id of object.
        :return: None.
        """
        from sqlalchemy import delete

        async with self.sqlalchemy_session() as session:  # type: ignore
            query = delete(self.model_cls).filter_by(id=id)
            await session.execute(query)
            await session.commit()

    async def get_obj(self, id: UUID | int) -> dict | None:
        """This method is used to get orm/db model object by id.

        :params id: an id of object.
        :return: An object or None.
        """
        from sqlalchemy import select

        async with self.sqlalchemy_session() as session:  # type: ignore
            query = select(self.model_cls).filter_by(id=id).limit(1)
            result = await session.scalars(query)
            obj = result.first()
            if not obj:
                return None
            return await self._obj_to_dict(obj)

    async def get_list(
        self,
        offset: int | None = None,
        limit: int | None = None,
        search: str | None = None,
        sort_by: str | None = None,
        filters: dict | None = None,
    ) -> tuple[list[dict], int]:
        """This method is used to get list of orm/db model objects.

        :params offset: an offset for pagination.
        :params limit: a limit for pagination.
        :params search: a search query.
        :params sort_by: a sort by field name.
        :params filters: a dict of filters.
        :return: A tuple of list of objects and total count.
        """
        from sqlalchemy import func, select, text
        async with self.sqlalchemy_session() as session:  # type: ignore
            qs = select(self.model_cls)

            # if filters:
            #     for filter_condition, value in filters.items():
            #         qs = qs.filter_by(**{filter_condition: value})

            # if search and self.search_fields:
            #     ids = await asyncio.gather(
            #         *(
            #             qs.filter(**{f + "__icontains": search}).values_list(self.model_cls._meta.pk_attr, flat=True)
            #             for f in self.search_fields
            #         )
            #     )
            #     ids = [item for sublist in ids for item in sublist]
            #     qs = qs.filter(id__in=ids)

            if sort_by:
                qs = qs.order_by(text(convert_sort_by(sort_by)))
            elif self.ordering:
                sort_by_text = ", ".join([convert_sort_by(f) for f in self.ordering])
                qs = qs.order_by(text(sort_by_text))


            objs = await session.execute(select(func.count()).select_from(qs))
            total = objs.scalar()

            if offset is not None and limit is not None:
                qs = qs.offset(offset)
                qs = qs.limit(limit)

            # if self.list_select_related:
            #     qs = qs.select_related(*self.list_select_related)

            objs = await session.scalars(qs)
            results = await asyncio.gather(
                *(self._obj_to_dict(obj, with_m2m=False, with_display_fields=True) for obj in objs)
            )
            return results, total

    def get_form_widget(self, field_name: str) -> tuple[WidgetType, dict]:
        """This method is used to get form item widget
        for field from orm/db model.

        :params field_name: a model field name.
        :return: A tuple of widget type and widget props.
        """
        fields = self.get_model_fields()
        field = fields[field_name]
        widget_props = {
            "required": field.get("required") or False,
            "disabled": field_name in self.readonly_fields,
            "readOnly": field_name in self.readonly_fields,
        }
        match field.get("orm_class_name"):
            case "String":
                return WidgetType.Input, widget_props
            case "Text":
                return WidgetType.TextArea, widget_props
            case "Boolean":
                return WidgetType.Switch, {
                    **widget_props,
                    "required": False,
                }
            # case "Array":
            #     return WidgetType.Select, {
            #         **widget_props,
            #         "mode": "tags",
            #     }
            case "Integer":
                return WidgetType.InputNumber, widget_props
            case "Float":
                return WidgetType.InputNumber, widget_props
            # case "Decimal":
            #     return WidgetType.InputNumber, widget_props
            case "Date":
                return WidgetType.DatePicker, {
                    **widget_props,
                    "format": settings.ADMIN_DATE_FORMAT,
                }
            case "DateTime":
                return WidgetType.DateTimePicker, {
                    **widget_props,
                    "format": settings.ADMIN_DATETIME_FORMAT,
                }
            case "Time":
                return WidgetType.TimePicker, {
                    **widget_props,
                    "format": settings.ADMIN_TIME_FORMAT,
                }
            case "ForeignKeyField":
                if field_name in self.raw_id_fields:
                    return WidgetType.Input, widget_props
                return WidgetType.AsyncSelect, {
                    **widget_props,
                    "parentModel": field.get("parent_model"),
                    "idField": field.get("parent_model_id"),
                    "labelFields": field.get("parent_model_labels"),
                }
            case "ManyToManyField":
                if field_name in self.raw_id_fields:
                    return WidgetType.Input, widget_props
                if field_name in self.filter_vertical or field_name in self.filter_horizontal:
                    return WidgetType.AsyncTransfer, {
                        **widget_props,
                        "required": False,
                        "parentModel": field.get("parent_model"),
                        "idField": field.get("parent_model_id"),
                        "labelFields": field.get("parent_model_labels"),
                        "layout": "vertical" if field in self.filter_vertical else "horizontal",
                    }
                return WidgetType.AsyncSelect, {
                    **widget_props,
                    "required": False,
                    "mode": "multiple",
                    "parentModel": field.get("parent_model"),
                    "idField": field.get("parent_model_id"),
                    "labelFields": field.get("parent_model_labels"),
                }
            case "OneToOneField":
                if field_name in self.raw_id_fields:
                    return WidgetType.Input, widget_props
                return WidgetType.AsyncSelect, {
                    **widget_props,
                    "parentModel": field.get("parent_model"),
                    "idField": field.get("parent_model_id"),
                    "labelFields": field.get("parent_model_labels"),
                }
            # case "CharEnumFieldInstance":
            #     if field_name in self.radio_fields:
            #         return WidgetType.RadioGroup, {
            #             **widget_props,
            #             "options": [{"label": k, "value": k} for k in field.get("choices") or []],
            #         }
            #     return WidgetType.Select, {
            #         **widget_props,
            #         "options": [{"label": k, "value": k} for k in field.get("choices") or []],
            #     }
        return WidgetType.Input, widget_props


class SqlAlchemyModelAdmin(SqlAlchemyMixin, ModelAdmin):
    pass


class SqlAlchemyInlineModelAdmin(SqlAlchemyMixin, InlineModelAdmin):
    pass
