from django.contrib import admin

from .models import Creator, OrderedCreatorRecord


class OrderedCreatorRecordAdmin(admin.ModelAdmin):
    """
    mostly to see the id for these records
    """

    fields = (
        'id',
        'entry',
        'creator',
    )

    readonly_fields = (
        'id',
        'entry',
        'creator',
    )


admin.site.register(Creator)
admin.site.register(OrderedCreatorRecord, OrderedCreatorRecordAdmin)
