"""
Create fake help types for local development, tests, and Heroku's review app.
"""

from factory import DjangoModelFactory, Faker

from pulseapi.helptypes.models import HelpType


class HelpTypeFactory(DjangoModelFactory):
    name = Faker('job')

    class Meta:
        model = HelpType
