"""
Tags used for categorizing entries
"""
from django.db import models

class TagQuerySet(models.query.QuerySet):
    """
    A queryset for tags which returns all tags
    """

    def public(self):
        """
        Returns all tags to start
        """
        return self

class Tag(models.Model):
    """
    Tags used to describe properties of an entry and to
    enable filtering entries by these properties
    """
    name = models.CharField(unique=True, max_length=150)
    objects = TagQuerySet.as_manager()

    def _get_entry_count(self):
        return self.entries.count()

    entry_count = property(_get_entry_count)

    def __str__(self):
        return str(self.name)

    class Meta:
        ordering = [
            'name',
        ]
