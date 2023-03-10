from fastadmin.models.base import InlineModelAdmin, ModelAdmin


class DjangoORMMixin:
    # TODO: Add support for Django ORM
    pass


class DjangoModelAdmin(DjangoORMMixin, ModelAdmin):
    pass


class DjangoInlineModelAdmin(DjangoORMMixin, InlineModelAdmin):
    pass
