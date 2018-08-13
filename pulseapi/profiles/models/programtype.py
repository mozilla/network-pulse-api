from django.db import models


class ProgramType(models.Model):
    """
    See https://github.com/mozilla/network-pulse/issues/657

    These values are determined by pulse API administrators
    (tech policy fellowship, mozfest speaker, etc)
    """
    value = models.CharField(
        max_length=150,
        unique=True
    )

    def __str__(self):
        return self.value