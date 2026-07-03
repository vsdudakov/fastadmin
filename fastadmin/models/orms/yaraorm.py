import functools
import operator
from typing import Any
from uuid import UUID

from yara_orm import Q

from fastadmin.models.base import InlineModelAdmin, ModelAdmin
from fastadmin.models.schemas import ModelFieldWidgetSchema, WidgetType
from fastadmin.settings import settings


class YaraOrmMixin:
    def _get_relation_target(self, field_name: str) -> Any:
        """Resolve the related model class for a forward relation field."""
        relation = self.model_cls._meta.relations.get(field_name)
        return relation.resolve_target() if relation else None

    def _resolve_ordering_field(self, ordering_field: str) -> str:
        """Resolve ordering field for Yara ORM.

        Relation names (e.g. `tournament`) are not orderable directly; for
        FK/O2O relations order by their backing id column (e.g. `tournament_id`).
        """
        if not ordering_field:
            return ordering_field

        prefix = "-" if ordering_field.startswith("-") else ""
        field_name = ordering_field.lstrip("-")

        # Respect explicit nested ordering (e.g. relation__name)
        if "__" in field_name:
            return ordering_field

        if field_name in self.model_cls._meta.relations:
            return f"{prefix}{field_name}_id"
        return ordering_field

    @staticmethod
    def get_model_pk_name(orm_model_cls: Any) -> str:
        """This method is used to get model pk name.

        :return: A str.
        """
        return orm_model_cls._meta.pk_field.model_field_name

    def _build_relation_widgets(
        self,
        field_type: str,
        field_name: str,
        rel_model_cls: Any,
        form_widget_props: dict,
        filter_widget_props: dict,
    ) -> tuple[WidgetType, WidgetType]:
        """Configure form/filter widgets for a relation field."""
        rel_model = rel_model_cls.__name__
        rel_model_id_field = self.get_model_pk_name(rel_model_cls)
        rel_model_label_fields = ("__str__", rel_model_id_field)

        if field_name in self.raw_id_fields:
            return WidgetType.Input, WidgetType.Input

        for props in (form_widget_props, filter_widget_props):
            props["parentModel"] = rel_model
            props["idField"] = rel_model_id_field
            props["labelFields"] = rel_model_label_fields

        if field_type == "ManyToManyFieldInstance":
            if field_name in self.filter_vertical or field_name in self.filter_horizontal:
                layout = "vertical" if field_name in self.filter_vertical else "horizontal"
                form_widget_props["layout"] = layout
                filter_widget_props["layout"] = layout
                return WidgetType.AsyncTransfer, WidgetType.AsyncTransfer
            form_widget_props["mode"] = "multiple"
            filter_widget_props["mode"] = "multiple"
            return WidgetType.AsyncSelect, WidgetType.AsyncSelect

        # FK / O2O
        filter_widget_props["mode"] = "multiple"
        return WidgetType.AsyncSelect, WidgetType.AsyncSelect

    def get_model_fields_with_widget_types(
        self,
        with_m2m: bool | None = None,
    ) -> list[ModelFieldWidgetSchema]:
        """This method is used to get model fields with widget types.

        :params with_m2m: a flag to include m2m fields.
        :return: A list of ModelFieldWidgetSchema.
        """
        meta = self.model_cls._meta
        # Yara ORM keeps forward fields in fields_map (with FKs appearing under
        # both the relation name and the `<name>_id` column) and m2m fields in a
        # separate `m2m` mapping.
        entries: list[tuple[str, Any, bool]] = [(name, field, False) for name, field in meta.fields_map.items()]
        entries += [(name, m2m_info.field, True) for name, m2m_info in meta.m2m.items()]

        fields = []
        for field_name, orm_model_field, is_m2m in entries:
            field_type = orm_model_field.__class__.__name__

            # Skip the raw `<name>_id` duplicate of a forward relation.
            if not is_m2m and field_name.endswith("_id") and getattr(orm_model_field, "reference", None):
                continue

            if with_m2m is not None and not with_m2m and is_m2m:
                continue
            if with_m2m is not None and with_m2m and not is_m2m:
                continue

            column_name = field_name
            if not is_m2m and getattr(orm_model_field, "reference", None):
                column_name = orm_model_field.model_field_name

            is_pk = getattr(orm_model_field, "pk", False)
            is_immutable = (
                is_pk or getattr(orm_model_field, "auto_now", False) or getattr(orm_model_field, "auto_now_add", False)
            ) and field_name not in self.readonly_fields
            required = (
                not getattr(orm_model_field, "null", False)
                and not getattr(orm_model_field, "default", None)
                and not is_pk
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
            filter_widget_props: dict = {"required": False}

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
                case "IntField" | "SmallIntField" | "BigIntField" | "FloatField" | "DecimalField":
                    form_widget_type = WidgetType.InputNumber
                    filter_widget_type = WidgetType.InputNumber
                case "UUIDField":
                    form_widget_type = WidgetType.Input
                    filter_widget_type = WidgetType.Input
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
                case "CharEnumField" | "IntEnumField":
                    form_widget_props["options"] = [{"label": k, "value": v.value} for k, v in choices.items()]
                    filter_widget_props["options"] = [{"label": k, "value": v.value} for k, v in choices.items()]
                    if field_name in self.radio_fields:
                        form_widget_type = WidgetType.RadioGroup
                        filter_widget_type = WidgetType.CheckboxGroup
                    else:
                        form_widget_type = WidgetType.Select
                        filter_widget_type = WidgetType.Select
                        filter_widget_props["mode"] = "multiple"
                case "JSONField":
                    form_widget_type = WidgetType.JsonTextArea

            if is_m2m or field_type in ("ForeignKeyFieldInstance", "OneToOneFieldInstance"):
                rel_model_cls = (
                    self.model_cls._meta.m2m[field_name].resolve_target()
                    if is_m2m
                    else (self._get_relation_target(field_name))
                )
                if rel_model_cls is not None:
                    form_widget_type, filter_widget_type = self._build_relation_widgets(
                        "ManyToManyFieldInstance" if is_m2m else field_type,
                        field_name,
                        rel_model_cls,
                        form_widget_props,
                        filter_widget_props,
                    )

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

        search_fields = list(self.search_fields)
        if search and search_fields:
            qs = qs.filter(
                functools.reduce(
                    operator.or_,
                    (Q(**{f + "__icontains": search}) for f in search_fields),  # ty: ignore[invalid-argument-type]
                    Q(),
                )
            )

        if sort_by:
            qs = qs.order_by(self._resolve_ordering_field(sort_by))
        elif self.ordering:
            qs = qs.order_by(*(self._resolve_ordering_field(field) for field in self.ordering))

        total = await qs.count()

        if self.list_select_related:
            qs = qs.select_related(*self.list_select_related)

        if offset is not None and limit is not None:
            qs = qs.offset(offset)
            qs = qs.limit(limit)

        return await qs, total

    async def orm_get_obj(self, id: UUID | int | str) -> Any | None:
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
        await obj.save(update_fields=list(payload.keys()) if id else None)
        return obj

    async def orm_delete_obj(self, id: UUID | int | str) -> None:
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
        target_model = m2m_rel.target
        return await m2m_rel.all().values_list(self.get_model_pk_name(target_model), flat=True)

    async def orm_save_m2m_ids(self, obj: Any, field: str, ids: list[int | str | UUID]) -> None:
        """This method is used to save m2m ids.

        :params obj: an object.
        :params field: a m2m field name.
        :params ids: a list of ids.
        :return: None.
        """
        m2m_rel = getattr(obj, field)
        await m2m_rel.clear()
        target_model = m2m_rel.target
        target_objs = []
        for rel_id in ids:
            target_obj = target_model()
            setattr(target_obj, self.get_model_pk_name(target_model), rel_id)
            target_obj._saved_in_db = True
            target_objs.append(target_obj)
        if target_objs:
            await m2m_rel.add(*target_objs)


class YaraOrmModelAdmin(YaraOrmMixin, ModelAdmin):
    pass


class YaraOrmInlineModelAdmin(YaraOrmMixin, InlineModelAdmin):
    pass
