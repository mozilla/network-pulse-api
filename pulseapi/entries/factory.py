from datetime import timezone

from factory import (
    DjangoModelFactory,
    Faker,
    Iterator,
    Trait,
    SubFactory)

from pulseapi.entries.models import Entry, ModerationState
from pulseapi.users.models import EmailUser


moderation = [
    'Approved',
    'Pending',
    'In Review',
    'Declined',
]


class ModerationFactory(DjangoModelFactory):

    class Meta:
        model = ModerationState
        django_get_or_create = ('name',)

    name = Faker('word', ext_word_list=moderation)


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
    moderation_state = SubFactory(ModerationFactory)
    description = Faker('paragraph', nb_sentences=6, variable_nb_sentences=True)
    internal_notes = Faker('paragraph', nb_sentences=3, variable_nb_sentences=True)

    # TODO tags and issues (many to many relation)


class GetInvolvedEntryFactory(BaseEntryFactory):

    get_involved = Faker('paragraph', nb_sentences=3, variable_nb_sentences=True)
    get_involved_url = Faker('url')

    # TODO help_types
