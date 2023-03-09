from fastadmin.models.base import InlineModelAdmin, ModelAdmin


class PonyORMMixin:
    # TODO: Add support for PonyORM
    pass


class PonyORMModelAdmin(PonyORMMixin, ModelAdmin):
    pass


class PonyORMInlineModelAdmin(PonyORMMixin, InlineModelAdmin):
    pass
