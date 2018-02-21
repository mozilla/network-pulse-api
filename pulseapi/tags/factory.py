"""
Create fake tags for local development and Heroku's review app.
"""

from factory import DjangoModelFactory, Faker

from pulseapi.tags.models import Tag


class TagFactory(DjangoModelFactory):

    class Meta:
        model = Tag

    name = Faker('word')
