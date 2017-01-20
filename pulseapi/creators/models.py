"""
The creator field for an entry. Can be empty, just a name, or linked to a pulse user
"""
from django.db import models
from pulseapi.users.models import EmailUser

class CreatorQuerySet(models.query.QuerySet):
    """
    A queryset for creators which returns all creators by name
    """

    def public(self):
        """
        Returns all creators. Mainly a starting point for the search query for use with suggestions
        """
        return self

    def slug(self, slug):
        return self.filter(name=slug)

class Creator(models.Model):
    """
    Person recognized as the creator of the thing an entry links out to.
    """
    name = models.CharField(max_length=140)
    user = models.ForeignKey(
        EmailUser,
        related_name='as_creator',
        blank=True,
        null=True,
    )
    objects = CreatorQuerySet.as_manager()

    def __str__(self):
        return str(self.name)
