from datetime import timezone

from factory import (
    DjangoModelFactory,
    Faker,
    LazyAttribute,
    SubFactory,
)

from pulseapi.entries.models import Entry
from pulseapi.users.factory import EmailUserFactory


class EntryFactory(DjangoModelFactory):

    class Meta:
        model = Entry

    title = Faker('sentence', nb_words=12, variable_nb_words=True)
    content_url = Faker('url')
    created = Faker('past_datetime', start_date='-30d', tzinfo=timezone.utc)
    published_by = SubFactory(EmailUserFactory)
