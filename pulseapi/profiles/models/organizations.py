import os

from django.db import models
from django.utils import timezone

from pulseapi.issues.models import Issue
from pulseapi.utility.model_fields import TemporaryField


def org_profile_thumbnail_path(instance, filename):
    return 'images/org-avatars/{timestamp}{ext}'.format(
        timestamp=str(timezone.now()),
        ext=os.path.splitext(filename)[1]
    )


class OrganizationProfileQueryset(models.query.QuerySet):
    """
    A manager for organization profiles with convenience queries
    """

    def saved(self):
        """
        Return all organization profiles that aren't temporarirly created
        """
        return self.filter(temporary_code=None)


class OrganizationProfile(models.Model):
    """
    This class houses Organization Profile data
    such as name, location, and website
    """
    name = models.CharField(
        verbose_name='Organization Name',
        max_length=300,
    )

    location = models.CharField(
        verbose_name='Headquarters Location',
        help_text='Full address of your headquarters including the city, '
                  'region (if any), and country.',
        max_length=1024,
    )

    tagline = models.TextField(
        help_text='A short (max 140 characters) one-liner about your mission',
        max_length=140,
    )

    about = models.TextField(
        help_text='Describe what type of organization you are, the kind of '
                  'work you do, what you offer, etc.',
        max_length=1024,
    )

    twitter = models.URLField(
        blank=True,
        help_text='Full url to Twitter profile',
        max_length=2048,
    )

    linkedin = models.URLField(
        blank=True,
        help_text='Full url to LinkedIn profile',
        max_length=2048,
    )

    email = models.EmailField(
        verbose_name='Organization Email',
        help_text='A contact email for your organization',
        blank=True,
    )

    website = models.URLField(
        blank=True,
        help_text='Full url to your organization\'s homepage',
        max_length=2048,
    )

    logo = models.ImageField(
        blank=True,
        max_length=2048,
        upload_to=org_profile_thumbnail_path,
    )

    administrator = models.ForeignKey(
        'profiles.UserProfile',
        null=True,
        blank=True,
        help_text='Link an existing Pulse account to manage your '
                  'organization’s profile',
        on_delete=models.SET_NULL,
    )

    issues = models.ManyToManyField(
        Issue,
        verbose_name='Internet Health Issues',
        related_name='related_organizations',
        blank=True,
    )

    temporary_code = TemporaryField()

    objects = OrganizationProfileQueryset.as_manager()

    class Meta:
        verbose_name = 'organization profile'
