"""Main entry data"""

from django.db import models
from pulseapi.tags.models import Tag
from pulseapi.issues.models import Issue

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
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    content_url = models.URLField()
    thumbnail_url = models.URLField()
    tags = models.ManyToManyField(
        Tag,
        related_name='entries',
        blank=True,
    )
    get_involved = models.CharField(max_length=300)
    get_involved_url = models.URLField()
    interest = models.CharField(max_length=300)
    featured = models.BooleanField()
    objects = EntryQuerySet.as_manager()
    issues = models.ManyToManyField(
        Issue,
        related_name='entries',
        blank=True,
    )

    class Meta:
        """
        Make plural not be wrong
        """
        verbose_name_plural = "entries"
        
    def __str__(self):
        return str(self.title)
