"""Main entry data"""
import os

from django.conf import settings
from django.db import models
from pulseapi.tags.models import Tag
from pulseapi.issues.models import Issue
from pulseapi.creators.models import Creator
from pulseapi.users.models import EmailUser
from django.utils import timezone
from django.utils.html import format_html

def entry_thumbnail_path(instance, filename):
    return 'images/entries/{timestamp}{ext}'.format(
        timestamp=str(timezone.now()),
        ext=os.path.splitext(filename)[1]
    )


# Create your models here.
class EntryQuerySet(models.query.QuerySet):
    """
    A queryset for entries which returns all entries
    """

    def public(self):
        """
        Return all entries to start
        """
        return self.filter(is_approved=True)

class Entry(models.Model):
    """
    A pulse entry
    """

    # required fields
    title = models.CharField(max_length=140)
    content_url = models.URLField()

    # optional fields
    description = models.CharField(max_length=600, blank=True)
    thumbnail_url = models.URLField(blank=True)
    get_involved = models.CharField(max_length=300, blank=True)
    get_involved_url = models.URLField(blank=True)
    interest = models.CharField(max_length=600, blank=True)
    featured = models.BooleanField(default=False)
    internal_notes = models.TextField(blank=True)

    # thumbnail image
    thumbnail = models.ImageField(
        max_length=2048,
        upload_to=entry_thumbnail_path,
        blank=True
    )

    def thumbnail_image_tag(self):
        if not self.thumbnail:
            return format_html('<span>No image to preview</span>')

        media_url = settings.MEDIA_URL

        if settings.USE_S3:
            media_url = 'https://{domain}/{bucket}/'.format(
                domain=settings.AWS_S3_CUSTOM_DOMAIN,
                bucket=settings.AWS_LOCATION
            )

        return format_html('<img src="{media_url}{src}" style="width:25%">'.format(
            media_url=media_url,
            src=self.thumbnail
        ))

    thumbnail_image_tag.short_description = 'Thumbnail preview'

    # crosslink fields
    tags = models.ManyToManyField(
        Tag,
        related_name='entries',
        blank=True
    )
    issues = models.ManyToManyField(
        Issue,
        related_name='entries',
        blank=True
    )
    creators = models.ManyToManyField(
        Creator,
        related_name='entries',
        blank=True
    )

    # automatically managed fields
    published_by = models.ForeignKey(
        EmailUser,
        related_name='entries'
    )
    created = models.DateTimeField(
        default = timezone.now
    )
    is_approved = models.BooleanField(
        default=False,
        help_text="Should this show up on the site?"
    )

    objects = EntryQuerySet.as_manager()

    class Meta:
        """
        Make plural not be wrong
        """
        verbose_name_plural = "entries"

    def __str__(self):
        return str(self.title)
