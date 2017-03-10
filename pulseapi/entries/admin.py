from django.contrib import admin

from .models import Entry


class EntryAdmin(admin.ModelAdmin):
    """
    Show a list of entries a user has submitted in the EmailUser Admin app
    """

    fields = (
        'title',
        'description',
        'content_url',
        'thumbnail_url',
        'thumbnail',
        'tags',
        'get_involved',
        'get_involved_url',
        'interest',
        'featured',
        'internal_notes',
        'issues',
        'creators',
        'published_by',
        'bookmark_count'
    )

    readonly_fields = ('bookmark_count',)

    def bookmark_count(self, instance):
        """
        Show the total number of bookmarks for this Entry
        """
        return instance.bookmarked_by.count()


admin.site.register(Entry, EntryAdmin)
