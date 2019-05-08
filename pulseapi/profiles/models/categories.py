from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from pulseapi.utility.validators import YearValidator


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


class CohortRecord(models.Model):
    profile = models.ForeignKey(
        'profiles.UserProfile',
        on_delete=models.CASCADE,
        related_name='cohort_records',
    )

    program = models.ForeignKey(
        'profiles.ProgramType',
        on_delete=models.PROTECT,
        related_name='profile_cohort_records',
    )

    year = models.PositiveSmallIntegerField(
        # TODO: Change to MaxValueValidator with callable when
        #       we update to Django > v2.2
        validators=[YearValidator(max_offset=2)],
        null=True,
        blank=True,
    )

    cohort_name = models.CharField(
        null=True,
        blank=True,
        max_length=200,
    )

    def __str__(self):
        return f'{self.profile.name} - {self.program} {self.year} {self.cohort_name}'

    def clean(self):
        # Don't allow both the cohort and year to be empty
        if self.year is None and not self.cohort_name:
            raise ValidationError(
                _('Either the year or cohort must have a value')
            )

    class Meta:
        verbose_name = 'cohort record'
        # This meta option creates an _order column in the table
        # See https://docs.djangoproject.com/en/1.11/ref/models/options/#order-with-respect-to for more details
        order_with_respect_to = 'profile'
        indexes = [
            models.Index(fields=['profile', '_order'], name='uk_membership_profile_order'),
        ]


class ProfileRole(models.Model):
    profile = models.ForeignKey(
        'profiles.UserProfile',
        on_delete=models.CASCADE,
        related_name='related_types',
    )

    profile_type = models.ForeignKey(
        'profiles.ProfileType',
        on_delete=models.CASCADE,
        related_name='related_profiles',
    )

    is_current = models.BooleanField(default=True)

    def __str__(self):
        is_was = 'is' if self.is_current else 'was'
        return f'{self.profile.name} {is_was} a {self.role}'

    class Meta:
        # This meta option creates an _order column in the table
        # See https://docs.djangoproject.com/en/1.11/ref/models/options/#order-with-respect-to for more details
        order_with_respect_to = 'profile'
        indexes = [
            models.Index(fields=['profile', 'is_current', '_order'], name='uk_role_profile_current_order'),
            models.Index(fields=['profile', 'is_current', 'profile_type'], name='uk_role_profile_current_type'),
        ]
