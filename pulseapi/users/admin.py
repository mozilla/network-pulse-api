"""
Admin setings for EmailUser app
"""
from django.contrib import admin
from django.contrib.auth.models import Group
from django.utils.html import format_html

from .models import EmailUser
from pulseapi.users.models import UserBookmarks
from pulseapi.profiles.models import UserProfile

class UserBookmarksInline(admin.TabularInline):
    """
    We need an inline widget before we can do anything
    with the user/entry bookmark data.
    """
    model = UserBookmarks
    verbose_name = 'UserBookmarks'


class EmailUserAdmin(admin.ModelAdmin):
    """
    Show a list of entries a user has submitted in the EmailUser Admin app
    """
    fields = ('password', 'last_login', 'email', 'name', 'is_staff', 'is_superuser', 'profile', 'entries','bookmarks', )
    readonly_fields = ('entries','bookmarks','profile')

    # this allows us to create/edit/delete/etc bookmarks:
    inlines = [ UserBookmarksInline ]

    def entries(self, instance):
        """
        Show all entries as a string of titles. In the future we should make them links.
        """
        return ", ".join([str(entry) for entry in instance.entries.all()])

    def profile(self, instance):
        """
        Link to this user's profile
        """
        profile = UserProfile.objects.get(user=instance)

        html = '<a href="/admin/profiles/userprofile/{id}/change/">Click here for this user\'s profile</a>'.format(
            id=profile.id,
        )

        return format_html(html)

    profile.short_description = 'User profile'


class UserBookmarksAdmin(admin.ModelAdmin):
    """
    ...
    """
    fields = ('entry', 'user',)
    readonly_fields = ('entry', 'user',)

admin.site.register(UserBookmarks, UserBookmarksAdmin)
admin.site.register(EmailUser, EmailUserAdmin)

# Add the admin view bits that let us add these users to groups
from .admin_group_editing import GroupAdmin
admin.site.unregister(Group)
admin.site.register(Group, GroupAdmin)
