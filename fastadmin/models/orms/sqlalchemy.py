import contextlib
from typing import Any
from uuid import UUID

from sqlalchemy import BIGINT, Integer, and_, func, inspect, or_, select, text
from sqlalchemy.orm import selectinload

from fastadmin.models.base import InlineModelAdmin, ModelAdmin
from fastadmin.models.helpers import getattrs
from fastadmin.models.schemas import ModelFieldWidgetSchema, WidgetType
from fastadmin.settings import settings


class SqlAlchemyMixin:
    @staticmethod
    def get_model_pk_name(orm_model_cls: Any) -> str:
        """This method is used to get model pk name.

        :return: A str.
        """
        return getattrs(orm_model_cls, "__table__.primary_key._autoincrement_column.name", default="id")

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
        mapper = inspect(self.model_cls)
        orm_model_fields = [f for f in mapper.c if not f.foreign_keys] + list(mapper.relationships)

        fields = []
        for orm_model_field in orm_model_fields:
            field_type = getattrs(orm_model_field, "direction.name") or getattrs(
                orm_model_field, "type.__class__.__name__"
            )
            field_name = orm_model_field.key
            column_name = orm_model_field.key

            if field_type in ("ONETOMANY",):
                continue

            if field_type in (
                "ONETOONE",
                "MANYTOONE",
            ) and not column_name.endswith("_id"):
                column_name = f"{column_name}_id"

                if column_name not in [f.key for f in mapper.c if f.foreign_keys]:
                    continue

            is_m2m = field_type == "MANYTOMANY"
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

            is_pk = self.get_model_pk_name(self.model_cls) == field_name
            is_immutable = (
                is_pk or bool(getattr(orm_model_field, "onupdate", None))
            ) and field_name not in self.readonly_fields
            required = (
                not getattr(orm_model_field, "nullable", False)
                and not getattr(orm_model_field, "default", False)
                and not is_m2m
            )
            choices = (
                orm_model_field.type._object_lookup
                if hasattr(orm_model_field, "type") and hasattr(orm_model_field.type, "_object_lookup")
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
                case "String":
                    form_widget_type = WidgetType.Input
                    filter_widget_type = WidgetType.Input
                case "Text":
                    form_widget_type = WidgetType.TextArea
                    filter_widget_type = WidgetType.TextArea
                case "Boolean":
                    form_widget_type = WidgetType.Switch
                    form_widget_props["required"] = False
                    filter_widget_type = WidgetType.RadioGroup
                    filter_widget_props["options"] = [
                        {"label": "Yes", "value": True},
                        {"label": "No", "value": False},
                    ]
                case "ARRAY":
                    form_widget_type = WidgetType.Select
                    form_widget_props["mode"] = "tags"
                    filter_widget_type = WidgetType.Select
                    filter_widget_props["mode"] = "tags"
                case "Integer" | "Float" | "Decimal":
                    form_widget_type = WidgetType.InputNumber
                    filter_widget_type = WidgetType.InputNumber
                case "Date":
                    form_widget_type = WidgetType.DatePicker
                    form_widget_props["format"] = settings.ADMIN_DATE_FORMAT
                    filter_widget_type = WidgetType.RangePicker
                    filter_widget_props["format"] = settings.ADMIN_DATE_FORMAT
                case "DateTime":
                    form_widget_type = WidgetType.DateTimePicker
                    form_widget_props["format"] = settings.ADMIN_DATETIME_FORMAT
                    filter_widget_type = WidgetType.RangePicker
                    filter_widget_props["format"] = settings.ADMIN_DATETIME_FORMAT
                    filter_widget_props["showTime"] = True
                case "Time":
                    form_widget_type = WidgetType.TimePicker
                    form_widget_props["format"] = settings.ADMIN_TIME_FORMAT
                    filter_widget_type = WidgetType.RangePicker
                    filter_widget_props["format"] = settings.ADMIN_TIME_FORMAT
                    filter_widget_props["showTime"] = True
                case "Enum":
                    form_widget_props["options"] = [{"label": k, "value": v} for k, v in choices.items()]
                    filter_widget_props["options"] = [{"label": k, "value": v} for k, v in choices.items()]
                    if field_name in self.radio_fields:
                        form_widget_type = WidgetType.RadioGroup
                        filter_widget_type = WidgetType.CheckboxGroup
                    else:
                        form_widget_type = WidgetType.Select
                        filter_widget_type = WidgetType.Select
                        filter_widget_props["mode"] = "multiple"
                case "JSON":
                    form_widget_type = WidgetType.JsonTextArea

            # relations
            if field_type in (
                "ONETOONE",
                "MANYTOONE",
                "MANYTOMANY",
            ):
                rel_model_cls = getattrs(orm_model_field, "entity.class_")
                rel_model = rel_model_cls.__name__
                rel_model_id_field = self.get_model_pk_name(rel_model_cls)
                rel_model_label_fields = ("__str__", rel_model_id_field)

                match field_type:
                    case "ONETOONE":
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
                    case "MANYTOONE":
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
                    case "MANYTOMANY":
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

        def convert_sort_by(sort_by: str) -> str:
            if sort_by.startswith("-"):
                return sort_by[1:] + " desc"
            return sort_by

        sessionmaker = self.get_sessionmaker()
        async with sessionmaker() as session:
            qs = select(self.model_cls)

            if filters:
                q = []
                for field_with_condition, value in filters.items():
                    field = field_with_condition[0]
                    condition = field_with_condition[1]
                    model_field = getattr(self.model_cls, field)

                    if isinstance(model_field.expression.type, BIGINT | Integer):
                        with contextlib.suppress(ValueError, TypeError):
                            value = int(value)

                    match condition:
                        case "lte":
                            q.append(model_field >= value)
                        case "gte":
                            q.append(model_field <= value)
                        case "lt":
                            q.append(model_field > value)
                        case "gt":
                            q.append(model_field < value)
                        case "exact":
                            q.append(model_field == value)
                        case "contains":
                            q.append(model_field.like(f"%{value}%"))
                        case "icontains":
                            q.append(model_field.ilike(f"%{value}%"))
                qs = qs.filter(and_(*q))

            if search and self.search_fields:
                q = []
                for field in self.search_fields:
                    q.append(getattr(self.model_cls, field).ilike(f"%{search}%"))
                qs = qs.filter(or_(*q))

            if sort_by:
                qs = qs.order_by(text(convert_sort_by(sort_by)))
            elif self.ordering:
                sort_by_text = ", ".join([convert_sort_by(f) for f in self.ordering])
                qs = qs.order_by(text(sort_by_text))

            objs = await session.execute(select(func.count()).select_from(qs))  # type: ignore [arg-type]
            total = objs.scalar()

            if self.list_select_related:
                for field in self.list_select_related:
                    qs = qs.options(selectinload(getattr(self.model_cls, field)))

            if offset is not None and limit is not None:
                qs = qs.offset(offset)
                qs = qs.limit(limit)

            return await session.scalars(qs), total

    async def orm_get_obj(self, id: UUID | int) -> Any | None:
        """This method is used to get orm/db model object.

        :params id: an id of object.
        :return: An object.
        """
        sessionmaker = self.get_sessionmaker()
        async with sessionmaker() as session:
            return await session.get(self.model_cls, id)

    def _get_foreign_key_fields(self) -> list[str]:
        """Returns a list of foreign key fields for the model.

        :return: List of foreign key field names.
        """
        return [column.name for column in self.model_cls.__table__.columns if column.foreign_keys]

    async def orm_save_obj(self, id: UUID | Any | None, payload: dict) -> Any:
        """This method is used to save orm/db model object.

        :params id: an id of object.
        :params payload: a dict of payload.
        :return: An object.
        """
        for fk_field_name in self._get_foreign_key_fields():
            if fk_field_name in payload and isinstance(payload[fk_field_name], str):
                with contextlib.suppress(ValueError, TypeError):
                    # convert string to int for foreign key fields for postgresql alchemy
                    payload[fk_field_name] = int(payload[fk_field_name])

        sessionmaker = self.get_sessionmaker()
        async with sessionmaker() as session:
            if id:
                obj = await session.get(self.model_cls, id)
                if not obj:
                    return None
                for k, v in payload.items():
                    setattr(obj, k, v)
                await session.merge(obj)
                await session.commit()
            else:
                obj = self.model_cls(**payload)
                session.add(obj)
                await session.commit()
            return await session.get(self.model_cls, getattr(obj, self.get_model_pk_name(self.model_cls)))

    async def orm_delete_obj(self, id: UUID | int) -> None:
        """This method is used to delete orm/db model object.

        :params id: an id of object.
        :return: None.
        """
        sessionmaker = self.get_sessionmaker()
        async with sessionmaker() as session:
            obj = await session.get(self.model_cls, id)
            await session.delete(obj)
            await session.commit()

    async def orm_get_m2m_ids(self, obj: Any, field: str) -> list[int | UUID]:
        """This method is used to get m2m ids.

        :params obj: an object.
        :params field: a m2m field name.

        :return: A list of ids.
        """
        sessionmaker = self.get_sessionmaker()
        async with sessionmaker() as session:
            id_key = self.get_model_pk_name(self.model_cls)
            qs = select(self.model_cls)
            qs = qs.filter_by(**{id_key: getattr(obj, id_key)})
            qs = qs.options(selectinload(getattr(self.model_cls, field)))
            obj = await session.scalar(qs)
            return [getattr(obj, id_key) for obj in getattr(obj, field, [])]

    async def orm_save_m2m_ids(self, obj: Any, field: str, ids: list[int | UUID]) -> None:
        """This method is used to get m2m ids.

        :params obj: an object.
        :params field: a m2m field name.
        :params ids: a list of ids.

        :return: A list of ids.
        """
        mapper = inspect(self.model_cls)
        orm_model_field = next((f for f in mapper.relationships if f.key == field), None)
        if not orm_model_field:
            raise ValueError(f"Field {field} is not a relationship field.")

        sessionmaker = self.get_sessionmaker()
        async with sessionmaker() as session:
            values = []
            id_key = self.get_model_pk_name(self.model_cls)
            obj_id = getattr(obj, id_key)
            if not obj_id:
                return
            obj_field_name = orm_model_field.synchronize_pairs[0][1].key
            rel_field_name = orm_model_field.secondary_synchronize_pairs[0][1].key

            qs = orm_model_field.secondary.delete().where(
                getattrs(orm_model_field.secondary, f"c.{obj_field_name}") == obj_id
            )
            await session.execute(qs)
            for rel_id in ids:
                with contextlib.suppress(ValueError, TypeError):
                    rel_id = int(rel_id)
                with contextlib.suppress(ValueError, TypeError):
                    obj_id = int(obj_id)
                values.append(
                    {
                        rel_field_name: rel_id,
                        obj_field_name: obj_id,
                    }
                )
            if values:
                await session.execute(orm_model_field.secondary.insert().values(values))
            await session.commit()

    async def orm_save_upload_field(self, obj: Any, field: str, base64: str) -> None:
        """This method is used to save upload field.

        :params obj: an object.
        :params field: a m2m field name.
        :params base64: a base64 string.

        :return: A list of ids.
        """


class SqlAlchemyModelAdmin(SqlAlchemyMixin, ModelAdmin):
    pass


class SqlAlchemyInlineModelAdmin(SqlAlchemyMixin, InlineModelAdmin):
    pass
