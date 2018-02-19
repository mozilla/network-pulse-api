from datetime import timezone

from factory import (
    DjangoModelFactory,
    Faker,
    Iterator,
    Trait,
)

from pulseapi.entries.models import Entry
from pulseapi.users.models import EmailUser


class EntryFactory(DjangoModelFactory):

    class Meta:
        model = Entry

    class Params:
        mozillauser=Trait(
            published_by=Iterator(EmailUser.objects.filter(email__icontains='mozilla'))
        )

    title = Faker('sentence', nb_words=12, variable_nb_words=True)
    content_url = Faker('url')
    created = Faker('past_datetime', start_date='-30d', tzinfo=timezone.utc)
    published_by = Iterator(EmailUser.objects.exclude(email__icontains='mozilla'))
