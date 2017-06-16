import factory
from faker import Factory as FakerFactory
from pulseapi.entries.models import Entry, ModerationState
from pulseapi.users.models import EmailUser


faker = FakerFactory.create()

pending = ModerationState.objects.get(name='Pending')
approved = ModerationState.objects.get(name='Approved')


class EntryFactory(factory.DjangoModelFactory):

    title = factory.LazyAttribute(
        lambda o: 'title '+' '.join(faker.words(nb=1))
    )
    description = factory.LazyAttribute(
        lambda o: 'description '+''.join(faker.sentence(nb_words=20))
    )
    content_url = 'http://example.org/image.png'
    featured = False
    published_by = factory.LazyAttribute(
        lambda o: EmailUser.objects.all()[0]
    )

    moderation_state = approved

    class Meta:
        model = Entry
