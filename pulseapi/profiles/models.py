import os

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.html import format_html


def entry_thumbnail_path(instance, filename):
    return 'images/user-avatars/{timestamp}{ext}'.format(
        timestamp=str(timezone.now()),
        ext=os.path.splitext(filename)[1]
    )


# We want to capture the user or group's location, but we don't
# want to do so in too fine a detail, so right now we mostly
# care about city, and country that city is in.
#
class Location(models.Model):
    """
    THIS COMES WITH ASSUMPTION-PROBLEMS:

    - A country might have two or more cities with the same name, but
      in different administative regions of that country.

    - Some cities lie in to countries. I know, that's crazy, but some do.

    - Some people live or work or associate with more than one location,
      especially if they live near an easily crossed border such as in
      many European countries.

    Making this do the right thing is going to take more work than any
    initial model implementation can achieve.
    """
    city = models.CharField(
        max_length=500,
        blank=True
    )

    country = models.CharField(
        max_length=500,
        blank=True
    )

    # Note: in a simplistic world this would be a OneToOneField, but
    # we do not live in a simplistic world, so one profile can in fact
    # have multiple locations associated with it.
    profile = models.ForeignKey(
        'profiles.UserProfile',
        blank=True,
        null=True
    )

    def __str__(self):
        return '{city}, {country}'.format(
            city=self.city,
            country=self.country
        )


class UserProfile(models.Model):
    """
    This class houses all user profile information,
    such as real name, social media information,
    bookmarks on the site, etc.
    """

    # This flag determines whether this profile has been
    # activated, meaning it can be retrieved through REST
    # API calls and might get crosslinked into data structures
    # that rely on knowing a user or group's profile.
    is_active = models.BooleanField(
        default=False
    )

    # Note that orphaned profiles, without an associated
    # user account, are perfectly fine in our architecture.
    user = models.OneToOneField(
        'users.EmailUser',
        on_delete=models.CASCADE,
        related_name='profile',
        null=True
    )

    # A tweet-style user bio
    user_bio = models.CharField(
        max_length=140,
        blank=True
    )

    # "user X bookmarked entry Y" is a many to many relation,
    # for which we also want to know *when* a user bookmarked
    # a specific entry. As such, we use a helper class that
    # tracks this relation as well as the time it's created.
    bookmarks = models.ManyToManyField(
        'entries.Entry',
        through='profiles.UserBookmarks'
    )

    # The name field is an alternative name to be used if the
    # associated user(s) don't want to expose their login-indicated
    # name instead.
    #
    # Examples of this are nicknames, pseudonyms, and org names
    custom_name = models.CharField(
        max_length=70,
        blank=True
    )

    custom_name.short_description = 'Custom user name'

    # Accessing the Profile-indicated name needs various stages
    # of fallback.
    def name(self):
        # blank values, including pure whitespace, don't count:
        if not self.custom_name:
            return self.user.name
        if not self.custom_name.strip():
            return self.user.name

        # anything else does count.
        return self.custom_name

    name.short_description = 'Name that will show'

    # This flag marks whether or not this profile applies to
    # "A human being", or a group of people (be that a club, org,
    # institution, etc. etc.)
    is_group = models.BooleanField(
        default=False
    )

    is_group.short_description = 'This is a group profile.'

    # Thumbnail image for this user; their "avatar" even though we
    # do not have anything on the site right now where avatars
    # come into play.
    thumbnail = models.ImageField(
        max_length=2048,
        upload_to=entry_thumbnail_path,
        blank=True
    )

    def thumbnail_image_tag(self):
        if not self.thumbnail:
            return format_html('<span>No image to preview</span>')

        media_url = settings.MEDIA_URL

        if settings.USE_S3:
            media_url = 'https://{domain}/{bucket}/'.format(
                domain=settings.AWS_S3_CUSTOM_DOMAIN,
                bucket=settings.AWS_LOCATION
            )

        html = '<img src="{media_url}{src}" style="width:25%">'.format(
            media_url=media_url,
            src=self.thumbnail
        )

        return format_html(html)

    thumbnail_image_tag.short_description = 'Thumbnail preview'

    # Which issues does this user care about/are they involved in?
    issues = models.ManyToManyField(
        'issues.Issue',
        blank=True,
    )

    # we allow users to indicate several possible predefined service URLs
    twitter = models.URLField(
        max_length=2048,
        blank=True
    )

    linkedin = models.URLField(
        max_length=2048,
        blank=True
    )

    github = models.URLField(
        max_length=2048,
        blank=True
    )

    website = models.URLField(
        max_length=2048,
        blank=True
    )

    def __str__(self):
        if self.user is None:
            return 'orphan profile'

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
