"""
Create fake creators that are not pulse users for local development and Heroku's review app.
"""

from factory import DjangoModelFactory, Faker

from pulseapi.creators.models import Creator


class CreatorFactory(DjangoModelFactory):

    class Meta:
        model = Creator

    name = Faker('name')

# TODO make sure that creators have entries link to them
