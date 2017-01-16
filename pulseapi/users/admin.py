"""
Admin setings for EmailUser app
"""
from django.contrib import admin
from .models import EmailUser


class UserBookmarksInline(admin.TabularInline):
    """
    We need an inline widget before we can do anything
    with the user/entry bookmark data.
    """
    model = EmailUser.bookmarks.through
    verbose_name = 'UserBookmarks'


class EmailUserAdmin(admin.ModelAdmin):
    """
    Show a list of entries a user has submitted in the EmailUser Admin app
    """
    fields = ('password', 'last_login', 'email', 'name', 'entries','bookmarks')
    readonly_fields = ('entries','bookmarks')

    # this allows us to create/edit/delete/etc bookmarks:
    inlines = [ UserBookmarksInline ]

    def entries(self, instance):
        """
        Show all entries as a string of titles. In the future we should make them links.
        """
        return ", ".join([str(entry) for entry in instance.entries.all()])


admin.site.register(EmailUser, EmailUserAdmin)
