"""Main entry data"""
import os

from django.conf import settings
from django.db import models
from pulseapi.tags.models import Tag
from pulseapi.issues.models import Issue
from pulseapi.helptypes.models import HelpType
from pulseapi.users.models import EmailUser
from django.utils import timezone
from django.utils.html import format_html

if settings.CACHE_ENABLED:
    from cacheback.jobs import QuerySetFilterJob, QuerySetGetJob
    cache_lifetime = settings.CACHE_LIFETIME 

def cache_queryset_filter(model, **kwargs):
    if settings.CACHE_ENABLED:
        print("asdf")
        return QuerySetFilterJob(model, lifetime=cache_lifetime).get(**kwargs)
    else: 
        return model.get(**kwargs)


def cache_queryset_get(model, **kwargs):
    if settings.CACHE_ENABLED:
        return QuerySetGetJob(model, lifetime=cache_lifetime).get(**kwargs)
    else: 
        return model.filter(**kwargs)



def entry_thumbnail_path(instance, filename):
    return 'images/entries/{timestamp}{ext}'.format(
        timestamp=str(timezone.now()),
        ext=os.path.splitext(filename)[1]
    )


# Create your models here.
class ModerationState(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return str(self.name)


def get_default_moderation_state():
    """
    Helper function to ensure there is a default
    ModerationState that can be tacked onto Entries.
    """

    states = ModerationState.objects.all()
    if (len(states) == 0):
        return -1

    default_state = states[0].id
    return default_state


class EntryQuerySet(models.query.QuerySet):
    """
    A queryset for entries which returns all entries
    """

    def public(self):
        """
        Return all entries to start
        """
        try:
            # This has to happen in a try/catch, so that migrations
            # don't break. Presumably this is due to the fact that
            # during migrations, Entry can exist prior to ModerationState
            # and so if its query set is checked, it'll crash out due
            # to the absence of the associated ModerationState table.
            approved = cache_queryset_get(ModerationState, name='Approved')
            return cache_queryset_filter(Entry, moderation_state=approved)
        except Exception as e:
            print(e)
            print("could not make use of ModerationState!")
            return self.all()


class Entry(models.Model):
    """
    A pulse entry
    """

    # required fields
    title = models.CharField(max_length=140)
    content_url = models.URLField()

    # optional fields
    description = models.CharField(max_length=600, blank=True)
    get_involved = models.CharField(max_length=300, blank=True)
    get_involved_url = models.URLField(blank=True)
    interest = models.CharField(max_length=600, blank=True)
    featured = models.BooleanField(default=False)
    internal_notes = models.TextField(blank=True)
    published_by_creator = models.BooleanField(default=False)

    # thumbnail image
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

    # crosslink fields
    tags = models.ManyToManyField(
        Tag,
        related_name='entries',
        blank=True
    )
    issues = models.ManyToManyField(
        Issue,
        related_name='entries',
        blank=True
    )
    help_types = models.ManyToManyField(
        HelpType,
        related_name='entries',
        blank=True
    )

    # automatically managed fields
    published_by = models.ForeignKey(
        EmailUser,
        related_name='entries'
    )
    created = models.DateTimeField(
        default=timezone.now
    )

    # moderation information
    moderation_state = models.ForeignKey(
        ModerationState,
        related_name='entries',
        default=get_default_moderation_state,
        on_delete=models.PROTECT
    )

    def set_moderation_state(self, state_name):
        (moderation_state, created) = ModerationState.objects.get_or_create(
            name=state_name
        )
        self.moderation_state = moderation_state

    def is_approved(self):
        return self.moderation_state.name == 'Approved'

    objects = EntryQuerySet.as_manager()

    class Meta:
        """
        Make plural not be wrong
        """
        verbose_name_plural = "entries"

    def __str__(self):
        return str(self.title)
