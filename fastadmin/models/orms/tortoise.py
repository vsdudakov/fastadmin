import functools
import operator
from typing import Any
from uuid import UUID

from tortoise.expressions import Q

from fastadmin.models.base import InlineModelAdmin, ModelAdmin
from fastadmin.models.schemas import ModelFieldWidgetSchema, WidgetType
from fastadmin.settings import settings


class TortoiseMixin:
    @staticmethod
    def get_model_pk_name(orm_model_cls: Any) -> str:
        """This method is used to get model pk name.

        :return: A str.
        """
        return orm_model_cls._meta.pk_attr

    def get_model_fields_with_widget_types(
        self,
        with_m2m: bool | None = None,
        with_upload: bool | None = None,
    ) -> list[ModelFieldWidgetSchema]:
        """This method is used to get model fields with widget types.

        :params with_m2m: a flag to include m2m fields.
        :params with_upload: a flag to include upload fields.
        :return: A list of ModelFieldWidgetSchema.
        """
        orm_model_fields = self.model_cls._meta.fields_map.items()
        fields = []
        for orm_model_field_name, orm_model_field in orm_model_fields:
            field_type = orm_model_field.__class__.__name__
            field_name = orm_model_field_name
            column_name = orm_model_field_name

            if getattr(orm_model_field, "_generated", False):
                continue

            if field_type in ("BackwardFKRelation", "BackwardOneToOneRelation"):
                continue

            if field_name.endswith("_id") and getattr(orm_model_field, "reference", False):
                # ignore _id fields for relations
                continue

            if field_type in ("OneToOneFieldInstance", "ForeignKeyFieldInstance") and not column_name.endswith("_id"):
                column_name = f"{column_name}_id"

            is_m2m = field_type == "ManyToManyFieldInstance"
            w_type, _ = self.formfield_overrides.get(field_name, (None, None))
            is_upload = w_type == WidgetType.Upload
            if with_m2m is not None and not with_m2m and is_m2m:
                continue
            if with_m2m is not None and with_m2m and not is_m2m:
                continue
            if with_upload is not None and not with_upload and is_upload:
                continue
            if with_upload is not None and with_upload and not is_upload:
                continue

            is_pk = getattr(orm_model_field, "pk", False)
            is_immutable = (
                is_pk or getattr(orm_model_field, "auto_now", False) or getattr(orm_model_field, "auto_now_add", False)
            ) and field_name not in self.readonly_fields
            required = (
                not getattr(orm_model_field, "null", False)
                and not getattr(orm_model_field, "default", False)
                and not is_m2m
            )
            choices = (
                orm_model_field.enum_type._member_map_
                if hasattr(orm_model_field, "enum_type") and hasattr(orm_model_field.enum_type, "_member_map_")
                else {}
            )

            form_widget_type = WidgetType.Input
            form_widget_props = {
                "required": required,
                "disabled": field_name in self.readonly_fields,
                "readOnly": field_name in self.readonly_fields,
            }
            filter_widget_type = WidgetType.Input
            filter_widget_props = {
                "required": False,
            }

            # columns
            match field_type:
                case "CharField":
                    form_widget_type = WidgetType.Input
                    filter_widget_type = WidgetType.Input
                case "TextField":
                    form_widget_type = WidgetType.TextArea
                    filter_widget_type = WidgetType.TextArea
                case "BooleanField":
                    form_widget_type = WidgetType.Switch
                    form_widget_props["required"] = False
                    filter_widget_type = WidgetType.RadioGroup
                    filter_widget_props["options"] = [
                        {"label": "Yes", "value": True},
                        {"label": "No", "value": False},
                    ]
                case "ArrayField":
                    form_widget_type = WidgetType.Select
                    form_widget_props["mode"] = "tags"
                    filter_widget_type = WidgetType.Select
                    filter_widget_props["mode"] = "tags"
                case "IntField" | "SmallIntField" | "BigIntField" | "FloatField" | "DecimalField":
                    form_widget_type = WidgetType.InputNumber
                    filter_widget_type = WidgetType.InputNumber
                case "DateField":
                    form_widget_type = WidgetType.DatePicker
                    form_widget_props["format"] = settings.ADMIN_DATE_FORMAT
                    filter_widget_type = WidgetType.RangePicker
                    filter_widget_props["format"] = settings.ADMIN_DATE_FORMAT
                case "DatetimeField":
                    form_widget_type = WidgetType.DateTimePicker
                    form_widget_props["format"] = settings.ADMIN_DATETIME_FORMAT
                    filter_widget_type = WidgetType.RangePicker
                    filter_widget_props["format"] = settings.ADMIN_DATETIME_FORMAT
                    filter_widget_props["showTime"] = True
                case "TimeField":
                    form_widget_type = WidgetType.TimePicker
                    form_widget_props["format"] = settings.ADMIN_TIME_FORMAT
                    filter_widget_type = WidgetType.RangePicker
                    filter_widget_props["format"] = settings.ADMIN_TIME_FORMAT
                    filter_widget_props["showTime"] = True
                case "CharEnumFieldInstance" | "IntEnumFieldInstance":
                    form_widget_props["options"] = [{"label": k, "value": v} for k, v in choices.items()]
                    filter_widget_props["options"] = [{"label": k, "value": v} for k, v in choices.items()]
                    if field_name in self.radio_fields:
                        form_widget_type = WidgetType.RadioGroup
                        filter_widget_type = WidgetType.CheckboxGroup
                    else:
                        form_widget_type = WidgetType.Select
                        filter_widget_type = WidgetType.Select
                        filter_widget_props["mode"] = "multiple"
                case "JSONField":
                    form_widget_type = WidgetType.JsonTextArea

            # relations
            if field_type in ("ForeignKeyFieldInstance", "OneToOneFieldInstance", "ManyToManyFieldInstance"):
                rel_model_cls = orm_model_field.related_model
                rel_model = rel_model_cls.__name__
                rel_model_id_field = self.get_model_pk_name(rel_model_cls)
                rel_model_label_fields = ("__str__", rel_model_id_field)

                match field_type:
                    case "OneToOneFieldInstance":
                        if field_name in self.raw_id_fields:
                            form_widget_type = WidgetType.Input
                            filter_widget_type = WidgetType.Input
                        else:
                            form_widget_type = WidgetType.AsyncSelect
                            form_widget_props["parentModel"] = rel_model
                            form_widget_props["idField"] = rel_model_id_field
                            form_widget_props["labelFields"] = rel_model_label_fields
                            filter_widget_type = WidgetType.AsyncSelect
                            filter_widget_props["mode"] = "multiple"
                            filter_widget_props["parentModel"] = rel_model
                            filter_widget_props["idField"] = rel_model_id_field
                            filter_widget_props["labelFields"] = rel_model_label_fields
                    case "ForeignKeyFieldInstance":
                        if field_name in self.raw_id_fields:
                            form_widget_type = WidgetType.Input
                            filter_widget_type = WidgetType.Input
                        else:
                            form_widget_type = WidgetType.AsyncSelect
                            form_widget_props["parentModel"] = rel_model
                            form_widget_props["idField"] = rel_model_id_field
                            form_widget_props["labelFields"] = rel_model_label_fields
                            filter_widget_type = WidgetType.AsyncSelect
                            filter_widget_props["mode"] = "multiple"
                            filter_widget_props["parentModel"] = rel_model
                            filter_widget_props["idField"] = rel_model_id_field
                            filter_widget_props["labelFields"] = rel_model_label_fields
                    case "ManyToManyFieldInstance":
                        if field_name in self.raw_id_fields:
                            form_widget_type = WidgetType.Input
                            filter_widget_type = WidgetType.Input
                        else:
                            form_widget_props["parentModel"] = rel_model
                            form_widget_props["idField"] = rel_model_id_field
                            form_widget_props["labelFields"] = rel_model_label_fields
                            filter_widget_props["parentModel"] = rel_model
                            filter_widget_props["idField"] = rel_model_id_field
                            filter_widget_props["labelFields"] = rel_model_label_fields
                            if field_name in self.filter_vertical or field_name in self.filter_horizontal:
                                form_widget_type = WidgetType.AsyncTransfer
                                form_widget_props["layout"] = (
                                    "vertical" if field_name in self.filter_vertical else "horizontal"
                                )
                                filter_widget_type = WidgetType.AsyncTransfer
                                filter_widget_props["layout"] = (
                                    "vertical" if field_name in self.filter_vertical else "horizontal"
                                )
                            else:
                                form_widget_type = WidgetType.AsyncSelect
                                form_widget_props["mode"] = "multiple"
                                filter_widget_type = WidgetType.AsyncSelect
                                filter_widget_props["mode"] = "multiple"

            form_widget_type, form_widget_props = self.formfield_overrides.get(
                field_name, (form_widget_type, form_widget_props)
            )
            fields.append(
                ModelFieldWidgetSchema(
                    name=field_name,
                    column_name=column_name,
                    is_m2m=is_m2m,
                    is_pk=is_pk,
                    is_immutable=is_immutable,
                    form_widget_type=form_widget_type,
                    form_widget_props=form_widget_props,
                    filter_widget_type=filter_widget_type,
                    filter_widget_props=filter_widget_props,
                )
            )
        return fields

    async def orm_get_list(
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

        if filters:
            for field_with_condition, value in filters.items():
                field = field_with_condition[0]
                condition = field_with_condition[1]
                qs = qs.filter(**{f"{field}__{condition}" if condition != "exact" else field: value})

        if search and self.search_fields:
            qs = qs.filter(
                functools.reduce(
                    operator.or_,
                    (Q(**{f + "__icontains": search}) for f in self.search_fields),
                    Q(),
                )
            )

        if sort_by:
            qs = qs.order_by(sort_by)
        elif self.ordering:
            qs = qs.order_by(*self.ordering)

        total = await qs.count()

        if self.list_select_related:
            qs = qs.select_related(*self.list_select_related)

        if offset is not None and limit is not None:
            qs = qs.offset(offset)
            qs = qs.limit(limit)

        return await qs, total

    async def orm_get_obj(self, id: UUID | int) -> Any | None:
        """This method is used to get orm/db model object.

        :params id: an id of object.
        :return: An object.
        """
        qs = self.model_cls.filter(**{self.get_model_pk_name(self.model_cls): id})
        return await qs.first()

    async def orm_save_obj(self, id: UUID | Any | None, payload: dict) -> Any:
        """This method is used to save orm/db model object.

        :params id: an id of object.
        :params payload: a dict of payload.
        :return: An object.
        """
        if id:
            obj = await self.model_cls.filter(**{self.get_model_pk_name(self.model_cls): id}).first()
            if not obj:
                return None
            for k, v in payload.items():
                setattr(obj, k, v)
        else:
            obj = self.model_cls(**payload)
        await obj.save(update_fields=payload.keys() if id else None)
        return obj

    async def orm_delete_obj(self, id: UUID | int) -> None:
        """This method is used to delete orm/db model object.

        :params id: an id of object.
        :return: None.
        """
        qs = self.model_cls.filter(**{self.get_model_pk_name(self.model_cls): id})
        await qs.delete()

    async def orm_get_m2m_ids(self, obj: Any, field: str) -> list[int | UUID]:
        """This method is used to get m2m ids.

        :params obj: an object.
        :params field: a m2m field name.

        :return: A list of ids.
        """
        m2m_rel = getattr(obj, field)
        remote_model = m2m_rel.remote_model
        return await m2m_rel.all().values_list(self.get_model_pk_name(remote_model), flat=True)

    async def orm_save_m2m_ids(self, obj: Any, field: str, ids: list[int | UUID]) -> None:
        """This method is used to get m2m ids.

        :params obj: an object.
        :params field: a m2m field name.
        :params ids: a list of ids.

        :return: A list of ids.
        """
        m2m_rel = getattr(obj, field)

        await m2m_rel.clear()
        remote_model = m2m_rel.remote_model
        remote_model_objs = []
        for rel_id in ids:
            remote_model_obj = remote_model()
            setattr(remote_model_obj, self.get_model_pk_name(remote_model), rel_id)
            remote_model_obj._saved_in_db = True
            remote_model_objs.append(remote_model_obj)
        if remote_model_objs:
            await m2m_rel.add(*remote_model_objs)

    async def orm_save_upload_field(self, obj: Any, field: str, base64: str) -> None:
        """This method is used to save upload field.

        :params obj: an object.
        :params field: a m2m field name.
        :params base64: a base64 string.

        :return: A list of ids.
        """


class TortoiseModelAdmin(TortoiseMixin, ModelAdmin):
    pass


class TortoiseInlineModelAdmin(TortoiseMixin, InlineModelAdmin):
    pass
