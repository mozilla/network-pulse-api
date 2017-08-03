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
