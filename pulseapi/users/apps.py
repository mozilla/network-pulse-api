from __future__ import unicode_literals

from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = 'pulseapi.users'

    def ready(self):
        import pulseapi.users.signals
