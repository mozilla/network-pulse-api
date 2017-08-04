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

    def __str__(self):
        return 'profile for {}'.format(self.user.email)


class UserBookmarks(models.Model):
    """
    This class is used to link users and entries through a
    "bookmark" relation. One user can bookmark many entries,
    and one entry can have bookmarks from many users.
    """
    entry = models.ForeignKey(
        'entries.Entry',
        on_delete=models.CASCADE,
        related_name='bookmarked_by_profile'
    )

    user = models.ForeignKey(
        'users.EmailUser',
        on_delete=models.CASCADE,
        related_name='bookmark_entries_from_user'
    )

    profile = models.ForeignKey(
        'profiles.UserProfile',
        on_delete=models.CASCADE,
        related_name='bookmark_entries_from_profile',
        null=True
    )

    timestamp = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return 'bookmark for "{e}" by {u}, with profile [{p}]'.format(
            u=self.user,
            e=self.entry,
            p=self.profile.id
        )
