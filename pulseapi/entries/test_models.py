import factory
from faker import Factory as FakerFactory

from pulseapi.entries.models import Entry
from pulseapi.users.test_models import EmailUserFactory


faker = FakerFactory.create()


class EntryFactory(factory.DjangoModelFactory):

    title = factory.LazyAttribute(lambda o: 'title '+' '.join(faker.words(nb=1)))
    description = factory.LazyAttribute(lambda o: 'description '+''.join(faker.sentence(nb_words=20)))
    content_url = 'http://example.org/image.png'
    featured = False
    published_by_id = 1

    class Meta:
        model = Entry
