from django.contrib import admin

from .models import Creator


class CreatorAdmin(admin.ModelAdmin):
    search_fields = (
        'name',
        'profile__custom_name',
        'profile__related_user__name',
    )


admin.site.register(Creator, CreatorAdmin)
