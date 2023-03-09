from fastadmin.models.base import InlineModelAdmin, ModelAdmin


class SqlAlchemyMixin:
    # TODO: Add support for SqlAlchemy
    pass


class SqlAlchemyModelAdmin(SqlAlchemyMixin, ModelAdmin):
    pass


class SqlAlchemyInlineModelAdmin(SqlAlchemyMixin, InlineModelAdmin):
    pass
