"""Main entry data"""

from django.db import models

# Create your models here.
class EntryQuerySet(models.query.QuerySet):
    """
    A queryset for entries which returns all entries
    """

    def public(self):
        return self

class Entry(models.Model):
    """
    A pulse entry
    """
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    content_url = models.URLField()
    thumbnail_url = models.URLField()
    tags = models.CharField(max_length=500)
    objects = EntryQuerySet.as_manager()

    class Meta:
        """
        Make plural not be wrong
        """
        verbose_name_plural = "entries"
