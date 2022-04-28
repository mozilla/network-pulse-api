"""
Admin setings for EmailUser app
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.utils.html import format_html


from pulseapi.entries.models import Entry
from pulseapi.users.models import EmailUser
from pulseapi.utility.get_admin_url import get_admin_url

from .admin_group_editing import GroupAdmin


class EmailUserAdmin(UserAdmin):
    """
    Show a list of entries a user has submitted in the EmailUser Admin app
    """
    fieldsets = (
        (None, {
            'fields': (
                'password',
                'last_login',
                'email',
                'name',
                'is_staff',
                'is_superuser',
                'is_active',
                'user_profile',
                'entries',
            )
        }),
    )

    readonly_fields = (
        'entries',
        'user_profile',
        'name',
    )

    list_display = ('pk', 'name', 'email', 'account_created', 'is_active', 'bio',)
    list_filter = ('is_staff', 'is_superuser', 'groups',)
    search_fields = ('name', 'email',)
    ordering = ('-pk', 'name')

    def entries(self, instance):
        entries = Entry.objects.filter(published_by=instance)
        rows = ['<tr><td><a href="{url}">{title} (id={id})</a></td></tr>'.format(
            url=get_admin_url(entry),
            id=entry.id,
            title=entry.title
        ) for entry in entries]
        return format_html('<table>{rows}</table>'.format(rows=''.join(rows)))
    entries.short_description = 'Entries posted by this user'

    def account_created(self, instance):
        try:
            return instance.profile.created_at
        except AttributeError:
            return 'Missing profile'

    def bio(self, instance):
        try:
            return instance.profile.user_bio
        except AttributeError:
            return 'Missing profile'

    def user_profile(self, instance):
        """
        Link to this user's profile
        """
        profile = instance.profile

        html = '<a href="{url}">Click here for this user\'s profile</a>'.format(
            url=get_admin_url(profile)
        )

        return format_html(html)

    user_profile.short_description = 'User profile'


admin.site.register(EmailUser, EmailUserAdmin)

# Add the admin view bits that let us add these users to groups
admin.site.unregister(Group)
admin.site.register(Group, GroupAdmin)
