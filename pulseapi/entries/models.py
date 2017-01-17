"""Main entry data"""

from django.db import models
from pulseapi.tags.models import Tag
from pulseapi.issues.models import Issue
from pulseapi.creators.models import Creator
from pulseapi.users.models import EmailUser

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
    title = models.CharField(max_length=140)
    description = models.CharField(max_length=300, blank=True)
    content_url = models.URLField(blank=True)
    thumbnail_url = models.URLField(blank=True)
    tags = models.ManyToManyField(
        Tag,
        related_name='entries',
        blank=True,
    )
    get_involved = models.CharField(max_length=300, blank=True)
    get_involved_url = models.URLField(blank=True)
    interest = models.CharField(max_length=300, blank=True)
    featured = models.BooleanField()
    internal_notes = models.TextField(blank=True)
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
    published_by = models.ForeignKey(
        EmailUser,
        related_name='entries',
    )

    objects = EntryQuerySet.as_manager()

    class Meta:
        """
        Make plural not be wrong
        """
        verbose_name_plural = "entries"

    def __str__(self):
        return str(self.title)
