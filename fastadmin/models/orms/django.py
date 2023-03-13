import asyncio
import inspect
from collections import OrderedDict
from typing import Any
from uuid import UUID

from asgiref.sync import sync_to_async

from fastadmin.models.base import InlineModelAdmin, ModelAdmin
from fastadmin.models.helpers import get_admin_model
from fastadmin.models.schemas import WidgetType
from fastadmin.settings import settings


class DjangoORMMixin:
    @sync_to_async
    def _sync_delete(self, qs: Any) -> None:
        """Deletes all objects from queryset.

        :params qs: a queryset.
        :return: None.
        """
        return qs.delete()

    @sync_to_async
    def _sync_first(self, qs: Any) -> Any | None:
        """Returns first object from queryset.

        :params qs: a queryset.
        :return: An object or None.
        """
        return qs.first()

    @sync_to_async
    def _sync_count(self, qs) -> int:
        """Returns count of objects from queryset.

        :params qs: a queryset.
        :return: An int.
        """
        return qs.count()

    @sync_to_async
    def _sync_list(self, qs) -> list[Any]:
        """Returns list of objects from queryset.

        :params qs: a queryset.
        :return: A list.
        """
        return list(qs)

    @sync_to_async
    def _sync_save(self, obj, *args, **kwargs) -> None:
        """Saves an object.

        :params obj: an object.
        :return: None.
        """
        return obj.save(*args, **kwargs)

    @sync_to_async
    def _sync_set(self, qs, *args, **kwargs) -> None:
        """Sets m2m fields.

        :params qs: a queryset.
        :return: None.
        """
        return qs.set(*args, **kwargs)

    @sync_to_async
    def _sync_values_list(self, qs, *args, **kwargs) -> list[Any]:
        """Returns list of values from queryset.

        :params qs: a queryset.
        :return: A list.
        """
        return list(qs.values_list(*args, **kwargs))

    async def _obj_to_dict(self, obj: Any, with_m2m: bool = True, with_display_fields: bool = False) -> dict:
        """Converts orm model obj to dict.

        :params obj: an object.
        :params with_m2m: a flag to include m2m fields.
        :params with_display_fields: a flag to include display fields.
        :return: A dict.
        """
        obj_dict = {k: v for k, v in obj.__dict__.items() if not k.startswith("_")}
        if with_m2m:
            fields = self.get_model_fields()
            m2m_fields = [f for f, v in fields.items() if v.get("is_m2m", False)]
            for field in m2m_fields:
                m2m_rel = getattr(obj, field)
                remote_model = m2m_rel.model
                qs = m2m_rel.all()
                remote_ids = await self._sync_values_list(qs, remote_model._meta.pk.name, flat=True)
                obj_dict[field] = remote_ids
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

        all_fields = self.model_cls._meta.get_fields()
        protection_fields = {f.name for f in self.model_cls._meta.fields}
        fk_fields = {f.name for f in all_fields if f.__class__.__name__ == "ForeignKey" and f.is_relation}
        o2o_fields = {f.name for f in all_fields if f.__class__.__name__ == "OneToOneField" and f.is_relation}
        m2m_fields = {f.name for f in all_fields if f.__class__.__name__ == "ManyToManyField" and f.is_relation}

        fields = OrderedDict()
        for field in all_fields:
            field_name = field.name
            if field_name not in protection_fields and field_name not in m2m_fields:
                continue
            parent_model_id = None
            parent_model_labels = ()
            parent_model = getattr(field, "related_model", None)
            if parent_model:
                parent_admin_model = get_admin_model(parent_model)
                parent_model_id = "id"
                parent_model_labels = ("id",)
                if parent_admin_model:
                    parent_model_id = parent_admin_model.model_cls._meta.pk.name
                    parent_model_labels = parent_admin_model.label_fields or (parent_model_id,)

            form_hidden = (
                getattr(field, "primary_key", False)
                or getattr(field, "auto_now", False)
                or getattr(field, "auto_now_add", False)
            )
            choices = None
            choices_tuple = getattr(field, "choices", None)
            if choices_tuple is not None:
                choices = {item[0]: item[1] for item in choices_tuple}
            fields[field_name] = {
                "is_pk": getattr(field, "primary_key", False),
                "is_m2m": field_name in m2m_fields,
                "is_fk": field_name in fk_fields,
                "is_o2o": field_name in o2o_fields,
                "orm_class_name": field.__class__.__name__,
                "parent_model": parent_model.__name__ if parent_model else None,
                "parent_model_id": parent_model_id,
                "parent_model_labels": parent_model_labels,
                "choices": choices,
                "required": not getattr(field, "null", False)
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
        fields = self.get_model_fields()
        m2m_fields = [f for f, v in fields.items() if v.get("is_m2m", False)]

        if id:
            qs = self.model_cls.objects.filter(id=id)
            obj = await self._sync_first(qs)
            if not obj:
                return None
        else:
            obj = self.model_cls()

        update_fields = []
        for key, value in payload.items():
            if key not in m2m_fields:
                setattr(obj, key, value)
                update_fields.append(key)

        await self._sync_save(obj, update_fields=update_fields if id else None)

        for key, values in payload.items():
            if key in m2m_fields:
                if values:
                    m2m_rel = getattr(obj, key)
                    await self._sync_set(m2m_rel, values)

        return await self._obj_to_dict(obj)

    async def delete_model(self, id: UUID | int) -> None:
        """This method is used to delete orm/db model object.

        :params id: an id of object.
        :return: None.
        """
        qs = self.model_cls.objects.filter(id=id)
        await self._sync_delete(qs)

    async def get_obj(self, id: UUID | int) -> dict | None:
        """This method is used to get orm/db model object by id.

        :params id: an id of object.
        :return: An object or None.
        """
        qs = self.model_cls.objects.filter(id=id)
        obj = await self._sync_first(qs)
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
        qs = self.model_cls.objects.all()

        if filters:
            for filter_condition, value in filters.items():
                qs = qs.filter(**{filter_condition: value})

        if search and self.search_fields:
            ids = []
            for f in self.search_fields:
                qs = qs.filter(**{f + "__icontains": search})
                ids += await self._sync_values_list(qs, self.model_cls._meta.pk.name, flat=True)
            qs = qs.filter(id__in=set(ids))

        if sort_by:
            qs = qs.order_by(sort_by)
        elif self.ordering:
            qs = qs.order_by(*self.ordering)

        total = await self._sync_count(qs)

        if self.list_select_related:
            qs = qs.select_related(*self.list_select_related)

        if offset is not None and limit is not None:
            qs = qs[offset : offset + limit]

        results = await asyncio.gather(
            *(self._obj_to_dict(obj, with_m2m=False, with_display_fields=True) for obj in await self._sync_list(qs))
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
            case "CharField":
                choices = field.get("choices")
                if choices is not None:
                    if field_name in self.radio_fields:
                        return WidgetType.RadioGroup, {
                            **widget_props,
                            "options": [{"label": k, "value": k} for k in field.get("choices") or []],
                        }
                    return WidgetType.Select, {
                        **widget_props,
                        "options": [{"label": k, "value": k} for k in field.get("choices") or []],
                    }
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
            case "IntegerField":
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
            case "DateTimeField":
                return WidgetType.DateTimePicker, {
                    **widget_props,
                    "format": settings.ADMIN_DATETIME_FORMAT,
                }
            case "TimeField":
                return WidgetType.TimePicker, {
                    **widget_props,
                    "format": settings.ADMIN_TIME_FORMAT,
                }
            case "ForeignKey":
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
        return WidgetType.Input, widget_props


class DjangoModelAdmin(DjangoORMMixin, ModelAdmin):
    pass


class DjangoInlineModelAdmin(DjangoORMMixin, InlineModelAdmin):
    pass
