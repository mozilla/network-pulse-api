"""Main entry data"""

from django.db import models
from django.conf import settings
from pulseapi.tags.models import Tag
from pulseapi.issues.models import Issue
from pulseapi.creators.models import Creator
from pulseapi.users.models import EmailUser
from django.utils import timezone
from django.utils.safestring import mark_safe


# Create your models here.
class EntryQuerySet(models.query.QuerySet):
    """
    A queryset for entries which returns all entries
    """

    def public(self):
        """
        Return all entries to start
        """
        return self

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

    # optional image field with optional S3 hosting
    thumbnail = models.ImageField(
        max_length=2048,
        upload_to='images/entries',
        blank=True
    )

    # A field for getting the `<img...>` HTML for the thumbnail image
    def thumbnail_tag(self):
        image_html_code = '<img src="{media_url}{href}" style="width: 25%">'.format(media_url=settings.MEDIA_URL, href=self.thumbnail)
        return mark_safe(image_html_code)

    thumbnail_tag.short_description = 'Thumbnail image'


    # crosslink fields
    tags = models.ManyToManyField(
        Tag,
        related_name='entries',
        blank=True,
    )
    issues = models.ManyToManyField(
        Issue,
        related_name='entries',
        blank=True,
    )
    creators = models.ManyToManyField(
        Creator,
        related_name='entries',
        blank=True
    )

    # automatically managed fields
    published_by = models.ForeignKey(
        EmailUser,
        related_name='entries',
    )
    created = models.DateTimeField(
        default = timezone.now,
    )

    objects = EntryQuerySet.as_manager()

    class Meta:
        """
        Make plural not be wrong
        """
        verbose_name_plural = "entries"

    def __str__(self):
        return str(self.title)
