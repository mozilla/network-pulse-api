from django.contrib import admin
from django.utils.html import format_html

from pulseapi.profiles.forms import ProfileAdminForm
from pulseapi.utility.get_admin_url import get_admin_url
from .models import (
    ProfileType,
    ProgramType,
    ProgramYear,
    UserProfile,
    UserBookmarks,
)


class UserProfileAdmin(admin.ModelAdmin):
    """
    Show the profile-associated user.
    """

    form = ProfileAdminForm

    fields = (
        'created_at',
        'is_active',
        'user_account',
        'name',
        'custom_name',
        'is_group',
        'location',
        'user_bio',
        'bookmark_count',
        'thumbnail',
        'thumbnail_image_tag',
        'issues',
        'twitter',
        'linkedin',
        'github',
        'website',
        'enable_extended_information',
        'profile_type',
        'program_type',
        'program_year',
        'affiliation',
        'user_bio_long',
    )

    readonly_fields = (
        'created_at',
        'user_account',
        'name',
        'thumbnail_image_tag',
        'bookmark_count',
    )

    list_select_related = ('profile_type', 'program_year', 'program_type', 'related_user')

    list_display = (
        'name',
        'is_active',
        'profile_type',
        'program_type',
        'program_year',
        'user_account',
        'enable_extended_information',
    )

    list_filter = (
        'profile_type',
        'program_type',
        'program_year',
        'enable_extended_information',
    )

    search_fields = (
        'custom_name',
        'related_user__name',
        'related_user__email',
    )

    def name(self, instance):
        return instance.name or '-'

    name.short_description = 'Name that will show'

    def user_account(self, instance):
        user = instance.user
        html = '<a href="{url}">{account}</a>'.format(
            url=get_admin_url(user),
            account=user.email
        ) if user else 'Orphan profile'
        return format_html(html)

    def bookmark_count(self, instance):
        """
        Show the total number of bookmarks for this Entry
        """
        return instance.bookmarks_from.count()


class UserBookmarksAdmin(admin.ModelAdmin):
    """
    ...
    """
    fields = ('entry', 'profile', 'timestamp', )
    readonly_fields = ('entry', 'profile', 'timestamp', )


admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(UserBookmarks, UserBookmarksAdmin)

admin.site.register(ProfileType)
admin.site.register(ProgramType)
admin.site.register(ProgramYear)
