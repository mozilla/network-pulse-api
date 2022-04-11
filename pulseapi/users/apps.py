from __future__ import unicode_literals

from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = 'pulseapi.users'

    def ready(self):
        # Importing this file so the signals in signals.py works.
        # The noqa is added as tests fail regarding an 'unused import' without it.
        import pulseapi.users.signals  # noqa: F401
