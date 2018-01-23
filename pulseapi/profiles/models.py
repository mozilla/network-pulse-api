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
        # We do not import EmailUser directly so that we don't end up with
        # a circular import. Instead, we dynamically get the model via its
        # relationship with `UserProfile`.
        EmailUser = self._meta.get_field('related_user').related_model

        try:
            # We have to fetch the user for this profile from the database
            # vs. accessing `self.related_user` because `related_user` is not
            # an actual field in the `UserProfile` model and we aren't dealing
            # with a full instance of the model in this function through which
            # we could have accessed reverse relations.
            related_user = EmailUser.objects.get(profile=self)
            return related_user
        except EmailUser.DoesNotExist:
            return None

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

    # --- extended information ---

    enable_extended_information = models.BooleanField(
        default=False
    )

    # currently not captured as Program class,
    # instead captured as type+year

    PROGRAM_NONE = "None"
    PROGRAM_MOZFELLOW = "Mozilla Fellow"

    PROGRAM_TYPES = (
        (PROGRAM_NONE, PROGRAM_NONE),
        (PROGRAM_MOZFELLOW, PROGRAM_MOZFELLOW),
    )

    program_type = models.CharField(
        max_length=200,
        choices=PROGRAM_TYPES,
        default=PROGRAM_NONE
    )

    PROGRAM_YEAR_NONE = "----"
    PROGRAM_YEAR_2005 = "2005"
    PROGRAM_YEAR_2006 = "2006"
    PROGRAM_YEAR_2007 = "2007"
    PROGRAM_YEAR_2008 = "2008"
    PROGRAM_YEAR_2009 = "2009"
    PROGRAM_YEAR_2010 = "2010"
    PROGRAM_YEAR_2011 = "2011"
    PROGRAM_YEAR_2012 = "2012"
    PROGRAM_YEAR_2013 = "2013"
    PROGRAM_YEAR_2014 = "2014"
    PROGRAM_YEAR_2015 = "2015"
    PROGRAM_YEAR_2016 = "2016"
    PROGRAM_YEAR_2017 = "2017"
    PROGRAM_YEAR_2018 = "2018"
    PROGRAM_YEAR_2019 = "2019"

    PROGRAM_YEARS = (
        (PROGRAM_YEAR_NONE, PROGRAM_YEAR_NONE),
        (PROGRAM_YEAR_2005, PROGRAM_YEAR_2005),
        (PROGRAM_YEAR_2006, PROGRAM_YEAR_2006),
        (PROGRAM_YEAR_2007, PROGRAM_YEAR_2007),
        (PROGRAM_YEAR_2008, PROGRAM_YEAR_2008),
        (PROGRAM_YEAR_2009, PROGRAM_YEAR_2009),
        (PROGRAM_YEAR_2010, PROGRAM_YEAR_2010),
        (PROGRAM_YEAR_2011, PROGRAM_YEAR_2011),
        (PROGRAM_YEAR_2012, PROGRAM_YEAR_2012),
        (PROGRAM_YEAR_2013, PROGRAM_YEAR_2013),
        (PROGRAM_YEAR_2014, PROGRAM_YEAR_2014),
        (PROGRAM_YEAR_2015, PROGRAM_YEAR_2015),
        (PROGRAM_YEAR_2016, PROGRAM_YEAR_2016),
        (PROGRAM_YEAR_2017, PROGRAM_YEAR_2017),
        (PROGRAM_YEAR_2018, PROGRAM_YEAR_2018),
        (PROGRAM_YEAR_2019, PROGRAM_YEAR_2019),
    )

    program_year = models.CharField(
        max_length=4,
        choices=PROGRAM_YEARS,
        default=PROGRAM_YEAR_NONE,
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
