from django.contrib import admin

from .models import Entry, ModerationState
from pulseapi.entries.forms import EntryAdminForm
from pulseapi.utility.autocomplete import autoselect_fields_check_can_add


class ModerationStateAdmin(admin.ModelAdmin):
    """
    Show a list of moderation states available for entry moderation
    """

    fields = (
        'name',
    )

    ordering = (
        'id',
    )


class EntryAdmin(admin.ModelAdmin):
    """
    Show a list of entries a user has submitted in the EmailUser Admin app
    """
    form = EntryAdminForm

    fields = (
        'id',
        'created',
        'moderation_state',
        'title',
        'description',
        'content_url',
        'thumbnail',
        'thumbnail_image_tag',
        'tags',
        'get_involved',
        'get_involved_url',
        'interest',
        'featured',
        'internal_notes',
        'issues',
        'help_types',
        'published_by',
        'creators',
        'bookmark_count',
    )

    readonly_fields = (
        'id',
        'created',
        'thumbnail_image_tag',
    )

    ordering = (
        '-created',
    )

    list_display = (
        'id',
        'title',
        'created',
        'published_by',
        'moderation_state',
    )

    # this allows us to filter on moderation state in the admin
    list_filter = (
        'moderation_state',
        'featured'
    )

    search_fields = (
        'title',
        'tags__name',
    )

    def get_form(self, request, *args, **kwargs):
        form = super().get_form(request, *args, **kwargs)
        autoselect_fields_check_can_add(form, self.model, request.user)
        form.current_user = request.user
        return form


admin.site.register(ModerationState, ModerationStateAdmin)
admin.site.register(Entry, EntryAdmin)
