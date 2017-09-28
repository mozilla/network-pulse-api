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

    # Make sure tags are cleaned when saving
    def save(self, *args, **kwargs):
        # We don't want to allow commas in tags, ever.
        # As such, if self.name has commas, we split it,
        # build new Tag instances for each term, and then
        # update ourselves to be the first term.
        name = self.name
        if ',' in name:
            terms = name.split(',')
            self.name = terms[0]
            for term in terms[1:]:
                Tag.objects.create(name=term)

        self.full_clean()
        super(Tag, self).save(*args, **kwargs)

    # clean tags don't have leading or trailing spaces
    def clean(self):
        self.name = self.name.strip()

    def __str__(self):
        return str(self.name)

    class Meta:
        ordering = [
            'name',
        ]
