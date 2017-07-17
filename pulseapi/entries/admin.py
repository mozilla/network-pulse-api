from django.contrib import admin

from .models import Entry, ModerationState


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
        'creators',
        'published_by',
        'bookmark_count',
    )

    readonly_fields = (
        'id',
        'created',
        'thumbnail_image_tag',
        'bookmark_count',
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

    def bookmark_count(self, instance):
        """
        Show the total number of bookmarks for this Entry
        """
        return instance.bookmarked_by.count()


admin.site.register(ModerationState, ModerationStateAdmin)
admin.site.register(Entry, EntryAdmin)
