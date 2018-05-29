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


class ProfileType(models.Model):
    """
    See https://github.com/mozilla/network-pulse/issues/657

    Values that should exist (handled via migration):

    - plain
    - staff
    - fellow
    - board member
    - grantee
    """
    value = models.CharField(
        max_length=50,
        unique=True
    )

    def get_default_profile_type():
        (default, _) = ProfileType.objects.get_or_create(value='plain')
        return default

    def __str__(self):
        return self.value


class ProgramType(models.Model):
    """
    See https://github.com/mozilla/network-pulse/issues/657

    These values are determined by pulse API administrators
    (tech policy fellowship, mozfest speaker, etc)
    """
    value = models.CharField(
        max_length=150,
        unique=True
    )

    def __str__(self):
        return self.value


class ProgramYear(models.Model):
    """
    See https://github.com/mozilla/network-pulse/issues/657

    You'd think this would be 4 characters, but a "year" is
    not a calendar year, so the year could just as easily
    be "summer 2017" or "Q2 2016 - Q1 2018", so this is the
    same kind of simple value model that the profile and
    program types use.
    """
    value = models.CharField(
        max_length=25,
        unique=True
    )

    def __str__(self):
        return self.value


class UserProfileQuerySet(models.query.QuerySet):
    """
    A queryset for profiles with convenience queries
    """

    def active(self):
        """
        Return all profiles that have the is_active flag set to True
        """
        return self.filter(is_active=True)


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
        max_length=140,
        blank=True
    )

    custom_name.short_description = 'Custom user name'

    # Accessing the Profile-indicated name needs various stages
    # of fallback.
    # Note that we cannot use this accessor as a lookup field in querysets
    # because it is not an actual field.
    @property
    def name(self):
        custom_name = self.custom_name

        # blank values, including pure whitespace, don't count:
        if not custom_name or not custom_name.strip():
            user = self.user
            return user.name if user else None

        # anything else does count.
        return custom_name

    # We provide an easy accessor to the profile's user because
    # accessing the reverse relation (using related_name) can throw
    # a RelatedObjectDoesNotExist exception for orphan profiles.
    # This allows us to return None instead.
    #
    # Note: we cannot use this accessor as a lookup field in querysets
    #       because it is not an actual field.
    @property
    def user(self):
        # Import EmailUser here to avoid circular import
        from pulseapi.users.models import EmailUser
        try:
            return self.related_user
        except EmailUser.DoesNotExist:
            return None

    # This flag marks whether or not this profile applies to
    # "A human being", or a group of people (be that a club, org,
    # institution, etc. etc.)
    is_group = models.BooleanField(
        default=False
    )

    is_group.short_description = 'This is a group profile.'

    # We deal with location by asking users to just write their
    # location as they would if they were search maps for it.
    location = models.CharField(
        max_length=1024,
        blank=True
    )

    location.short_description = 'User location (as would be typed in a maps search)'

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

    # --- extended information ---

    enable_extended_information = models.BooleanField(
        default=False
    )

    profile_type = models.ForeignKey(
        'profiles.ProfileType',
        null=True,
        blank=True,
        on_delete=models.SET_NULL
        # default is handled in save()
    )

    program_type = models.ForeignKey(
        'profiles.ProgramType',
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    program_year = models.ForeignKey(
        'profiles.ProgramYear',
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    # Free form affiliation information
    affiliation = models.CharField(
        max_length=200,
        blank=True
    )

    # A tweet-style user bio
    user_bio = models.CharField(
        max_length=212,
        blank=True
    )

    # A long-form user bio
    user_bio_long = models.CharField(
        max_length=4096,
        blank=True
    )

    objects = UserProfileQuerySet.as_manager()

    def save(self, *args, **kwargs):
        if self.profile_type is None:
            self.profile_type = ProfileType.get_default_profile_type()
        super(UserProfile, self).save(*args, **kwargs)

    def __str__(self):
        if self.user is None:
            return f'{self.custom_name} (no user)'

        return f'{self.name} ({self.user.email})'

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
