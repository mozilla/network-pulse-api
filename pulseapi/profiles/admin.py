from django.contrib import admin
from django.utils.html import format_html
from pulseapi.utility.get_admin_url import get_admin_url
from .models import Location, UserProfile, UserBookmarks


class LocationInline(admin.TabularInline):
    model = Location
    verbose_name = 'location'


class UserProfileAdmin(admin.ModelAdmin):
    """
    Show the profile-associated user.
    """

    inlines = [
        LocationInline,
    ]

    fields = (
        'is_active',
        'user_account',
        'name',
        'custom_name',
        'is_group',
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
        'program_type',
        'program_year',
        'affiliation',
        'user_bio_long',
    )

    readonly_fields = (
        'user_account',
        'name',
        'thumbnail_image_tag',
        'bookmark_count',
    )

    def name(self, instance):
        return instance.name or '-'

    name.short_description = 'Name that will show'

    def user_account(self, instance):
        user = instance.user
        html = '<a href="{url}">{account}</a>'.format(
            url=get_admin_url(user),
            account=user.email if user else None
        )
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
