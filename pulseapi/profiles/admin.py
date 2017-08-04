from django.contrib import admin
from .models import UserProfile, UserBookmarks

class UserProfileAdmin(admin.ModelAdmin):
    """
    Show a list of entries a user has submitted in the EmailUser Admin app
    """
    fields = ('user',)
    readonly_fields = ('user',)

class UserBookmarksAdmin(admin.ModelAdmin):
	"""
	...
	"""
	fields = ('entry', 'user', 'profile',)
	readonly_fields = ('entry', 'user', 'profile',)

admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(UserBookmarks, UserBookmarksAdmin)
