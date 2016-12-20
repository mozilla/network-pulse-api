"""
Admin setings for EmailUser app
"""
from django.contrib import admin

from .models import EmailUser

class EmailUserAdmin(admin.ModelAdmin):
    """
    Show a list of entries a user has submitted in the EmailUser Admin app
    """
    fields = ('password', 'last_login', 'email', 'name', 'entries')
    readonly_fields = ('entries',)
    def entries(self, instance):
        """
        Show all entries as a string of titles. In the future we should make them links.
        """
        return ", ".join([str(entry) for entry in instance.entries.all()])

admin.site.register(EmailUser, EmailUserAdmin)
