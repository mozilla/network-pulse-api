from django.contrib import admin

from pulseapi.tags.models import Tag
from pulseapi.tags.forms import TagAdminForm


class TagAdmin(admin.ModelAdmin):
    form = TagAdminForm

    fields = (
        'name',
        'entry_count',
        'entries',
    )

    readonly_fields = (
        'entry_count',
    )

    list_display = (
        'name',
        'entry_count',
    )

    search_fields = (
        'name',
    )

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        form.instance.entries.clear()
        form.instance.entries.add(*form.cleaned_data['entries'])


admin.site.register(Tag, TagAdmin)
