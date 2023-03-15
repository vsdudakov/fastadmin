from typing import Any
from uuid import UUID

from pony.orm import db_session

from fastadmin.models.base import InlineModelAdmin, ModelAdmin
from fastadmin.models.decorators import sync_to_async
from fastadmin.models.helpers import get_admin_model
from fastadmin.models.schemas import ModelFieldWidgetSchema, WidgetType
from fastadmin.settings import settings


class PonyORMMixin:

    @staticmethod
    def get_model_pk_name(orm_model_cls: Any) -> str:
        """This method is used to get model pk name.

        :return: A str.
        """
        return "id"

    def get_model_fields_with_widget_types(
        self,
        with_m2m: bool | None = None,
    ) -> list[ModelFieldWidgetSchema]:
        """This method is used to get model fields with widget types.

        :params with_m2m: a flag to include m2m fields.
        :params with_pk: a flag to include pk fields.
        :params with_readonly: a flag to include readonly fields.
        :return: A list of ModelFieldWidgetSchema.
        """
        return []

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
        return [], 0

    @sync_to_async
    @db_session
    def orm_get_obj(self, id: UUID | int) -> Any | None:
        """This method is used to get orm/db model object.

        :params id: an id of object.
        :return: An object.
        """
        return None

    @sync_to_async
    @db_session
    def orm_save_obj(self, obj: Any, update_fields: list[str] | None = None) -> Any:
        """This method is used to save orm/db model object.

        :params obj: an object.
        :params update_fields: a list of fields to update.
        :return: An object.
        """
        return obj

    @sync_to_async
    @db_session
    def orm_delete_obj(self, id: UUID | int) -> None:
        """This method is used to delete orm/db model object.

        :params id: an id of object.
        :return: None.
        """
        return None

    @sync_to_async
    @db_session
    def orm_get_m2m_ids(self, obj: Any, field: str) -> list[int | UUID]:
        """This method is used to get m2m ids.

        :params obj: an object.
        :params field: a m2m field name.

        :return: A list of ids.
        """
        return []

    @sync_to_async
    @db_session
    def orm_save_m2m_ids(self, obj: Any, field: str, ids: list[int | UUID]) -> None:
        """This method is used to get m2m ids.

        :params obj: an object.
        :params field: a m2m field name.

        :return: A list of ids.
        """
        return None



class PonyORMModelAdmin(PonyORMMixin, ModelAdmin):
    pass


class PonyORMInlineModelAdmin(PonyORMMixin, InlineModelAdmin):
    pass
