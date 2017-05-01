from django.contrib import admin

from .models import Entry


class EntryAdmin(admin.ModelAdmin):
    """
    Show a list of entries a user has submitted in the EmailUser Admin app
    """

    fields = (
        'id',
        'is_approved',
        'title',
        'description',
        'content_url',
        'thumbnail_url',
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
        'thumbnail_url',
        'thumbnail_image_tag',
        'bookmark_count',
    )

    def bookmark_count(self, instance):
        """
        Show the total number of bookmarks for this Entry
        """
        return instance.bookmarked_by.count()


admin.site.register(Entry, EntryAdmin)
