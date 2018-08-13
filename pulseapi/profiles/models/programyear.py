from django.db import models


class ProgramYear(models.Model):
    """
    See https://github.com/mozilla/network-pulse/issues/657

    You'd think this would be 4 characters, but a "year" is
    not a calendar year, so the year could just as easily
    be "summer 2017" or "Q2 2016 - Q1 2018", so this is the
    same kind of simple value model that the profile and
    program types use.
    """
    value = models.CharField(
        max_length=25,
        unique=True
    )

    def __str__(self):
        return self.value