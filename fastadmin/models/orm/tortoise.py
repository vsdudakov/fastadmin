import asyncio
import csv
from io import BytesIO, StringIO
from typing import Any, Sequence

from fastapi import HTTPException, status

from fastadmin.models.base import BaseModelAdmin
from fastadmin.schemas.api import ExportFormat
from fastadmin.schemas.configuration import WidgetType


class TortoiseModelAdmin(BaseModelAdmin):
    def _get_model_fields(self) -> list[str]:
        fields = [f for f in self.model_cls._meta.fields_db_projection.keys()]
        for m2m_field in self.model_cls._meta.m2m_fields:
            fields.append(m2m_field)
        return fields

    async def save_model(self, obj: Any, payload: dict, add: bool = False) -> None:
        for key, value in payload.items():
            setattr(obj, key, value)
        await obj.save(update_fields=payload.keys() if not add else None)

    async def delete_model(self, obj: Any) -> None:
        await obj.delete()

    async def get_obj(self, id: str) -> Any | None:
        return await self.model_cls.filter(id=id).first()

    async def get_list(
        self,
        offset: int | None = None,
        limit: int | None = None,
        search: str | None = None,
        sort_by: str | None = None,
        filters: dict | None = None,
    ) -> tuple[list[Any], int]:
        qs = self.model_cls.all()

        fields = self._get_model_fields()

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

    async def get_export(
        self,
        export_format: ExportFormat | None,
        offset: int | None = None,
        limit: int | None = None,
        search: str | None = None,
        sort_by: str | None = None,
        filters: dict | None = None,
    ) -> StringIO | BytesIO | None:
        objs, _ = await self.get_list(offset=offset, limit=limit, search=search, sort_by=sort_by, filters=filters)
        fields = self._get_model_fields()
        hidden_fields = await self.get_hidden_fields()
        m2m_fields = self.model_cls._meta.m2m_fields
        fieldnames = [f for f in fields if f not in hidden_fields and f not in m2m_fields]
        if not export_format or export_format == ExportFormat.CSV:
            output = StringIO()
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            for obj in objs:
                obj_dict = {fieldname: getattr(obj, fieldname, None) for fieldname in fieldnames}
                writer.writerow(obj_dict)
            output.seek(0)
            return output
        return None

    def get_form_widget(self, field: str) -> tuple[WidgetType, dict]:
        field_obj = self.model_cls._meta.fields_map[field]
        field_obj = field_obj.reference if field_obj.reference else field_obj
        widget_props = {
            "required": not field_obj.null and not field_obj.default,
            "disabled": field in self.readonly_fields,
            "readonly": field in self.readonly_fields,
        }
        field_class = field_obj.__class__.__name__
        if field_class == "CharField":
            return WidgetType.Input, widget_props
        if field_class == "TextField":
            return WidgetType.TextArea, widget_props
        if field_class == "BooleanField":
            return WidgetType.Switch, {**widget_props, "required": False}
        if field_class == "ArrayField":
            return WidgetType.Select, {
                **widget_props,
                "mode": "tags",
            }
        if field_class == "IntField":
            return WidgetType.InputNumber, widget_props
        if field_class == "FloatField":
            return WidgetType.InputNumber, widget_props
        if field_class == "DecimalField":
            return WidgetType.InputNumber, widget_props
        if field_class == "DateField":
            return WidgetType.DatePicker, widget_props
        if field_class == "DatetimeField":
            return WidgetType.DateTimePicker, widget_props
        if field_class == "TimeField":
            return WidgetType.TimePicker, widget_props
        if field_class == "ForeignKeyFieldInstance":
            if field in self.raw_id_fields:
                return WidgetType.Input, widget_props
            return WidgetType.AsyncSelect, {
                **widget_props,
                "parentModel": field_obj.model_name.rsplit(".", 1)[-1],
                "idField": "id",
                "labelField": "username",
            }
        if field_class == "ManyToManyFieldInstance":
            if field in self.raw_id_fields:
                return WidgetType.Input, widget_props
            if field in self.filter_vertical or field in self.filter_horizontal:
                return WidgetType.AsyncTransfer, {
                    **widget_props,
                    "required": False,
                    "parentModel": field_obj.model_name.rsplit(".", 1)[-1],
                    "idField": "id",
                    "labelField": "id",  # TODO: labelField
                    "layout": "vertical" if field in self.filter_vertical else "horizontal",
                }
            return WidgetType.AsyncSelect, {
                **widget_props,
                "required": False,
                "mode": "multiple",
                "parentModel": field_obj.model_name.rsplit(".", 1)[-1],
                "idField": "id",
                "labelField": "id",  # TODO: labelField
            }
        if field_class == "OneToOneFieldInstance":
            if field in self.raw_id_fields:
                return WidgetType.Input, widget_props
            return WidgetType.AsyncSelect, {
                **widget_props,
                "parentModel": field_obj.model_name.rsplit(".", 1)[-1],
                "idField": "id",
                "labelField": "id",  # TODO: labelField
            }
        if field_class == "CharEnumFieldInstance":
            return WidgetType.RadioGroup if field in self.radio_fields else WidgetType.Select, {
                **widget_props,
                "options": [{"label": k, "value": k} for k in field_obj.enum_type],
            }
        return WidgetType.Input, widget_props

    def get_fields(self) -> Sequence[str]:
        fields = super().get_fields()
        model_fields = self._get_model_fields()
        if not fields:
            if self.exclude:
                return [f for f in model_fields if f not in self.exclude]
            return model_fields
        return [f for f in fields if f in model_fields]

    def get_list_display(self) -> Sequence[str]:
        list_display = super().get_list_display()
        fields_map = self.model_cls._meta.fields_map
        model_fields = self._get_model_fields()
        if not list_display:
            return [f for f in model_fields if getattr(fields_map[f], "index", True)]
        return [f for f in list_display if f in model_fields]

    def get_form_hidden_fields(self) -> Sequence[str]:
        fields_map = self.model_cls._meta.fields_map
        form_hidden_fields = super().get_form_hidden_fields()
        model_fields = self._get_model_fields()
        if not form_hidden_fields:
            return [
                f
                for f in model_fields
                if (
                    getattr(fields_map[f], "_generated", False)
                    or getattr(fields_map[f], "index", False)
                    or getattr(fields_map[f], "auto_now", False)
                    or getattr(fields_map[f], "auto_now_add", False)
                )
                and f not in self.readonly_fields
            ]
        return [f for f in form_hidden_fields if f in model_fields]
