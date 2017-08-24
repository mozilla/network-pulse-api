"""
The creator field for an entry. Can be empty, just a name,
or linked to a pulse user
"""
from django.db import models
from pulseapi.users.models import EmailUser


class CreatorQuerySet(models.query.QuerySet):
    """
    A queryset for creators which returns all creators by name
    """

    def public(self):
        """
        Returns all creators. Mainly a starting point for the search
        query for use with suggestions
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


class OrderedCreatorRecord(models.Model):
    """
    This model records creators for entries,
    with an explicit ordering field so that
    we can reconstruct the order in which
    the list of creators was submitted.
    """
    entry = models.ForeignKey(
        'entries.Entry',
        on_delete=models.CASCADE,
        related_name='created_by'
    )

    creator = models.ForeignKey(
        'creators.Creator',
        on_delete=models.CASCADE,
        related_name='entries_by',
        null=True
    )

    # Rather than an "order" field, we rely on
    # the auto-generated `id` field, which is
    # an auto-incrementing value that does not
    # indicate when an entry was created, but does
    # indicate the temporal order in which records
    # were added into the database, allowing us
    # to sort the list based on insertion-ordering.

    def __str__(self):
        return 'ordered creator for "{entry}" by [{creator}:{order}]'.format(
            entry=self.entry,
            creator=self.creator,
            order=self.id
        )

    class Meta:
        verbose_name = "Ordered creator record"

        # Ensure that these records are always ordred based on
        # row ordering in the database.
        ordering = [
            'pk',
        ]
