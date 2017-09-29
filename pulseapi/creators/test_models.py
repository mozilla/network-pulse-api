import factory
from faker import Factory as FakerFactory
from pulseapi.creators.models import Creator


faker = FakerFactory.create()


class CreatorFactory(factory.DjangoModelFactory):

    name = factory.LazyAttribute(lambda o: faker.name())

    class Meta:
        model = Creator
