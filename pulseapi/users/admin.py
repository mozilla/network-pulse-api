from django.contrib import admin

from pulseapi.entries.models import Entry
from .models import EmailUser

class EntryInline(admin.StackedInline):
    model = Entry

class EmailUserAdmin(admin.ModelAdmin):
    fields = ('password', 'last_login', 'email', 'name', 'entries')
    readonly_fields = ('entries',)
    def entries(self, instance):
        return ", ".join([str(entry) for entry in instance.entries.all()])

admin.site.register(EmailUser, EmailUserAdmin)
