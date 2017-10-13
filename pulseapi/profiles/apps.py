from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class ProfilesConfig(AppConfig):
    name = 'pulseapi.profiles'
    verbose_name = _('user profiles')

    def ready(self):
        import pulseapi.profiles.signals  # noqa
