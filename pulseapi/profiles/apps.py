from django.apps import AppConfig
from django.utils.translation import ugettext_lazy


class ProfilesConfig(AppConfig):
    name = 'pulseapi.profiles'
    verbose_name = ugettext_lazy('user profiles')

    def ready(self):
        import pulseapi.profiles.signals  # noqa
