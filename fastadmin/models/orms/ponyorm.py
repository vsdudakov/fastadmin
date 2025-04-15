from enum import EnumMeta
from typing import Any
from uuid import UUID

from asgiref.sync import sync_to_async
from pony.orm import commit, db_session, desc, flush

from fastadmin.models.base import InlineModelAdmin, ModelAdmin
from fastadmin.models.schemas import ModelFieldWidgetSchema, WidgetType
from fastadmin.settings import settings


class PonyORMMixin:
    @staticmethod
    def get_model_pk_name(orm_model_cls: Any) -> str:
        """This method is used to get model pk name.

        :return: A str.
        """
        return orm_model_cls._pk_.name

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
        orm_model_fields = [v for f, v in self.model_cls.__dict__.items() if not f.startswith("_")]
        fields = []
        for orm_model_field in orm_model_fields:
            field_type = orm_model_field.py_type.__name__
            field_name = orm_model_field.name
            column_name = orm_model_field.name

            if orm_model_field.is_relation:
                if orm_model_field.is_collection:
                    field_type = "m2m"
                    column_name = field_name
                else:
                    field_type = "fk"

            is_m2m = field_type in "m2m"
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

            is_pk = getattr(orm_model_field, "is_pk", False)
            is_immutable = (
                is_pk or getattr(orm_model_field, "hidden", False)
            ) and field_name not in self.readonly_fields

            required = getattr(orm_model_field, "is_required", False)

            choices = None
            if isinstance(orm_model_field.py_type, EnumMeta):
                field_type = "enum"
                choices = {item.name: item.value for item in orm_model_field.py_type}

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
                case "str" | "unicode":
                    form_widget_type = WidgetType.Input
                    filter_widget_type = WidgetType.Input
                case "LongStr" | "LongUnicode":
                    form_widget_type = WidgetType.TextArea
                    filter_widget_type = WidgetType.TextArea
                case "bool":
                    form_widget_type = WidgetType.Switch
                    form_widget_props["required"] = False
                    filter_widget_type = WidgetType.RadioGroup
                    filter_widget_props["options"] = [
                        {"label": "Yes", "value": True},
                        {"label": "No", "value": False},
                    ]
                case "IntArray" | "StrArray" | "FloatArray":
                    form_widget_type = WidgetType.Select
                    form_widget_props["mode"] = "tags"
                    filter_widget_type = WidgetType.Select
                    filter_widget_props["mode"] = "tags"
                case "int" | "float" | "Decimal":
                    form_widget_type = WidgetType.InputNumber
                    filter_widget_type = WidgetType.InputNumber
                case "date":
                    form_widget_type = WidgetType.DatePicker
                    form_widget_props["format"] = settings.ADMIN_DATE_FORMAT
                    filter_widget_type = WidgetType.RangePicker
                    filter_widget_props["format"] = settings.ADMIN_DATE_FORMAT
                case "datetime":
                    form_widget_type = WidgetType.DateTimePicker
                    form_widget_props["format"] = settings.ADMIN_DATETIME_FORMAT
                    filter_widget_type = WidgetType.RangePicker
                    filter_widget_props["format"] = settings.ADMIN_DATETIME_FORMAT
                    filter_widget_props["showTime"] = True
                case "time":
                    form_widget_type = WidgetType.TimePicker
                    form_widget_props["format"] = settings.ADMIN_TIME_FORMAT
                    filter_widget_type = WidgetType.RangePicker
                    filter_widget_props["format"] = settings.ADMIN_TIME_FORMAT
                    filter_widget_props["showTime"] = True
                case "enum":
                    form_widget_props["options"] = [{"label": k, "value": v} for k, v in (choices or {}).items()]
                    filter_widget_props["options"] = [{"label": k, "value": v} for k, v in (choices or {}).items()]
                    if field_name in self.radio_fields:
                        form_widget_type = WidgetType.RadioGroup
                        filter_widget_type = WidgetType.CheckboxGroup
                    else:
                        form_widget_type = WidgetType.Select
                        filter_widget_type = WidgetType.Select
                        filter_widget_props["mode"] = "multiple"
                case "Json":
                    form_widget_type = WidgetType.JsonTextArea

            # relations
            if field_type in ("fk", "o2o", "m2m"):
                rel_model_cls = orm_model_field.py_type
                rel_model = rel_model_cls.__name__
                rel_model_id_field = self.get_model_pk_name(rel_model_cls)
                rel_model_label_fields = ("__str__", rel_model_id_field)

                match field_type:
                    case "o2o":
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
                    case "fk":
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
                    case "m2m":
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

    @sync_to_async
    @db_session
    def orm_get_list(
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

        qs = getattr(self.model_cls, "select")(lambda m: m)  # noqa: B009
        if filters:
            for field_with_condition, value in filters.items():
                field = field_with_condition[0]
                condition = field_with_condition[1]
                model_pk_name = self.get_model_pk_name(self.model_cls)
                if field.endswith(f"_{model_pk_name}"):
                    field = field.replace(f"_{model_pk_name}", f".{model_pk_name}")
                pony_condition = "=="
                match condition:
                    case "lte":
                        pony_condition = ">="
                    case "gte":
                        pony_condition = "<="
                    case "lt":
                        pony_condition = ">"
                    case "gt":
                        pony_condition = "<"
                    case "exact":
                        pony_condition = "=="
                    case "contains":
                        pony_condition = "in"
                    case "icontains":
                        # TODO: support icontains here
                        pony_condition = "in"
                filter_expr = f""""{value}" {pony_condition}  m.{field}"""
                qs = qs.filter(filter_expr)

        if search and self.search_fields:
            ids = []
            for search_field in self.search_fields:
                # TODO: support icontains here
                filter_expr = f""""{search}" in m.{search_field}"""
                qs_ids = qs.filter(filter_expr)
                objs = list(qs_ids)
                ids += [o.id for o in objs]
            qs = qs.filter(lambda m: m.id in set(ids))

        ordering = [sort_by] if sort_by else self.ordering
        if ordering:
            desc_fields = [o[1:] for o in ordering if o.startswith("-")]
            asc_fields = [o for o in ordering if not o.startswith("-")]
            if asc_fields:
                qs = qs.order_by(*(getattr(self.model_cls, o) for o in asc_fields))
            if desc_fields:
                qs = qs.order_by(*(desc(getattr(self.model_cls, o)) for o in desc_fields))

        total = qs.count()

        if self.list_select_related:
            qs = qs.prefetch(*[getattr(self.model_cls, field) for field in self.list_select_related])

        if offset is not None and limit is not None:
            qs = qs.limit(limit, offset=offset)

        objs = list(qs)
        return objs, total

    @sync_to_async
    @db_session
    def orm_get_obj(self, id: UUID | int) -> Any | None:
        """This method is used to get orm/db model object.

        :params id: an id of object.
        :return: An object.
        """
        return self.model_cls.select(**{self.get_model_pk_name(self.model_cls): id}).first()

    @sync_to_async
    @db_session
    def orm_save_obj(self, id: UUID | Any | None, payload: dict) -> Any:
        """This method is used to save orm/db model object.

        :params id: an id of object.
        :params payload: a dict of payload.
        :return: An object.
        """
        if id:
            obj = self.model_cls.select(**{self.get_model_pk_name(self.model_cls): id}).first()
            if not obj:
                return None
            obj.set(**payload)
        else:
            obj = self.model_cls(**payload)
        flush()
        commit()
        return obj

    @sync_to_async
    @db_session
    def orm_delete_obj(self, id: UUID | int) -> None:
        """This method is used to delete orm/db model object.

        :params id: an id of object.
        :return: None.
        """
        obj = self.model_cls.select(**{self.get_model_pk_name(self.model_cls): id}).first()
        if not obj:
            return
        obj.delete()
        flush()
        commit()

    @sync_to_async
    @db_session
    def orm_get_m2m_ids(self, obj: Any, field: str) -> list[int | UUID]:
        """This method is used to get m2m ids.

        :params obj: an object.
        :params field: a m2m field name.

        :return: A list of ids.
        """
        key_id = self.get_model_pk_name(self.model_cls)
        obj = self.model_cls.select(**{key_id: getattr(obj, key_id)}).first()
        if not obj:
            return []
        rel_model_cls = getattr(self.model_cls, field).py_type
        rel_key_id = self.get_model_pk_name(rel_model_cls)
        return [getattr(o, rel_key_id) for o in getattr(obj, field)]

    @sync_to_async
    @db_session
    def orm_save_m2m_ids(self, obj: Any, field: str, ids: list[int | UUID]) -> None:
        """This method is used to get m2m ids.

        :params obj: an object.
        :params field: a m2m field name.
        :params ids: a list of ids.

        :return: A list of ids.
        """
        key_id = self.get_model_pk_name(self.model_cls)
        obj = self.model_cls.select(**{key_id: getattr(obj, key_id)}).first()
        if not obj:
            return
        getattr(obj, field).clear()
        if ids:
            rel_model_cls = getattr(self.model_cls, field).py_type
            rel_key_id = self.get_model_pk_name(rel_model_cls)
            rel_objs = list(rel_model_cls.select(lambda o: getattr(o, rel_key_id) in ids))
            getattr(obj, field).add(rel_objs)
        flush()
        commit()

    @sync_to_async
    @db_session
    def orm_save_upload_field(self, obj: Any, field: str, base64: str) -> None:
        """This method is used to save upload field.

        :params obj: an object.
        :params field: a m2m field name.
        :params base64: a base64 string.

        :return: A list of ids.
        """

    @sync_to_async
    @db_session
    def serialize_obj_attributes(
        self, obj: Any, attributes_to_serizalize: list[ModelFieldWidgetSchema]
    ) -> dict[str, Any]:
        """Serialize orm model obj attribute to dict.

        :params obj: an object.
        :params attributes_to_serizalize: a list of attributes to serialize.
        :return: A dict of serialized attributes.
        """
        data = {}
        key_id = self.get_model_pk_name(self.model_cls)
        obj = self.model_cls.select(**{key_id: getattr(obj, key_id)}).first()
        if not obj:
            return data

        return obj.to_dict(only=(f.column_name for f in attributes_to_serizalize))


class PonyORMModelAdmin(PonyORMMixin, ModelAdmin):
    pass


class PonyORMInlineModelAdmin(PonyORMMixin, InlineModelAdmin):
    pass
