import asyncio
from collections import OrderedDict
from typing import Any

from fastapi import HTTPException, status

from fastadmin.models.base import BaseModelAdmin
from fastadmin.models.helpers import get_admin_model
from fastadmin.schemas.configuration import WidgetType
from fastadmin.settings import settings


class TortoiseModelAdmin(BaseModelAdmin):
    async def save_model(self, id: str | None, payload: dict) -> Any | None:
        """This method is used to save orm/db model object.

        :params id: an id of object.
        :params payload: a payload from request.
        :return: A saved object or None.
        """
        fields = self.get_model_fields()
        m2m_fields = [f for f, v in fields.items() if v.get("is_m2m", False)]

        if id:
            obj = await self.model_cls.filter(id=id).first()
            if not obj:
                return None
        else:
            obj = self.model_cls()

        update_fields = []
        for key, value in payload.items():
            if key not in m2m_fields:
                setattr(obj, key, value)
                update_fields.append(key)

        await obj.save(update_fields=update_fields if id else None)

        for key, values in payload.items():
            if key in m2m_fields:
                m2m_rel = getattr(obj, key, None)
                if m2m_rel is None:
                    continue
                remote_model = m2m_rel.remote_model
                await m2m_rel.clear()
                remote_model_objs = []
                for id in values:
                    remote_model_obj = remote_model()
                    setattr(remote_model_obj, remote_model._meta.pk_attr, id)
                    setattr(remote_model_obj, "_saved_in_db", True)
                    remote_model_objs.append(remote_model_obj)
                if remote_model_objs:
                    await m2m_rel.add(*remote_model_objs)
        return obj

    async def delete_model(self, obj: Any) -> None:
        """This method is used to delete orm/db model object.

        :params obj: an orm/db model object.
        :return: None.
        """
        await obj.delete()

    async def get_obj(self, id: str) -> Any | None:
        """This method is used to get orm/db model object by id.

        :params id: an id of object.
        :return: An object or None.
        """
        fields = self.get_model_fields()
        m2m_fields = [f for f, v in fields.items() if v.get("is_m2m", False)]
        obj = await self.model_cls.filter(id=id).first()
        if not obj:
            return obj
        obj_dict = {k: v for k, v in obj.__dict__.items() if not k.startswith("_")}
        for field in m2m_fields:
            m2m_rel = getattr(obj, field, None)
            if m2m_rel is None:
                continue
            remote_model = m2m_rel.remote_model
            remote_ids = await m2m_rel.all().values_list(remote_model._meta.pk_attr, flat=True)
            obj_dict[field] = remote_ids
        return obj_dict

    async def get_list(
        self,
        offset: int | None = None,
        limit: int | None = None,
        search: str | None = None,
        sort_by: str | None = None,
        filters: dict | None = None,
    ) -> tuple[list[Any], int]:
        """This method is used to get list of orm/db model objects.

        :params offset: an offset for pagination.
        :params limit: a limit for pagination.
        :params search: a search query.
        :params sort_by: a sort by field name.
        :params filters: a dict of filters.
        :return: A tuple of list of objects and total count.
        """
        qs = self.model_cls.all()

        fields = self.get_model_fields()

        if filters:
            for filter_condition, value in filters.items():
                field = filter_condition.split("__", 1)[0]
                if field not in fields:
                    raise HTTPException(
                        status.HTTP_400_BAD_REQUEST, detail=f"Filter by {filter_condition} is not allowed"
                    )
                qs = qs.filter(**{filter_condition: value})

        if search:
            if self.search_fields:
                for field in self.search_fields:
                    if field not in fields:
                        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=f"Search by {field} is not allowed")
                ids = await asyncio.gather(
                    *(qs.filter(**{f + "__icontains": search}).values_list("id", flat=True) for f in self.search_fields)
                )
                ids = [item for sublist in ids for item in sublist]
                qs = qs.filter(id__in=ids)

        if sort_by:
            if sort_by.strip("-") not in fields:
                raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=f"Sort by {sort_by} is not allowed")
            qs = qs.order_by(sort_by)
        else:
            if self.ordering:
                if self.ordering.strip("-") not in fields:
                    raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=f"Sort by {self.ordering} is not allowed")
                qs = qs.order_by(*self.ordering)

        total = await qs.count()

        if offset is not None and limit is not None:
            qs = qs.offset(offset)
            qs = qs.limit(limit)

        if self.list_select_related:
            for field in self.list_select_related:
                if field not in fields:
                    raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=f"Select related by {field} is not allowed")
            qs = qs.select_related(*self.list_select_related)

        return await qs, total

    def get_model_fields(self) -> OrderedDict[str, dict]:
        """This method is used to get all orm/db model fields
        with saving ordering (non relations, fk, o2o, m2m).

        :return: An OrderedDict of model fields.
        """
        if hasattr(self, "_model_fields"):
            return self._model_fields

        protection_fields = self.model_cls._meta.fields_db_projection.keys()
        fk_fields = self.model_cls._meta.fk_fields
        o2o_fields = self.model_cls._meta.o2o_fields
        m2m_fields = self.model_cls._meta.m2m_fields

        fields = OrderedDict()
        for field_name, field in self.model_cls._meta.fields_map.items():
            if field_name not in protection_fields and field_name not in m2m_fields:
                continue
            field = getattr(field, "reference", None) or field
            parent_model_id = None
            parent_model_label = None
            parent_model = getattr(field, "model_name", "").rsplit(".", 1)[-1] or None
            if parent_model:
                parent_admin_model = get_admin_model(parent_model)
                parent_model_id = "id"
                parent_model_label = "id"
                if parent_admin_model:
                    parent_model_id = parent_admin_model.model_cls._meta.pk_attr
                    parent_model_label = parent_admin_model.model_cls._meta.pk_attr
                    parent_fields = parent_admin_model.model_cls._meta.fields_db_projection.keys()
                    if "name" in parent_fields:
                        parent_model_label = "name"
                    elif "title" in parent_fields:
                        parent_model_label = "title"
                    elif "email" in parent_fields:
                        parent_model_label = "email"

            form_hidden = (
                getattr(field, "_generated", False)
                or getattr(field, "index", False)
                or getattr(field, "auto_now", False)
                or getattr(field, "auto_now_add", False)
            )

            fields[field_name] = {
                "is_pk": getattr(field, "index", False),
                "is_m2m": field_name in m2m_fields,
                "is_fk": field_name in fk_fields,
                "is_o2o": field_name in o2o_fields,
                "orm_class_name": field.__class__.__name__,
                "parent_model": parent_model,
                "parent_model_id": parent_model_id,
                "parent_model_label": parent_model_label,
                "enum_type": getattr(field, "enum_type", None),
                "required": not getattr(field, "null", False)
                and not getattr(field, "default", False)
                and field_name not in m2m_fields,
                "form_hidden": form_hidden,
            }

        setattr(self, "_model_fields", fields)
        return fields

    def get_form_widget(self, field_name: str) -> tuple[WidgetType, dict]:
        """This method is used to get form item widget
        for field from orm/db model.

        :params field_name: a model field name.
        :return: A tuple of widget type and widget props.
        """
        fields = self.get_model_fields()
        field = fields.get(field_name)
        if not field:
            raise Exception("Invalid field name %s" % field_name)
        widget_props = {
            "required": field.get("required") or False,
            "disabled": field_name in self.readonly_fields,
            "readonly": field_name in self.readonly_fields,
        }
        match field.get("orm_class_name"):
            case "CharField":
                return WidgetType.Input, widget_props
            case "TextField":
                return WidgetType.TextArea, widget_props
            case "BooleanField":
                return WidgetType.Switch, {
                    **widget_props,
                    "required": False,
                }
            case "ArrayField":
                return WidgetType.Select, {
                    **widget_props,
                    "mode": "tags",
                }
            case "IntField":
                return WidgetType.InputNumber, widget_props
            case "FloatField":
                return WidgetType.InputNumber, widget_props
            case "DecimalField":
                return WidgetType.InputNumber, widget_props
            case "DateField":
                return WidgetType.DatePicker, {
                    **widget_props,
                    "format": settings.ADMIN_DATE_FORMAT,
                }
            case "DatetimeField":
                return WidgetType.DateTimePicker, {
                    **widget_props,
                    "format": settings.ADMIN_DATETIME_FORMAT,
                }
            case "TimeField":
                return WidgetType.TimePicker, {
                    **widget_props,
                    "format": settings.ADMIN_TIME_FORMAT,
                }
            case "ForeignKeyFieldInstance":
                if field_name in self.raw_id_fields:
                    return WidgetType.Input, widget_props
                return WidgetType.AsyncSelect, {
                    **widget_props,
                    "parentModel": field.get("parent_model"),
                    "idField": field.get("parent_model_id") or "id",
                    "labelField": field.get("parent_model_label") or "id",
                }
            case "ManyToManyFieldInstance":
                if field_name in self.raw_id_fields:
                    return WidgetType.Input, widget_props
                if field_name in self.filter_vertical or field_name in self.filter_horizontal:
                    return WidgetType.AsyncTransfer, {
                        **widget_props,
                        "required": False,
                        "parentModel": field.get("parent_model"),
                        "idField": field.get("parent_model_id") or "id",
                        "labelField": field.get("parent_model_label") or "id",
                        "layout": "vertical" if field in self.filter_vertical else "horizontal",
                    }
                return WidgetType.AsyncSelect, {
                    **widget_props,
                    "required": False,
                    "mode": "multiple",
                    "parentModel": field.get("parent_model"),
                    "idField": field.get("parent_model_id") or "id",
                    "labelField": field.get("parent_model_label") or "id",
                }
            case "OneToOneFieldInstance":
                if field_name in self.raw_id_fields:
                    return WidgetType.Input, widget_props
                return WidgetType.AsyncSelect, {
                    **widget_props,
                    "parentModel": field.get("parent_model"),
                    "idField": field.get("parent_model_id") or "id",
                    "labelField": field.get("parent_model_label") or "id",
                }
            case "CharEnumFieldInstance":
                if field_name in self.radio_fields:
                    return WidgetType.RadioGroup, {
                        **widget_props,
                        "options": [{"label": k, "value": k} for k in field.get("enum_type") or []],
                    }
                return WidgetType.Select, {
                    **widget_props,
                    "options": [{"label": k, "value": k} for k in field.get("enum_type") or []],
                }
        return WidgetType.Input, widget_props
