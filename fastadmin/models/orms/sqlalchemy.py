from fastadmin.models.base import InlineModelAdmin, ModelAdmin, ORMInterfaceMixin


class SqlAlchemyMixin(ORMInterfaceMixin):
    # TODO: Add support for SqlAlchemy
    pass


class SqlAlchemyModelAdmin(SqlAlchemyMixin, ModelAdmin):
    pass


class SqlAlchemyInlineModelAdmin(SqlAlchemyMixin, InlineModelAdmin):
    pass
