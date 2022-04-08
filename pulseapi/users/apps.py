from __future__ import unicode_literals

from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = 'pulseapi.users'

    def ready(self):
        # Importing this file so the post_delete signal in signals.py works.
        # The noqa is added as without it, tests fail regarding a 'unused import'.
        import pulseapi.users.signals  # noqa: F401
