from django.contrib import admin

from pulseapi.entries.models import Entry
from .models import Tag


class EntryInline(admin.TabularInline):
    """
    We need an inline widget before we can do anything
    with the tag/entry relationship data.
    """
    model = Entry.tags.through
    verbose_name = 'Tagged entry'


class TagAdmin(admin.ModelAdmin):
    inlines = [EntryInline]

    fields = (
        'name',
        'entry_count',
    )

    readonly_fields = (
        'entry_count',
    )

    list_display = (
        'name',
        'entry_count',
    )


admin.site.register(Tag, TagAdmin)
