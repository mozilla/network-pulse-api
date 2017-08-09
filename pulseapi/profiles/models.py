from django.db import models

class UserProfile(models.Model):
    """
    This class houses all user profile information,
    such as real name, social media information,
    bookmarks on the site, etc.
    """

    user = models.ForeignKey(
        'users.EmailUser',
        on_delete=models.SET_NULL,
        related_name='profile',
        null=True
    )

    # "user X bookmarked entry Y" is a many to many relation,
    # for which we also want to know *when* a user bookmarked
    # a specific entry. As such, we use a helper class that
    # tracks this relation as well as the time it's created.
    bookmarks = models.ManyToManyField(
        'entries.Entry',
        through='profiles.UserBookmarks'
    )

    def __str__(self):
        return 'profile for {}'.format(self.user.email)
   
    class Meta:
        verbose_name = "Profile"


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
