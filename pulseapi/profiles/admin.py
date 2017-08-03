from django.contrib import admin
from .models import UserProfile

class UserProfileAdmin(admin.ModelAdmin):
    """
    Show a list of entries a user has submitted in the EmailUser Admin app
    """
    fields = ('user',)
    readonly_fields = ('user',)


admin.site.register(UserProfile, UserProfileAdmin)
