"""
Create fake entries for local development and Heroku's review app.
"""

from datetime import timezone

from factory import (
    DjangoModelFactory,
    Faker,
    Iterator,
    Trait,
    post_generation,
    LazyAttribute,
)

from faker import Factory as FakerFactory

from pulseapi.entries.models import Entry, ModerationState
from pulseapi.helptypes.models import HelpType
from pulseapi.issues.models import Issue
from pulseapi.tags.models import Tag
from pulseapi.users.models import EmailUser
from pulseapi.utility.factories_utility import get_random_items, ImageProvider

Faker.add_provider(ImageProvider)

faker = FakerFactory.create()

pending = ModerationState.objects.get(name='Pending')
approved = ModerationState.objects.get(name='Approved')


class EntryFactory(DjangoModelFactory):

    title = LazyAttribute(
        lambda o: 'title ' + ' '.join(faker.words(nb=1))
    )
    description = LazyAttribute(
        lambda o: 'description ' + ''.join(faker.sentence(nb_words=20))
    )
    content_url = 'http://example.org/image.png'
    featured = False
    published_by = LazyAttribute(
        lambda o: EmailUser.objects.all()[0]
    )

    moderation_state = approved

    class Meta:
        model = Entry


class BasicEntryFactory(DjangoModelFactory):

    class Meta:
        model = Entry
        exclude = ('title_sentence',)

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

    title = LazyAttribute(lambda o: o.title_sentence.rstrip('.'))
    content_url = Faker('url')
    created = Faker('past_datetime', start_date='-30d', tzinfo=timezone.utc)
    published_by = Iterator(EmailUser.objects.exclude(email__icontains='mozilla'))
    moderation_state = Iterator(ModerationState.objects.all())
    description = Faker('paragraph', nb_sentences=6, variable_nb_sentences=True)
    internal_notes = Faker('paragraph', nb_sentences=3, variable_nb_sentences=True)

    # LazyAttribute helper value
    title_sentence = Faker('sentence', nb_words=8, variable_nb_words=True)

    @post_generation
    def tags(self, create, extracted, **kwargs):
        self.tags.add(*get_random_items(Tag))

    @post_generation
    def issues(self, create, extracted, **kwargs):
        self.issues.add(*get_random_items(Issue))

    @post_generation
    def set_thumbnail(self, create, extracted, **kwargs):
        self.thumbnail.name = Faker('generic_image').generate({})


class GetInvolvedEntryFactory(BasicEntryFactory):

    get_involved = Faker('paragraph', nb_sentences=3, variable_nb_sentences=True)
    get_involved_url = Faker('url')

    @post_generation
    def help_types(self, create, extracted, **kwargs):
        self.help_types.add(*(get_random_items(HelpType)))
