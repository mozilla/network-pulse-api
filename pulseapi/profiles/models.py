from django.db import models
from django.utils.html import format_html


def entry_thumbnail_path(instance, filename):
    return 'images/user-avatars/{timestamp}{ext}'.format(
        timestamp=str(timezone.now()),
        ext=os.path.splitext(filename)[1]
    )


class Location(models.Model):
    """
    THIS COMES WITH ASSUMPTION-PROBLEMS:
    - A country might have two or more cities with the same name, but
      in different administative regions of that country.
    - Some cities lie in to countries. I know, that's crazy, but some do.

    Making this do the right thing is going to take more work than any
    initial model implementation can achieve.
    """
    city = models.CharField(max_length=500, blank=False, null=True)
    country  = models.CharField(max_length=500, blank=False, null=True)

    def __str__(self):
        return '{city}, {country}'.format(
            city=self.city,
            country=self.country
        )

class SocialUrl(models.Model):
    url = models.URLField()

    service = models.CharField(
        max_length=500,
        blank=False,
        null=True
    )

    def get_service_name(self):
        """
        This function can "guess" at what the service name for this
        URL is based on the domain found in the url. This lets us
        say things like "this is twitter" or "this is facebook" or
        "a blog", or it might be prespecified by the user, or we
        will be unable to guess, in which case the result is False
        """
        if self.service is not None:
            return self.service

        # ... we would guess at the service here based on the URL...

        return False

    def __str__(self):
        service = self.get_service_name()

        if service is False:
            return self.url

        return '{url} ({service})'.format(
            url=self.url,
            service=service
        )

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

    # A tweet-style user bio
    user_blurp = models.CharField(
        max_length=140,
        blank=True,
        default=''
    )

    # A longer user bio that can be exposed when clicking through
    # to a user's profile because you care to know what they're about.
    user_bio = models.CharField(
        max_length=1000,
        blank=True,
        default=''
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
    alternative_name = models.CharField(
        max_length=500,
        blank=False,
        null=True
    )

    # Accessing the Profile-indicated name needs various stages
    # of fallback.
    def name(self):
        if self.alternative_name is not None:
            return self.alternative_name
        if self.user is not None:
            return self.user.name
        return ''

    name.short_description = 'name'


    # This flag marks whether or not this profile applies to
    # "A human being", or a group of people (be that a club, org,
    # institution, etc. etc.)
    is_group = models.BooleanField(
        default=False
    )

    # We want to capture the user or group's location, but we don't
    # want to do so in too fine a detail, so right now we mostly
    # care about city, and country that city is in.
    location = models.ManyToManyField(
        Location,
        related_name="Profile"
    )

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

    # A UserProfile can have any number of associated social urls
    social_urls = models.ManyToManyField(
        SocialUrl,
        related_name='Profile'
    )

    # Which issues does this user care about/are they involved in?
    issues = models.ManyToManyField('issues.Issue')

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
