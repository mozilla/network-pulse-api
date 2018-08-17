import os

from django.db import models
from django.utils import timezone

from pulseapi.issues.models import Issue


def entry_thumbnail_path(instance, filename):
    return 'images/org-avsatars/{timestamp}{ext}'.format(
        timestamp=str(timezone.now()),
        ext=os.path.splitext(filename)[1]
    )


class OrganizationProfile(models.Model):
    """
    This class houses Organization Profile data
    such as name, location, and website
    """
    name = models.TextField(
        verbose_name='Organization Name',
        blank=False,
        null=False,
        max_length = 140
    )

    location = models.TextField(
        verbose_name='Headquarters Location',
        blank=False,
        null=False,
        max_length=1024
    )

    tagline = models.TextField(
        blank=False,
        null=False,
        max_length=140
    )

    about = models.TextField(
        blank=False,
        null=False,
        max_length=1024
    )

    twitter = models.URLField(
        blank=True,
        max_length=2048
    )

    linkedin = models.URLField(
        blank=True,
        max_length=2048
    )

    email = models.EmailField(
        verbose_name='Organization Email',
        blank=True
    )

    website = models.URLField(
        blank=True
    )

    logo = models.ImageField(
        blank=True,
        max_length=2048,
        upload_to=entry_thumbnail_path
    )

    administrator = models.ForeignKey(
        'profiles.UserProfile',
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    issues = models.ManyToManyField(
        Issue,
        verbose_name='Internet Health Issues',
        related_name='entries',
        blank=True
    )