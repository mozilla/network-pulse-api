from django.db import models


class UserBookmarks(models.Model):
    """
    This class is used to link users and entries through a
    "bookmark" relation. One user can bookmark many entries,
    and one entry can have bookmarks from many users.
    """
    entry = models.ForeignKey(
        'entries.Entry',
        on_delete=models.CASCADE,
        related_name='bookmarked_by'
    )

    profile = models.ForeignKey(
        'profiles.UserProfile',
        on_delete=models.CASCADE,
        related_name='bookmarks_from',
        null=True
    )

    timestamp = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return 'bookmark for "{e}" by [{p}]'.format(
            e=self.entry,
            p=self.profile.id
        )

    class Meta:
        verbose_name = "Bookmarks"
        verbose_name_plural = "Bookmarks"