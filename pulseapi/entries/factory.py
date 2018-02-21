"""
Create fake entries for local development and Heroku's review app.
"""

from datetime import timezone
from random import randrange, choices

from factory import (
    DjangoModelFactory,
    Faker,
    Iterator,
    Trait,
    post_generation
)

from pulseapi.entries.models import Entry, ModerationState
from pulseapi.helptypes.models import HelpType
from pulseapi.issues.models import Issue
from pulseapi.tags.models import Tag
from pulseapi.users.models import EmailUser


def get_random_items(model):
    items = model.objects.all()
    return choices(items, k=randrange(len(items)))


class BaseEntryFactory(DjangoModelFactory):

    class Meta:
        model = Entry

    class Params:
        mozillauser = Trait(
            published_by=Iterator(EmailUser.objects.filter(email__icontains='mozilla'))
        )
        is_featured = Trait(
            featured=True
        )
        is_published_by_creator = Trait(
            published_by_creator=True
        )

    title = Faker('sentence', nb_words=12, variable_nb_words=True)
    content_url = Faker('url')
    created = Faker('past_datetime', start_date='-30d', tzinfo=timezone.utc)
    published_by = Iterator(EmailUser.objects.exclude(email__icontains='mozilla'))
    moderation_state = Iterator(ModerationState.objects.all())
    description = Faker('paragraph', nb_sentences=6, variable_nb_sentences=True)
    internal_notes = Faker('paragraph', nb_sentences=3, variable_nb_sentences=True)

    @post_generation
    def tags(self, create, extracted, **kwargs):
        self.tags.add(*(get_random_items(Tag)))

    @post_generation
    def issues(self, create, extracted, **kwargs):
        self.issues.add(*(get_random_items(Issue)))


class GetInvolvedEntryFactory(BaseEntryFactory):

    get_involved = Faker('paragraph', nb_sentences=3, variable_nb_sentences=True)
    get_involved_url = Faker('url')

    @post_generation
    def help_types(self, create, extracted, **kwargs):
        self.help_types.add(*(get_random_items(HelpType)))
