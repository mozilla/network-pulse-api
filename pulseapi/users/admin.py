"""
Admin setings for EmailUser app
"""
from django.contrib import admin
from django.contrib.auth.models import Group
from django.utils.html import format_html

from pulseapi.profiles.models import UserProfile

from .models import EmailUser
from .admin_group_editing import GroupAdmin


class EmailUserAdmin(admin.ModelAdmin):
    """
    Show a list of entries a user has submitted in the EmailUser Admin app
    """
    fields = (
        'password',
        'last_login',
        'email',
        'name',
        'is_staff',
        'is_superuser',
        'profile',
        'entries',
        'bookmarks',
    )

    readonly_fields = (
        'entries',
        'bookmarks',
        'profile',
    )

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

    def bookmarks(self, instance):
        """
        Show all bookmarked entries as a string of titles. In the future we should make them links.
        """
        profile = UserProfile.objects.get(user=instance)
        return ", ".join([str(bookmark.entry) for bookmark in profile.bookmarks])

    profile.short_description = 'User profile'


admin.site.register(EmailUser, EmailUserAdmin)

# Add the admin view bits that let us add these users to groups
admin.site.unregister(Group)
admin.site.register(Group, GroupAdmin)
