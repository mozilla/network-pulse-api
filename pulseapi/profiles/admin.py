from django.contrib import admin
from .models import UserProfile, UserBookmarks


class UserProfileAdmin(admin.ModelAdmin):
    """
    Show the profile-associated user.
    """

    fields = (
    	'user',
    	'name',
    	'location',
    	'is_group',
    	'user_blurp',
    	'user_bio',
		'bookmark_count',
        'thumbnail',
        'thumbnail_image_tag',
        'social_urls',
        'issues',
    )

    readonly_fields = (
    	'user',
    	'name',
        'thumbnail_image_tag',
        'bookmark_count',
    )

    def bookmark_count(self, instance):
        """
        Show the total number of bookmarks for this Entry
        """
        return instance.bookmarked_by.count()



class UserBookmarksAdmin(admin.ModelAdmin):
    """
    ...
    """
    fields = ('entry', 'profile', 'timestamp')
    readonly_fields = ('entry', 'profile', 'timestamp')


admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(UserBookmarks, UserBookmarksAdmin)
