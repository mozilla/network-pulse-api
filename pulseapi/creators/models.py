"""
The creator field for an entry. Can be empty, just a name,
or linked to a pulse user
"""
from django.db import models


class EntryCreator(models.Model):
    """
    A bridge model to describe a relationship between profiles
    as creators and entries.
    """
    entry = models.ForeignKey(
        'entries.Entry',
        on_delete=models.CASCADE,
        related_name='related_entry_creators',
    )

    profile = models.ForeignKey(
        'profiles.UserProfile',
        on_delete=models.CASCADE,
        related_name='related_entry_creators',
    )

    def __str__(self):
        return 'Creator {creator} for "{entry}"'.format(
            entry=self.entry.title,
            creator=self.profile.name,
        )

    class Meta:
        verbose_name = 'Entry Creators'
        # This meta option creates an _order column in the table
        # See https://docs.djangoproject.com/en/1.11/ref/models/options/#order-with-respect-to for more details
        order_with_respect_to = 'entry'
        indexes = [
            models.Index(fields=['entry', '_order'], name='uk_entrycreator_entryid_order'),
            models.Index(fields=['entry', 'profile'], name='uk_entrycreator_entry_profile')
        ]
        unique_together = ('entry', 'profile',)
