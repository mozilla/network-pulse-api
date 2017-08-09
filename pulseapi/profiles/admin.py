from django.contrib import admin
from .models import UserProfile, UserBookmarks

class UserProfileAdmin(admin.ModelAdmin):
    """
    Show the profile-associated user.
    """
    fields = ('user',)
    readonly_fields = ('user',)

class UserBookmarksAdmin(admin.ModelAdmin):
	"""
	...
	"""
	fields = ('entry', 'profile', 'timestamp')
	readonly_fields = ('entry', 'profile', 'timestamp')

admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(UserBookmarks, UserBookmarksAdmin)
