from django.db import models


class ProfileType(models.Model):
    """
    See https://github.com/mozilla/network-pulse/issues/657

    Values that should exist (handled via migration):

    - plain
    - staff
    - fellow
    - board member
    - grantee
    """
    value = models.CharField(
        max_length=50,
        unique=True
    )

    def get_default_profile_type():
        (default, _) = ProfileType.objects.get_or_create(value='plain')
        return default

    def __str__(self):
        return self.value
