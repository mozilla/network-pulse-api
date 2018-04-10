"""
The creator field for an entry. Can be empty, just a name,
or linked to a pulse user
"""
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _


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
    name = models.CharField(
        max_length=140,
        blank=True,
        null=True,
    )
    profile = models.OneToOneField(
        'profiles.UserProfile',
        on_delete=models.CASCADE,
        related_name='related_creator',
        blank=True,
        null=True,
    )

    objects = CreatorQuerySet.as_manager()

    @property
    def creator_name(self):
        return self.profile.name if self.profile else self.name

    def clean(self):
        """
        We provide custom validation for the model to make sure that
        either a profile or a name is provided for the creator since
        a creator without either is not useful.
        """
        profile = self.profile
        name = self.name

        if profile is None and name is None:
            raise ValidationError(_('Either a profile or a name must be specified for this creator.'))

        if profile and name:
            # In case both name and profile are provided, we clear the
            # name so that the profile's name takes precedence. We do this
            # so that if a profile's name is changed, the creator reflects
            # the updated name.
            self.name = None

    def save(self, *args, **kwargs):
        """
        Django does not automatically perform model validation on save due to
        backwards compatibility. Since we have custom validation, we manually
        call the validator (which calls our clean function) on save.
        """
        self.full_clean()
        super(Creator, self).save(*args, **kwargs)

    def __str__(self):
        return '{name}{has_profile}'.format(
            name=self.creator_name,
            has_profile=' (no profile)' if not self.profile else ''
        )

    class Meta:
        verbose_name = "Creator"
        ordering = [
            'name'
        ]


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
        related_name='related_creators'
    )

    creator = models.ForeignKey(
        'creators.Creator',
        on_delete=models.CASCADE,
        related_name='related_entries',
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
