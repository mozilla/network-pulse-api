"""
Create fake creators that are not pulse users for local development and Heroku's review app.
"""

from factory import (
    DjangoModelFactory,
    Faker,
    Iterator,
)

from pulseapi.creators.models import Creator, OrderedCreatorRecord


# Create creators that are not pulse users
class CreatorFactory(DjangoModelFactory):

    class Meta:
        model = Creator

    name = Faker('name')


# Create a relation between a random creator and a random entry
class OrderedCreatorRecordFactory(DjangoModelFactory):

    class Meta:
        model = OrderedCreatorRecord

    creator = Iterator(Creator.objects.all())
