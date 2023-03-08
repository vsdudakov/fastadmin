from fastadmin.models.base import InlineModelAdmin, ModelAdmin, ORMInterfaceMixin


class PonyORMMixin(ORMInterfaceMixin):
    # TODO: Add support for PonyORM
    pass


class PonyORMModelAdmin(PonyORMMixin, ModelAdmin):
    pass


class PonyORMInlineModelAdmin(PonyORMMixin, InlineModelAdmin):
    pass
